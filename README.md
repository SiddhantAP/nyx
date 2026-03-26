# 𝑁𝑌𝑋
### *Your guardian for the walk home.*

**Track: Safety & Wellbeing - RentIts Global Hackathon 2026**

<br>

> *It's 1am. The library is closing. She's walking back to her dorm alone.*
> *She wants to tell someone she's on her way - but opening an app, finding a contact,*
> *typing a message, waiting for a reply - she doesn't do it.*
> *She just walks and hopes.*
>
> **Nyx makes that moment one tap.**

<br>

---

## The Problem

Every night, thousands of students walk home alone after late classes, library sessions, and club events. They want someone to know. But the tools available to them — emergency calls, location sharing apps, check-in messages — all demand too much from someone who is already nervous, already moving, already alone in the dark.

Emergency calls require speaking out loud. Location sharing requires the contact to be actively watching. Safety apps require setup, forms, and deliberate triggers. None of them are designed for the cognitive reality of someone who is scared.

So most students do nothing. They just walk and hope.

---

## What Nyx Does

| | |
|---|---|
| **One tap** | Starts a walk. No forms, no destination entry, no friction. Phone goes in pocket. |
| **Calm contacts** | Trusted contacts are notified when you set off and when you arrive safely. No noise in between. |
| **Graduated escalation** | If something goes wrong — check-in first, then notification, then SMS. No panic, no false alarms. |
| **Shake to alert** | Hard shake from anywhere — including the lock screen — fires an immediate alert. |
| **On-device AI** | TensorFlow.js + YAMNet listens for distress sounds. No audio ever leaves your phone. |
| **Consent-first** | Contacts explicitly accept before receiving anything. They can revoke access at any time. |

---

## How It Works

When a student starts a walk, Nyx opens a WebSocket connection to stream live GPS every 5 seconds to a Redis session store — coordinates never touch PostgreSQL. OpenRouteService calculates the walking ETA and PostGIS monitors a 100m geofence around home. A Redis-backed escalation state machine watches the clock: if the student doesn't arrive, it fires a silent vibration check-in first, waits 60 seconds, then escalates to an FCM push notification to the trusted contact with a live map link, then to a Twilio SMS, then to any secondary contact — each step logged to an immutable audit trail. On the student's device, TensorFlow.js runs Google's YAMNet audio model continuously, classifying ambient sound against a confidence threshold of 0.85 — a spike triggers a check-in, never a direct alert. The moment a walk ends, Redis keys are deleted immediately. The map link returns 404. The session is over.

---

## Safety by Default

Nyx is designed to work correctly even when the user is panicked, rushing, or not paying attention.

- **One action per screen.** No screen requires reading under stress.
- **Vibration before notification.** The student always gets a private check-in before any contact is alerted.
- **Shake requires confirmation.** A dialog appears before any alert fires — accidental triggers don't reach contacts.
- **Rate limited SOS.** Maximum 3 activations per 30 seconds. Cooldown message appears after limit. No spam.
- **Backend-driven escalation.** If the student's phone dies mid-walk, the Redis timer keeps running. Escalation fires normally. The system never depends on continued phone connection.
- **Silent SOS.** Full alert chain with zero phone audio — usable in any situation.

---

## Escalation Chain

```
Walk starts
    │
    ▼
ETA window passes ──────────────────────────────────► Student arrives safely
    │                                                        │
    ▼                                                        ▼
Vibration check-in on student phone              Safe arrival notification
60 second window                                 to all contacts. Done.
    │
    │ No response
    ▼
FCM push → trusted contact
Live map link. Student last known position.
    │
    │ No response (2 min)
    ▼
Twilio SMS → trusted contact
Same message. Different channel.
    │
    │ No response (3 min)
    ▼
Secondary contact alerted
FCM + SMS both fire.
```

*At any point — student shakes phone → immediate alert skips the chain.*
*At any point — student taps "I'm home safe" → chain cancelled, contacts notified.*

Full map: [`docs/escalation-map.md`](docs/escalation-map.md)

---

## Consent Model

