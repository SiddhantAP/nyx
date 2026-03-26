# Risk Register — Nyx

Last updated: March 2026
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## Overview

Every risk in Nyx falls into one of three categories: privacy risks, false positive risks, and abuse risks. Each has a different character and a different mitigation. This register documents all identified risks, their likelihood and impact, and exactly how the system handles them.

---

## Risk Table

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| False positive — student stopped at a shop or friend's place | High | Medium | Graduated escalation. Check-in fires before any contact is notified. Student has 60 seconds to self-resolve with a single tap. Contact never knows. |
| Contact panics from an unnecessary alert | Medium | High | Calm, factual copy at every step. No alarming language until situation is confirmed. Cancellation notification fires the moment student self-resolves — contact is informed immediately. |
| Location data breach | Low | Very High | Location stored in Redis only with TTL. Never written to PostgreSQL. Deleted immediately on walk end — not at TTL expiry. Encrypted in transit over WSS. Map links return 404 the moment session ends. |
| Audio classifier false positive from loud music or crowd noise | High | Low | Audio anomaly triggers check-in only — never a direct alert. YAMNet confidence threshold minimum 0.85. Student has 30 seconds to dismiss before any escalation. |
| Contact misuses live map to track student beyond walk | Low | High | Location relay is only active during an active session. Walk ends → Redis key deleted immediately → map link returns 404. There is no replay. No historical location data stored anywhere. |
| Accidental shake-to-alert spam | Medium | Medium | Rate limit: maximum 3 activations per 30 seconds per session. Confirmation dialog on every trigger — no alert fires without explicit tap. Cooldown message appears after limit reached. |
| Student phone dies mid-walk | Medium | High | ETA timer and escalation state machine run entirely on the backend in Redis. Escalation fires normally regardless of phone connection. Backend never depends on the student device staying online. |
| Contact ignores notifications | Medium | High | Multi-channel escalation. FCM push first, then Twilio SMS on a separate channel. Secondary contact alerted if primary remains unresponsive after 3 minutes. |
| Student shares consent link publicly or with wrong person | Low | Medium | Consent tokens are UUID-based and single-use. Accepting consent is an explicit action — not automatic on link open. Student can remove any contact from settings immediately, terminating all access. |
| Stalker or abuser added as trusted contact by coercion | Low | Very High | Student controls the contact list entirely. Removal is immediate from settings with no confirmation required from the contact. Removed contact receives a neutral notification with no location data. |
| WebSocket connection drops mid-walk | Medium | Medium | Escalation timer runs on backend. If student WebSocket drops and no safe arrival is logged by ETA, escalation fires normally. Reconnection resumes location relay without restarting the session. |
| Redis key expiry before walk ends in a very long walk | Low | Medium | TTL is set to ETA + 30 minutes. For unusually long walks, TTL is extended when the student sends a location update. Key is never allowed to expire during an active session. |
| Judges or testers trigger excessive alerts during demo | Medium | Low | Rate limiting applies universally. Cooldown message is clear and informative. All test events are logged to walk_events with full audit trail. |

---

## False Alarm Drill

A false alarm is the most likely real-world failure mode. Here is exactly how Nyx handles it:

**Scenario:** Student stops at a convenience store 10 minutes before ETA. ETA passes.

```
ETA passes
    │
    ▼
Backend: state → MISSED_ETA
Student phone: silent vibration + screen notification
"Just checking in — are you still on your way? Tap to confirm."
    │
    │ Student taps confirm (in shop, sees notification)
    ▼
State resets. ETA extended by 10 minutes.
Contact: receives nothing. Knows nothing.

    │ Student misses the 60 second window (phone in pocket)
    ▼
State → CHECKIN_SENT
Contact: FCM push
"We haven't been able to reach [Name]. Their last known location
is on the map. Please check in with them if you can."
    │
    │ Student exits shop, sees missed notification, taps "I'm home safe"
    ▼
State → CANCELLED
Contact: "Rishit has confirmed they're safe. No action needed."
All timers cancelled. Redis keys deleted.
```

The contact received one calm notification and one immediate resolution. No panic. No siren. No drama.

---

## Residual Risks

The following risks are acknowledged but not fully mitigated within the scope of this hackathon build:

- **Offline areas:** GPS signal loss in tunnels or basements means location updates stop. The escalation timer continues. This may cause false positives in areas with known dead zones. Mitigation in a production build would include signal-loss detection with a grace period.
- **International SMS delivery:** Twilio trial accounts have verified number restrictions. In production, full Twilio account with regional SMS routing would be required.
- **Accessibility:** The current build is not audited for screen reader compatibility. This is a known gap for a future release.
