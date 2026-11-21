# Doodle Figure: production plan (v1 release)

**Starting point:** core loop done; visuals OK; sound and announcer are AI placeholders; English only; 3 months of development so far.
**Decisions already made:** $10 one-time purchase; marketing does the heavy lifting; sandbox stays out of the main game.

## 1. Gameplay improvements, by priority

### Must-have for v1

1. **A show with stakes** (fixes the "every round ends the same" problem).
   - **Before the curtain:** the sculptor is prompted "Say your guess out loud!" Everyone is in the same room, so this needs no speech tech.
   - **After the reveal:** phones vote "Nailed it / Close / Nope". The crowd reaction scales with the result: a standing ovation, polite claps, or laughter and a single cough.
   - **The night as a show:** each night is a set number of acts (for example 6–8 rounds). The playbill keeps a room score: "Tonight's company: 5 of 7 hits".
   - **Finale:** curtain call, "Best Sculptor of the Night" by phone vote, and the full programme keepsake sent to every phone.
2. **Phones as the audience.**
   - Matching emojis from several phones build into a crowd wave (laughter or applause spreads through the theatre).
   - One sculpt-time heckle ("Hurry up!" or "Ooooh") that the sculptor clearly notices.
3. **Sculpting feel.**
   - Mirror-symmetry toggle (the biggest jump in how good creatures look).
   - Duplicate, undo, and gentle snapping.
   - Check that a first-timer can make something readable in 60–90 s.
4. **Sculptor onboarding.**
   - A 30–45 s hands-on warm-up the first time a new person puts on the headset: grab, stretch, fuse, paint.
   - This is where the old sandbox belongs: as a free-sculpt warm-up stage while phones are still joining.
5. **Custom words, back in (humans only).**
   - When enabled, bots sit out and phones write prompts for each other.
   - Add a basic profanity filter and a family-friendly setting.
6. **Word content.**
   - A base list of about 300–500 words in easy, medium and hard tiers.
   - Bots draw only from the roughly 345 Quick, Draw! categories, so tag every word as bot-compatible or not.
7. **Room settings:** round length, difficulty, family filter, number of acts.

### Nice-to-have (only if time allows)

- At the reveal, a time-lapse replay of the sculpture being built, sent to the phones.
- A palette suitable for colour-blind players, and a one-handed sculpt option.
- Lighting or crowd variety per act, so act 6 doesn't look exactly like act 1.

## 2. Party modes

Ship **Classic plus one new mode** at launch. Add one more after launch as a free update; it doubles as a marketing beat.

| Mode | How it works | Build cost | Value |
|---|---|---|---|
| **Classic** (current, plus stakes) | Phones draw, VR sculpts blind, reveal | — | The core |
| **Sculpt & Guess** (recommended for launch) | Roles reversed: the sculptor sees the word, phones race to type the answer, the first correct guess scores | **Low.** Reuses everything; only a phone text box and scoring are new | Adds competition and individual scores. Keeps every phone busy the whole round |
| **Imposter** (after launch) | Every drawer gets the word except one, who only gets the category. Sculptor builds, then phones vote out the imposter | Medium | Social deduction with strong stakes; very good in clips |
| **Telephone** (after launch) | Word → drawing → sculpture → the next phone draws the sculpture → … → the chain is revealed at the end | Medium-high | Funny, and fits passing the headset around, but long rounds |
| Sandbox | — | — | Not a mode. It becomes the warm-up stage (see above) |

## 3. Production build checklist

**Audio and voice**
- Replace placeholder sound effects with licensed library sounds where they matter most: crowd, applause, curtain, UI.
- **Music:** licensed tracks or a commissioned short loop set.
- **Announcer:** AI voice is acceptable if your service's licence allows commercial use; keep one consistent voice. A human voice actor is an optional upgrade.
- Check the current Meta store rules on AI-generated content disclosure before submitting.

**Performance and comfort**
- Hold 72 fps on Quest 2 and 90 fps on Quest 3/3S.
- Seated play works.
- Essential UI sits inside a narrower field of view (helps future VR glasses support).

**Networking at scale**
- **Photon costs:** each phone counts as a concurrent connection, so a full room of 1 headset plus 5 phones is 6 connections. Check Photon's pricing tiers against your expected peak players before launch.
- Load-test many rooms at once.

**Safety, privacy and rating**
- Privacy policy for the phone site: no accounts, keep data to a minimum.
- Moderation for custom words.
- IARC age rating questionnaire.
- Make it easy for a host to report or kick a player.

**Store and platform**
- Pass Meta's store technical requirements checks (VRC).
- Store page assets: real-people screenshots, the 90 s trailer.
- Support email and Discord.

**Analytics** (minimal, anonymous)
- Rounds per session and session length.
- Number of phones per room.
- Mode played.
- Where groups stop playing.

## 4. Schedule (about 10–12 weeks to launch, February–March)

| Weeks | Focus |
|---|---|
| 1–4 | Show structure and stakes, phone crowd waves and heckle, sculpt tools (mirror, undo, duplicate), warm-up stage, custom words back |
| 5–8 | Sculpt & Guess mode, word list and tiers, audio pass, settings. **Weekly real-group playtests, filmed** |
| 9–10 | Bug fixing, performance, store requirements checks, privacy and rating, store page, trailer re-cut |
| 11–12 | Launch buffer, press and creator outreach, launch |
| After launch | Free word pack every 6–8 weeks; Imposter mode as the first big free update |

**Holiday gatherings (now to January)** are playtest and footage season, running alongside weeks 1–6.

## 5. Budget (rough estimates; check current prices)

| Item | Estimated range |
|---|---|
| Licensed sound effects and music | $100–500 |
| Announcer (AI subscription, or a human voice actor) | $20–800 |
| Photon plan (depends on concurrent users) | check current tiers |
| Hosting and domain (phone site) | $0–20/month |
| Trailer edit (do it yourself or hire) | $0–1,000 |
| Paid ads | **$0** (not recommended before organic clips show what works) |
| **Total** | **about $500–2,500** |

## 6. When to stop investing

- **Time box:** about 3 more months to launch. Don't add a third mode or sandbox before launch.
- **Before launch:** keep improving if real groups ask for "one more round" or ask to play again next time. If they don't, fix the core (stakes, sculpt feel) before adding anything new.
- **After launch:** set a check-in at about 8 weeks (sales, wishlist conversion, session data, reviews). Decide then whether to do bigger updates (new modes, other languages, VR glasses support) or move on.
- **Be realistic about sales:** a solo-developer $10 party game on Quest can range from a few hundred to a few thousand copies in year one, depending almost entirely on marketing traction. Keep costs low enough that the low end is fine.
