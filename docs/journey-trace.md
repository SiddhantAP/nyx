# Journey Trace — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## Persona

**Priya, 20. Second year. Computer Science.**

Lives 18 minutes from campus on foot. Takes the late bus when it runs, walks when it doesn't. Her mum asks her to text when she gets home. She forgets about half the time — not because she doesn't care, but because by the time she's unlocking her door she's already thinking about something else. Her mum stays up.

---

## The Journey

### 11:47pm — Library closing

Priya packs up. She's been here since 8. She's tired. She puts her headphones in.

She thinks about texting her mum. Opens WhatsApp. Sees 3 unread messages from a group chat. Gets distracted. Puts her phone in her pocket. Starts walking.

**Friction identified:** The intent to communicate is there. The steps required — open app, find contact, compose message, send, wait for read receipt — are too many for someone who is tired and already moving. She abandons the action entirely.

---

### 11:48pm — Outside the library

Priya opens Nyx. One screen. One button.

*"I'm walking home"*

She taps it. Phone goes in pocket.

**Aha moment — 00:00:08 from app open.**

Eight seconds. That's the entire interaction. ETA calculated. Location streaming. Mum notified. Nyx is watching.

**What made it work:** No destination entry. No contact selection. No confirmation screen. The system already knows her home location and her trusted contacts. The only decision she makes is to start.

---

### 11:48pm — Priya's mum's phone (Nagpur)

FCM push arrives.

*"Priya is on their way home. Expected arrival: 12:06am. You'll hear from us when they're safe."*

Mum reads it. Puts her phone down. Goes to sleep.

**What made it work:** The notification is complete. It contains everything needed — who, what, when. No action required from the contact. No app to open. No map to watch. Just information, delivered calmly.

---

### 12:03am — Walking

Priya stops to tie her shoelace outside a closed pharmacy. Stands there for 4 minutes checking a meme someone sent her.

Motion anomaly detected. On-device accelerometer registers unexpected stop.

No alert fires. No vibration. The system notes it but waits — a 4 minute stop is within normal behavior range. The ETA buffer absorbs it.

**What worked:** The system does not over-react. A stopped student is not a distressed student. The buffer exists precisely for this.

---

### 12:09am — ETA passes (3 min late)

Priya is 2 streets away. Still walking. Not worried.

Backend: ETA passed. No geofence arrival. State → `MISSED_ETA`.

Student phone: silent vibration. Screen lights up.

*"Just checking in — are you still on your way? Tap to confirm."*

Priya feels the vibration. Takes out her phone. Taps confirm without reading the full text — muscle memory.

State resets. ETA extended 10 minutes. Mum: still asleep. Knows nothing.

**What worked:** The check-in is private. It requires one tap. It does not alarm the contact. It gives Priya the chance to self-resolve in under 3 seconds.

**Friction identified:** Priya had to take her phone out of her pocket. In a genuinely distressing situation, this might not be possible. (Mitigated by shake detection and silent SOS for those cases.)

---

### 12:14am — Home

Priya reaches her building. PostGIS geofence triggers — 100m radius.

Backend: state → `SAFE`. Redis keys deleted. Session closed.

Mum's phone:

*"Priya arrived home safely at 12:14am. No further updates."*

Mum doesn't see this until morning. That's fine. That's the point.

**What worked:** Priya didn't have to do anything. No "I'm home safe" tap needed — the geofence handled it automatically. The contact notification is calm, final, and requires no response.

---

## Retention Hook

The next time Priya opens Nyx, the insights screen shows:

- 3 walks this week
- Average walk: 19 minutes
- Always home safe

No streak pressure. No gamification. Just a quiet record that someone was watching.

---

## Friction Summary

| Moment | Friction | Resolution |
|---|---|---|
| Deciding to communicate at all | Too many steps in WhatsApp | One tap replaces entire flow |
| Starting the walk | Destination entry, contact selection | Removed entirely — system knows both |
| Check-in response | Unlocking phone, reading notification | Single tap dismiss, no reading required |
| Arriving home | Remembering to send "I'm home" message | Geofence handles it automatically |
| Contact staying informed | Contact needs to actively watch | Push notification delivers complete information passively |

---

## What Nyx Does Not Do

Nyx does not solve every safety problem. It solves the first one — making sure someone knows you're on your way home, and knows immediately if something changes. Everything else — campus lighting, escort services, emergency response — is outside its scope and out of scope intentionally. A tool that tries to do everything does nothing well.
