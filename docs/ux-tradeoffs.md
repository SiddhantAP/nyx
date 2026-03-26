# UX Trade-offs — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## What We Cut and Why

Every cut in Nyx was a deliberate judgment call. This document records what we decided not to build, what we shipped instead, and why the simpler version is the right version for this product.

---

### 1. Destination entry — Cut entirely

**What perfect looks like:**
Student enters a custom destination each walk. Route is calculated. Deviation from route triggers check-in. ETA is always accurate.

**What we shipped:**
Student sets home location once during onboarding. Every walk goes home. ETA calculated from current position to home. No route deviation tracking.

**Why:**
This app is used at the moment of highest cognitive load — tired, end of night, one hand on the phone. Adding a destination entry step removes the core value proposition. The product exists because existing tools require too many steps. Adding a step to the core flow to enable a marginal accuracy improvement is the wrong trade. 95% of use cases are "walking home." We optimised for 95%.

---

### 2. Live route line on map — Cut

**What perfect looks like:**
Contact sees the student's full walking route on the map — a line from origin to home, with the student dot moving along it.

**What we shipped:**
Contact sees the student dot only. No route line.

**Why:**
Route calculation requires a directions API call per session. Displaying it requires additional MapLibre layers. More importantly — the route line implies the student is following a specific path, which creates a false expectation when they take a shortcut or stop somewhere. The dot is honest. It shows where the student is, not where we predicted they'd be.

---

### 3. In-app chat with contact — Cut

**What perfect looks like:**
Contact can send a message to the student from the live map view. "I can see you, you're almost home."

**What we shipped:**
No in-app messaging. Contacts use their existing messaging apps.

**Why:**
Building a messaging layer adds WebSocket complexity, notification routing, and read receipts. It also creates a false sense of safety — a contact who is messaging is a contact who is distracted from the actual task, which is watching the map and being ready to act. The contact's job is simple: watch, wait, act if alerted. Messaging complicates that.

---

### 4. Multiple simultaneous walks — Cut

**What perfect looks like:**
Student can have multiple active sessions — useful if a student wants to monitor a friend walking home at the same time.

**What we shipped:**
One active walk session per user at a time.

**Why:**
The data model, Redis state machine, and WebSocket architecture all assume one active session per student. Supporting multiple sessions multiplies complexity across every layer. The use case is real but rare. For a hackathon build, we optimised for the primary flow.

---

### 5. Walk scheduling — Cut

**What perfect looks like:**
Student can schedule a walk in advance. "I'm leaving the library at 11:30pm." Contact is pre-notified. Session starts automatically.

**What we shipped:**
Walk starts on tap only. No scheduling.

**Why:**
Scheduled walks require a background job runner, a notification 15 minutes before the scheduled time, and handling the case where the student doesn't actually leave at the scheduled time. The complexity is significant. The benefit is marginal — tapping one button takes 8 seconds. Scheduling a walk takes longer than that.

---

### 6. SOS without confirmation — Cut (intentionally not shipped)

**What perfect looks like:**
Shake phone → alert fires instantly, no dialog.

**What we almost shipped:**
No confirmation dialog on shake-to-alert.

**Why we kept the dialog:**
Shake detection has a high false positive rate. Phones get shaken in bags, on buses, during exercise. A false alert firing to a trusted contact at 2am is a significant harm — it causes real distress to a real person. The one-tap confirmation adds less than 2 seconds to the SOS flow and eliminates almost all false positives. For a safety product, the confirmation dialog is not friction — it is a feature.

---

### 7. Insights gamification — Cut

**What perfect looks like:**
Walk streaks. Badges for consistent safe arrivals. Social sharing of safety scores.

**What we shipped:**
Quiet walk history. No streaks. No badges. No sharing.

**Why:**
Gamification creates pressure. A student who breaks a streak might feel anxiety about opening the app. A student who shares their safety score is sharing behavioral data publicly. Neither outcome serves the product's core purpose. The insights screen exists to give the student a quiet sense that Nyx is working. That's all it needs to do.

---

## The Judgment We Applied

Every cut came down to one question: **does this feature serve the student in the moment of use, or does it serve a hypothetical better version of the product?**

Nyx is used at night, tired, one-handed, under mild to moderate stress. Every feature that adds a step, a decision, or a distraction in that moment is a feature that works against the product. We cut everything that didn't pass that test.

The result is a product with fewer features than we designed and more focus than we expected.
