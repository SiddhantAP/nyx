# Research Memo — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## What We Were Trying to Understand

Before building anything, we needed to answer one question: **why don't students already do the safe thing?**

The safe thing is easy to describe. Text someone when you leave. Text them when you arrive. If you don't arrive, they call you. Simple. Free. No app required.

Most students know this. Most students don't do it consistently. We wanted to know why.

---

## What We Observed

### Observation 1 — The action is abandoned at the moment of initiation, not midway

Students don't start to text and then give up. They decide not to start. The friction is at the very beginning — finding the contact, opening a conversation, composing something. By the time they've done two of those three steps, they're already halfway down the street and the moment has passed.

**What this told us:** The solution is not a better messaging interface. It is the elimination of the messaging interface entirely. One tap replaces the whole flow.

---

### Observation 2 — Students are more worried about worrying their contacts than about their own safety

A recurring pattern: students don't send the "I'm walking home" message because they don't want to make their parent or friend anxious if they're late. They'd rather say nothing than say something and then be 10 minutes late and have someone panic.

**What this told us:** The contact experience matters as much as the student experience. Nyx's graduated escalation — calm notification on departure, calm notification on arrival, nothing in between unless something is wrong — directly addresses this. The contact only hears from Nyx when there's a reason to. Students can use the app without fear of causing unnecessary worry.

---

### Observation 3 — Existing safety apps feel like surveillance tools

Students who had tried safety apps described them as "creepy," "like being tracked," and "something a controlling parent would use." The mental model was wrong from the start — these apps positioned themselves as monitoring tools, not as communication tools.

**What this told us:** Framing matters enormously. Nyx is not a tracking app. It is a notification system that happens to use location. The copy, the consent flow, and the contact controls all reflect this. The contact's first experience is a consent screen that explains exactly what they're agreeing to. The opt-out is in every notification. The map link expires the moment the walk ends.

---

### Observation 4 — The contact's experience is almost always ignored

Every safety app we looked at was designed entirely for the person being watched, not for the person watching. Contacts were treated as passive recipients of data. No thought was given to what the contact experience should feel like — how to notify them without alarming them, how to give them enough information to act without overwhelming them, how to let them know everything is fine.

**What this told us:** The contact is a user. Design for them. Every notification Nyx sends to a contact was written to answer three questions: what is happening, what do I need to do, and will I hear back. The answer to the third question is always yes.

---

### Observation 5 — Students stop using safety tools after the first false alarm

One unnecessary alert — a contact calling in a panic because the student was 5 minutes late — was enough to make students abandon the tool permanently. Trust in the system was binary. Once broken, it didn't recover.

**What this told us:** False positives are not an inconvenience. They are an existential risk to the product. Every architectural decision in the escalation chain — the check-in before contact notification, the 60 second window, the rate limiting, the confidence threshold on audio classification — exists to protect the trust relationship between the student and their contact.

---

## What We Cut Based on This Research

### Real-time route tracking
Research showed contacts didn't want to watch a moving dot. They wanted to know two things: is this person on their way, and did they arrive safely. Continuous route visualization created anxiety, not reassurance. We cut the route line and kept the dot.

### Push-to-talk SOS
An early concept allowed the student to send a live audio clip to the contact in an emergency. Research suggested this created more problems than it solved — contacts hearing ambient noise with no context, students unable to speak in situations where speaking is dangerous. Silent SOS with location is more useful in more scenarios.

### Automatic contact notification on audio anomaly
Original design had audio classification trigger a direct contact notification at high confidence. Research on false positive impact (Observation 5) made this untenable. Audio now triggers a check-in only. The student has 30 seconds to dismiss. Contact is never notified from audio alone.

### Social proof features
An early design included a community layer — "127 students walked safely this week on your campus." Research showed this created pressure and comparison rather than reassurance. Cut entirely.

---

## What the Research Confirmed We Got Right

- **One tap.** No student we spoke to said the problem was that safety apps were hard to use once started. The problem was starting. One tap is the right answer.
- **Calm copy.** Students consistently described existing safety tools as "dramatic." Every word in Nyx was written against this feedback.
- **Contact consent.** Every student we spoke to felt uncomfortable with the idea of sharing their location without the contact explicitly knowing what they were signing up for. The consent flow is not a legal requirement. It is a design decision based on what students said they needed.
- **Graduated escalation.** The concept of "check-in first, contact second" was immediately understood and trusted by every student we described it to. It matched their intuition about how a thoughtful system should work.

---

## The Core Insight

Students don't need a better emergency tool. They need a better default.

The gap is not between "I'm in danger" and "I'm safe." The gap is between "I'm leaving" and "I'm home" — a routine 20 minute window that happens every night and almost always ends safely. Nyx fills that gap with the minimum possible friction and the minimum possible noise.

Everything else follows from that.
