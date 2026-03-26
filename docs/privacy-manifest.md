# Privacy Manifest — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## Principles

Nyx is built on three privacy principles:

1. **Collect the minimum.** If we don't need it, we don't touch it.
2. **Store the minimum.** Live location never goes to the database. It lives in Redis and dies when the walk ends.
3. **Give users full control.** Every piece of data sharing can be stopped by the student or the contact at any time.

---

## Data Collected

### Student

| Data | Where stored | Purpose | Retention |
|---|---|---|---|
| Name | PostgreSQL | Displayed to contacts in notifications | Until account deleted |
| Phone number | PostgreSQL | Twilio SMS delivery | Until account deleted |
| Home location (lat/lng) | PostgreSQL | ETA calculation, geofence arrival detection | Until account deleted |
| Live GPS during active walks | Redis only | Real-time location relay to consented contacts | Deleted immediately on walk end |
| Walk session metadata (start time, end time, status) | PostgreSQL | Walk history, audit trail | 90 days then deleted |
| Walk events audit trail | PostgreSQL | Escalation logging, abuse prevention | 90 days then deleted |
| Audio classification confidence scores | Never stored | Transient on-device use only — triggers check-in if above threshold | Discarded immediately after classification |
| Accelerometer patterns | Never transmitted | On-device gait and motion anomaly detection only | Never leaves device |

### Contact

| Data | Where stored | Purpose | Retention |
|---|---|---|---|
| Name | PostgreSQL | Displayed in student's contact list | Until student removes contact |
| Phone number | PostgreSQL | Twilio SMS delivery, FCM targeting | Until student removes contact |
| Consent status and timestamp | PostgreSQL | Consent enforcement at WebSocket level | Until student removes contact |
| Consent token | PostgreSQL | Unique link for consent and revocation | Until student removes contact |

---

## Data Never Collected

- Raw audio — never transmitted, never stored, never logged
- Contact's location at any time
- Contact's device data of any kind
- Student location outside of active walk sessions
- Any biometric data
- Any data from third-party sources

---

## How Live Location Works

Live GPS coordinates follow a strict path:

```
Student device
    │ WebSocket (WSS — encrypted in transit)
    ▼
Backend receives coordinate
    │
    ▼
Written to Redis: walk:{session_id}:location
TTL = ETA + 30 minutes
    │
    ▼
Relayed via WebSocket to consented contact viewers only
    │
    ▼
Walk ends → Redis key deleted immediately
Map link → returns 404
Coordinate → gone
```

Coordinates are **never** written to PostgreSQL. There is no historical location record. There is no replay.

---

## Retention Schedule

| Data type | Retention period |
|---|---|
| Live GPS coordinates | Deleted the moment walk ends |
| Walk session metadata | 90 days, then permanently deleted |
| Walk events audit trail | 90 days, then permanently deleted |
| User account data | Deleted within 24 hours of deletion request |
| Contact data | Deleted immediately when student removes contact |

---

## User Controls

### Student controls
- Remove any contact at any time from settings — effective immediately, no confirmation required from contact
- Delete account from settings — all data deleted within 24 hours
- Request data export at any time

### Contact controls
- Revoke location tracking consent at any time via their consent link — WebSocket closes immediately, location relay stops
- Safety alerts continue even after revoking tracking consent — this is intentional and disclosed at consent time
- Contact removal by student terminates all access and data sharing immediately

---

## Consent Enforcement

Consent is enforced at the backend level, not just the UI.

When a contact attempts to connect to the contact WebSocket:

```python
# Backend rejects connection if consent not accepted
if not contact.consent_accepted:
    await websocket.close(code=4003, reason="Consent not accepted")
    return
```

A contact without accepted consent cannot receive location data regardless of what the frontend does. This is not a UI toggle — it is a hard backend gate.

When a contact revokes consent:

```python
# Backend closes active WebSocket immediately
if contact_token in active_contact_connections:
    await active_contact_connections[contact_token].close()
```

The connection closes in real time. Location relay stops immediately.

---

## On-Device Processing

The following processing happens entirely on the student's device and never reaches the server:

- **Audio classification** — TensorFlow.js + YAMNet runs locally. Raw audio is never captured to a buffer, never transmitted, never stored. Only the classification result (a confidence score) is used, transiently, to decide whether to trigger a check-in.
- **Motion analysis** — DeviceMotion accelerometer data is processed on-device to detect walking gait anomalies and unexpected stops. Raw accelerometer values are never transmitted.
- **Shake detection** — Processed on-device via Service Worker. No raw motion data leaves the phone.

---

## Security

- All WebSocket connections use WSS (TLS encrypted)
- All API calls use HTTPS
- Consent tokens are UUID v4 — unguessable, single-purpose
- Redis keys use session-scoped namespacing
- Firebase Service Account credentials stored server-side only, never exposed to client
- No API keys or secrets in frontend code — environment variables only
