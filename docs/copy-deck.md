# Copy Deck — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## Principles

Every word in Nyx is written to lower anxiety, not raise it. The tone is a calm trusted friend — factual, clear, never dramatic. No red warnings until the situation is confirmed serious. No alarming language until absolutely necessary.

---

## SMS Messages (Twilio)

### Consent invite to contact
```
Nyx: [Name] has added you as a trusted contact. Tap to accept: [url]
```

### Alert to contact
```
Nyx: We haven't been able to reach [Name] since [time]. Last location: [url]. Please check on them.
```

---

## Push Notifications (Firebase FCM)

### Walk start — to contact
```
Title: [Name] is on their way home
Body: Expected arrival: [time]. You'll hear from us when they're safe.
```

### Safe arrival — to contact
```
Title: [Name] arrived home safely
Body: [Name] arrived home safely at [time]. No further updates.
```

### Check-in failed — to contact
```
Title: We haven't been able to reach [Name]
Body: Their last known location is on the map. Please check in with them if you can.
```

### Walk cancelled — to contact
```
Title: [Name] is safe
Body: [Name] has confirmed they're safe. No action needed.
```

---

## In-App Copy — Student

### Home screen CTA
```
I'm walking home
```

### Walk screen subtext
```
Nyx is watching. You'll be home soon.
```

### ETA display
```
Expected home by [time] · [X] min away
```

### Check-in notification
```
Just checking in — are you still on your way? Tap to confirm.
```

### Check-in confirm button
```
Yes, still walking
```

### Safe arrival CTA
```
I'm home safe
```

### Safe arrival confirmation
```
Glad you're home. Your contacts have been notified.
```

### SOS confirmation dialog
```
Headline: Send an alert to your contacts?
Confirm button: Yes, send now
Cancel button: Cancel
```

### SOS cooldown message
```
Alert sent. If you need emergency services, call 112.
```

### Silent SOS button
```
Silent SOS
```

### Audio classifier label
```
Listening on device · nothing leaves your phone
```

---

## In-App Copy — Contact View

### Consent screen headline
```
[Name] has added you as a trusted contact on Nyx.
```

### Consent screen body
```
If [Name] is walking home and doesn't arrive safely, we'll notify you. You'll only receive messages when there's a reason to.
```

### Consent accept button
```
I accept
```

### Live map screen subtext
```
[Name] is on their way home · last updated [time]
```

### Opt-out button
```
Stop receiving updates
```

### Opt-out confirmation
```
You've stopped receiving location updates. If there's an emergency, you'll still be notified.
```

---

## System Messages

### Contact removed
```
[Name] has updated their trusted contacts. You will no longer receive notifications from Nyx.
```

### Session expired (map link returns 404)
```
This walk has ended. No further location data is available.
```

### Consent already accepted
```
You've already accepted. [Name]'s walks are being monitored by Nyx.
```

---

## Tone Guide

| Situation | Tone | Example |
|---|---|---|
| Walk active, everything normal | Calm, reassuring | "Nyx is watching. You'll be home soon." |
| Check-in needed | Gentle, non-alarming | "Just checking in — are you still on your way?" |
| Contact notified, location shared | Factual, helpful | "Their last known location is on the map." |
| Student self-resolves | Warm, immediate | "Glad you're home. Your contacts have been notified." |
| SOS triggered | Clear, no panic | "Send an alert to your contacts?" |
| Emergency services needed | Direct, practical | "If you need emergency services, call 112." |
| Contact revokes tracking | Respectful, clear | "You've stopped receiving location updates. If there's an emergency, you'll still be notified." |

---

## What We Never Say

- ❌ "Emergency" — until it is one
- ❌ "Danger" — implies confirmed threat, not a missed ETA
- ❌ "Help" — too alarming for a check-in
- ❌ "We're worried about you" — emotional language that raises panic
- ❌ "Something may have happened" — speculative and frightening
- ❌ "ALERT" in caps — aggressive, not calm
