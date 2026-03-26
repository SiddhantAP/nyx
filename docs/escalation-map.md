# Escalation Map — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## Overview

Nyx never jumps straight to an alert. Every escalation step is deliberate, graduated, and designed to give the student the opportunity to self-resolve before anyone else is involved. The contact only sees what they need to see, when they need to see it.

---

## Principals

| Principal | Role |
|---|---|
| **Student** | The person walking home. Controls the session entirely. |
| **Primary contact** | First trusted contact. Receives walk-start notification and escalation alerts. |
| **Secondary contact** | Optional. Only alerted if primary contact escalation goes unanswered. |
| **Backend** | Runs the escalation state machine in Redis. Never depends on the student's phone staying connected. |

---

## Data Visibility by Step

| Step | Student sees | Primary contact sees | Secondary contact sees |
|---|---|---|---|
| Walk active | Live ETA countdown, location streaming indicator | Walk-start notification, live map link (if consent given) | Nothing |
| ETA missed | Silent vibration + check-in screen | Nothing | Nothing |
| Check-in no response | Nothing further | FCM push + live map link | Nothing |
| SMS step | Nothing further | Twilio SMS + static map link | Nothing |
| Secondary escalation | Nothing further | Already notified | FCM push + SMS + static map link |
| Student self-resolves | Confirmation screen | Cancellation notification | Cancellation notification (if already alerted) |
| Safe arrival | Safe screen | Safe arrival notification | Nothing |

---

## Step-by-Step Escalation

### Step 0 — Walk Active

**Trigger:** Student taps "I'm walking home"

**Student:**
- Walk screen shows live ETA countdown
- Location streaming every 5 seconds via WebSocket
- Motion and audio classifiers running on-device

**Primary contact:**
- Receives FCM push: *"[Name] is on their way home. Expected arrival: [time]. You'll hear from us when they're safe."*
- If consent given and tracking active: live map link available showing student dot

**Data visible to contact:**
- Student first name
- ETA
- Live GPS position (updates every 5 seconds)

**Backend state:** `ACTIVE`
Redis keys created: `walk:{id}:location`, `walk:{id}:state`
ETA timer set.

---

### Step 1 — ETA Missed

**Trigger:** ETA passes with no geofence arrival detected

**Student only:**
- Silent vibration
- Screen notification: *"Just checking in — are you still on your way? Tap to confirm."*
- 60 second window to respond

**Primary contact:** Nothing. Contact is not involved at this step.

**Backend state:** `MISSED_ETA`
60 second timer set.

---

### Step 2 — Check-in No Response

**Trigger:** 60 seconds pass with no student response to check-in

**Student:** Nothing further on device

**Primary contact:**
- FCM push notification
- *"We haven't been able to reach [Name]. Their last known location is on the map. Please check in with them if you can."*
- Live map link included

**Data shared with contact:**
- Student first name
- Last known GPS position as live map link
- Timestamp of last known location

**Backend state:** `CHECKIN_SENT`
2 minute timer set.

---

### Step 3 — Contact No Response

**Trigger:** 2 minutes pass with no student self-resolution

**Student:** Nothing further on device

**Primary contact:**
- Twilio SMS fires — same message, different channel
- *"Nyx: We haven't been able to reach [Name] since [time]. Last location: [url]. Please check on them."*

**Data shared with contact:**
- Student first name
- Last known GPS as static map link
- Timestamp

**Backend state:** `CONTACT_NOTIFIED`
3 minute timer set.

---

### Step 4 — Secondary Escalation

**Trigger:** 3 minutes pass with no student self-resolution

**Secondary contact (if set):**
- FCM push — identical message to Step 2
- Twilio SMS — identical message to Step 3

**Data shared:**
- Identical to Steps 2 and 3
- No additional personal data at any step

**Backend state:** `SMS_SENT` → `ESCALATED`
All steps logged to `walk_events`.

---

### Step 5 — Student Self-Resolves (any point)

**Trigger:** Student taps "I'm home safe" or geofence arrival detected

**Student:** Safe confirmation screen

**All notified contacts:**
- FCM push: *"[Name] has confirmed they're safe. No action needed."*

**Backend:**
- All timers cancelled immediately
- Redis keys deleted immediately
- Session status → `safe`
- Final event written to `walk_events`

---

### Manual SOS — Shake or Silent SOS (any point)

**Trigger:** Student shakes phone hard OR taps Silent SOS button

**Student:**
- Confirmation dialog: *"Send an alert to your contacts?"*
- Buttons: *"Yes, send now"* and *"Cancel"*
- On confirm: rate limit checked (max 3 per 30 seconds)
- If rate limit hit: *"Alert sent. If you need emergency services, call 112."*

**Primary contact:**
- Skips directly to Step 2 escalation (FCM push + live map link)
- No waiting for ETA or check-in

**Backend state:** Jumps directly to `CONTACT_NOTIFIED`

---

## Revocation Controls

| Action | Who | Effect |
|---|---|---|
| "Stop receiving updates" | Contact | WebSocket closes immediately. Location relay stops. Safety alerts still fire. |
| Remove contact from settings | Student | All data sharing terminated immediately. Contact receives neutral removal notification. No location data included. |
| Walk ends (safe or cancelled) | Student or backend | Redis keys deleted immediately. Map link returns 404. Session closed. |

---

## State Machine

```
ACTIVE
  │
  │ ETA passes, no arrival
  ▼
MISSED_ETA
  │
  │ 60s, no check-in response
  ▼
CHECKIN_SENT
  │
  │ 2 min, no resolution
  ▼
CONTACT_NOTIFIED
  │
  │ 3 min, no resolution
  ▼
SMS_SENT
  │
  │ Secondary contact alerted
  ▼
ESCALATED

Every state: student self-resolves → CANCELLED
Any state: geofence arrival → SAFE
Any state: manual SOS → jumps to CONTACT_NOTIFIED
```

Every state transition writes a row to `walk_events` with timestamp, event type, recipient, and data shared.