```
Student adds contact
        │
        ▼
Twilio SMS fires to contact
"[Name] has added you as a trusted contact. Tap to accept."
        │
        ▼
Contact opens consent screen
Reads exactly what they're agreeing to
        │
        ▼
Contact explicitly accepts
        │
        ├── Location relay: ACTIVE (can revoke anytime)
        └── Safety alerts: ALWAYS ON (even after revoking location)

Contact taps "Stop receiving updates"
        │
        ├── WebSocket closes immediately (backend-enforced, not just UI)
        ├── Location relay: OFF
        └── Safety alerts: STILL FIRE

Student removes contact from settings
        │
        └── All access terminated immediately. No grace period.
```

---

## Abuse Prevention

| Mechanism | Implementation |
|---|---|
| SOS rate limit | Max 3 triggers per 30 seconds per session. Returns 429 with `retry_after`. |
| Confirmation dialog | Every SOS trigger shows "Send an alert to your contacts?" before firing. |
| Cooldown message | After rate limit hit: "Alert sent. If you need emergency services, call 112." |
| Audit trail | Every alert, escalation step, and cancellation written to `walk_events` with timestamp and recipient. |
| Audio threshold | YAMNet confidence minimum 0.85 before triggering check-in. Never triggers direct alert. |
| False positive recovery | Student has 60 seconds to self-resolve before any contact is notified. |
| Easy cancellation | "I'm home safe" cancels all escalation and notifies contacts immediately. |

---

## Privacy by Design

- **Live location** lives in Redis only. TTL = ETA + 30 minutes. Deleted immediately on walk end.
- **Raw audio** is never transmitted. Never stored. Confidence score only, discarded after use.
- **Accelerometer data** never leaves the device.
- **Contacts** receive only: student first name, ETA, live map link during active session.
- **Consent enforced at WebSocket level** — not just the UI. No accepted consent = connection rejected.
- **Map links** return 404 the moment a walk ends.

Full manifest: [`docs/privacy-manifest.md`](docs/privacy-manifest.md)

---

## Tech Stack

**Frontend**
```
Next.js 14          App Router, TypeScript, PWA
Tailwind CSS        Dark-first, calm escalation palette
MapLibre GL JS      Live student location rendering
TensorFlow.js       On-device YAMNet audio classification
Service Workers     Background GPS, shake detection from lock screen
Firebase FCM        Push notifications
Vercel              Deployment
```

**Backend**
```
FastAPI             Python 3.12, async throughout
PostgreSQL          User data, consent state, session metadata
PostGIS             ST_DWithin geofence, 100m home radius
Redis               Live location (TTL), escalation state machine, rate limiting
WebSockets          Real-time location relay, student ↔ contact
OpenRouteService    Walking ETA calculation
Twilio              SMS alerts and consent invites
Firebase Admin      FCM push notification delivery
Railway             Deployment
```

---

## Scoring Artifacts

| Artifact | File |
|---|---|
| Risk Register | [`docs/risk-register.md`](docs/risk-register.md) |
| Escalation Map | [`docs/escalation-map.md`](docs/escalation-map.md) |
| Privacy Manifest | [`docs/privacy-manifest.md`](docs/privacy-manifest.md) |
| Copy Deck | [`docs/copy-deck.md`](docs/copy-deck.md) |
| Journey Trace | [`docs/journey-trace.md`](docs/journey-trace.md) |
| Flow Clarity | [`docs/flow-clarity.md`](docs/flow-clarity.md) |
| UX Trade-offs | [`docs/ux-tradeoffs.md`](docs/ux-tradeoffs.md) |
| Research Memo | [`docs/research-memo.md`](docs/research-memo.md) |

---

## How to Test

1. Open the app on any Android phone
2. Complete onboarding — name, home location, one trusted contact
3. The contact receives an SMS invite — open the link and accept
4. Tap **"I'm walking home"** on the student phone
5. Contact phone receives a push notification within 10 seconds
6. Open the live map link on the contact phone — student dot is visible
7. To test escalation: wait for ETA to pass without tapping "I'm home safe"
8. To test SOS: shake the student phone hard — confirm the dialog — watch alert arrive on contact phone
9. To test rate limiting: shake 3 times rapidly — cooldown message appears
10. To test revocation: contact taps "Stop receiving updates" — dot disappears, but alerts still fire
11. To test cancellation: tap "I'm home safe" — contact receives safe arrival notification immediately

---

## Live Demo

| | |
|---|---|
| **App** | *[Vercel URL]* |
| **Demo video** | *[Link]* |

---

<br>

*Named after Nyx — the Greek goddess of the night, one of the first primordial beings, feared even by Zeus. She walks the dark so others don't have to.*
