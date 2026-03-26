# Flow Clarity — Nyx

Last updated: March 2026
<br>
Track: Safety & Wellbeing — RentIts Global Hackathon 2026

---

## The Flow We Identified as Broken

**Contact onboarding — receiving a consent invite and accepting it.**

This is the most critical flow in the product. If a contact cannot complete it, nothing works. No location sharing. No notifications. No safety net.

It is also the flow that happens exactly once, on a phone the contact has never used with Nyx before, triggered by an SMS they weren't expecting.

We broke it. Then we fixed it.

---

## Original Flow (Broken)

```
Contact receives SMS
    │
    ▼
Taps link
    │
    ▼
[Screen 1] — Wall of text
"By accepting, you agree to receive location updates from [Name]
during their active walk sessions. You may revoke this consent
at any time by visiting your consent settings. Location data is
stored in Redis with a TTL and deleted on session end. You will
receive FCM push notifications and Twilio SMS alerts..."
    │
    ▼
[Screen 2] — Two CTAs, same visual weight
"Accept and enable notifications" | "Decline"
    │
    ▼
[Screen 3] — Browser notification permission dialog (OS-level)
"[site] wants to send you notifications"
Allow / Block
    │
    ▼
[Screen 4] — Confirmation
"You have accepted. You will now receive notifications."
```

**Problems:**

1. Screen 1 is a legal wall. A contact receiving this at 11pm after an unexpected SMS will not read it. They will either abandon or tap through without understanding.
2. Two CTAs on Screen 2 with equal visual weight creates hesitation. The primary action is not obvious.
3. The OS notification permission dialog appears as a surprise at Step 3. The contact doesn't know why it's appearing or what it's for. Many will tap Block by instinct.
4. Screen 4 is a dead end. No context on what happens next.

**Result:** Drop-off. Contacts abandon before accepting. Student has no safety net.

---

## Redlined Version (Fixed)

### Screen 1 — Who sent this and why (single focus)

```
┌─────────────────────────────────────┐
│                                     │
│         [Nyx wordmark]              │
│                                     │
│   Priya has added you as a          │
│   trusted contact on Nyx.           │
│                                     │
│   If Priya is walking home and      │
│   doesn't arrive safely, we'll      │
│   notify you. You'll only hear      │
│   from us when there's a reason to. │
│                                     │
│   ┌─────────────────────────────┐   │
│   │        I accept             │   │  ← single CTA, full width, high contrast
│   └─────────────────────────────┘   │
│                                     │
│   What you're agreeing to →         │  ← disclosure link, not primary
│                                     │
└─────────────────────────────────────┘
```

**Changes:**
- One CTA. Full width. No competing action.
- Lead with the human — "Priya has added you" — not the legal text.
- Disclosure is available but not forced. Contact can read it if they want.
- No decline button on this screen — contact can simply close the tab.

---

### Screen 2 — Notification permission (primed, not surprised)

```
┌─────────────────────────────────────┐
│                                     │
│   One last thing.                   │
│                                     │
│   To notify you if Priya needs      │
│   help, we need permission to        │
│   send you notifications.           │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   Enable notifications      │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘

[OS dialog appears here — contact already knows why]
```

**Changes:**
- The OS permission dialog is no longer a surprise. We explain what's coming and why before it appears.
- "One last thing" signals this is the final step.
- Contact taps our button first, then the OS dialog. Primed, not ambushed.

---

### Screen 3 — Done (with context)

```
┌─────────────────────────────────────┐
│                                     │
│   You're set.                       │
│                                     │
│   You'll hear from Nyx only when    │
│   Priya is on her way home, and     │
│   when she arrives safely.          │
│                                     │
│   If you ever want to stop          │
│   receiving updates, there's a      │
│   link in every notification.       │
│                                     │
└─────────────────────────────────────┘
```

**Changes:**
- Confirmation is warm and specific — not "you have accepted."
- Sets expectation for what they'll receive and when.
- Surfaces the opt-out proactively — reduces anxiety about being stuck.

---

## Result

| Metric | Before | After |
|---|---|---|
| Screens | 4 | 3 |
| CTAs per screen | 2 | 1 |
| Notification permission surprises | 1 | 0 |
| Legal walls | 1 | 0 (disclosure available, not forced) |
| Contact knows what they signed up for | Unlikely | Yes |

---

## The Rule We Applied

**One CTA per screen.**

If a screen has two things to decide, it is two screens. If a screen has one thing to decide, make that one thing obvious. Everything else is secondary and should look secondary.

This rule applies to every screen in Nyx — not just consent. The walk screen has one button. The check-in screen has one button. The safe arrival screen has one button. Stress and one-handed use are the default conditions. The interface has to work in those conditions without asking the user to think.
