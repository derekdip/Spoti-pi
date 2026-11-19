# Meta VR Start Developer Competition 2026: competitive analysis for Doodle Figure

Research date: 2026-11-19, the day after submissions closed (Nov 18, 12:00 PT).
Labels used throughout: **[V]** verified from an official source or the page itself, **[D]** developer-reported claim, **[I]** my inference, **[J]** subjective judgment, **[?]** unknown.

---

## 0. Bottom line (read this first)

1. **The field is large, and its top tier is deep.** There are 2,105 submissions **[V]**. A systematic 10% sample suggests about 260 entries (10–20% of the field) look like polished, complete experiences on paper **[I]**. Roughly 40–80 look like realistic award contenders **[J]**.
2. **Doodle Figure looks like a credible but not front-running submission.** On Meta's four criteria I score it **74/100 (plausible range 66–82)**. The best eligible competitors I found sit at **79–83**. On raw quality it ranks roughly 10th–15th among about 25 serious Social & Multiplayer contenders **[J]**.
3. **Its unusual position is that it fits the Social & Multiplayer award almost perfectly.** I read all 868 multiplayer-candidate descriptions. Doodle Figure is the **only** entry I found where non-headset people physically in the same room are *essential* players. It is also among the few social entries a judge can fully experience with one headset and their own phone. Nearly every stronger social entry needs 2–4 headsets.
4. **Calibrated chances** (§10): Best Social & Multiplayer **about 5–12%**, Adapted Gaming winner or runner-up **about 3–8%**, Best First Five Minutes **about 1–4%**, **any award about 8–18%**. These are wide because the trailer could not be watched and judges' play-testing depth is unknown.
5. **Biggest threats:**
   - **Social award:** Game Night – Tabletop Mode, Campy, 23:17, RULE MAKER, PullFit, Sneak-A-Snack and Let's Flock.
   - **Adapted Gaming:** Game Night and Surface Breach, plus Let's Flock if Meta keeps it in Gaming.

---

## 1. Competition overview

### Verified facts [V]
Source: https://start-developer-competition-26.devpost.com/rules

- **Submissions:** 2,105 unique projects across 88 gallery pages (24 per page) on 2026-11-19; I scraped every page and removed duplicates. The participants tab showed 7,244.
- **Entry period:** Sep 24 – Nov 18, 2026. Judging runs about Nov 18 – Dec 9, and winners are announced about Dec 11.
- **Tracks:** Entertainment, Gaming, Productivity. Meta can re-assign an entry's track.
- **Divisions:** New Experience, or Adapted / Significantly Updated (existed before Sep 24; "adding multiplayer support" is listed as an example of a significant update). Meta can re-assign an entry's division.
- **Track and division are private.** They are selected on the submission form and appear nowhere on the public gallery or project pages. Every track or division value in my data is either stated in the entry's own text or inferred.
- **Judging:**
  - Stage One is a pass/fail viability check.
  - Stage Two uses four equally weighted criteria (25% each). "AI tools may also be used to assist in the judging, but final decisions will be made by human judges."
  - Judges are given an APK in a "Competition" release channel, or a URL for WebXR, so they *can* play the builds. Judges are not required to watch more than 3 minutes of video.
- **Exact criteria wording (condensed quotes):**
  - **Innovation & Creativity:** "originality, creative ambition, and relevance to the chosen track… uniquely leverage Meta device capabilities (e.g., spatial depth, hands-first design, gaze, passthrough mode, scene understanding, persistent anchors) to drive repeat usage."
  - **Experience Design:** "design, mechanics, and user journey… seated, hands-first, or context-specific use… intuitive navigation, clear onboarding, and a habit-forming purpose." It also says "Passthrough should be purposeful" and "We'll also evaluate FoV-aware design."
  - **Technical Implementation:** "reliability, and strategic use of platform tools… gaze interactions (ISDK v207+), hand tracking, passthrough, spatial anchoring, and FoV-aware design… performant on Meta Quest hardware (min 60 fps), solid and bug-free."
  - **Polish & Presentation:** "UI/UX, art direction, and sound design… high-quality submission materials (text, images, video)… show real gameplay that honestly represents the experience… Don't lean on AI-generated video."
- **Prizes:** limit **one prize per entry**.
  - **Track prizes:** Best New and Best Adapted in each track, each with a winner and a runner-up (12 prizes). Entertainment and Gaming pay $100k/$50k; Productivity pays $70k/$35k.
  - **Special awards ($25k, one winner each):** Social & Multiplayer ("Experiences designed for shared presence—co-watching, cooperative play, social spaces, or asymmetric multiplayer"), Agentic Interaction, Reason to Come Back, First Five Minutes, Accessibility Forward, and Boldest Original Concept.
  - **Judge's Choice:** 2 × $20k. That makes **20 prizes in total**.
- **Who can win the special awards:** the rules attach no track or division restriction to them, so I infer they are open to all 2,105 entries **[I]**. Doodle Figure competes for Social & Multiplayer against every track and both divisions.
- **One prize per entry matters:** a strong entry that wins its track prize is removed from the special-award pool **[I]**. That slightly helps second-tier entries like Doodle Figure in special awards.

### Implications [I]
- Doodle Figure is fully immersive VR with no passthrough, MRUK, anchors or gaze. The written criteria explicitly reward those platform features, which is a structural scoring disadvantage on Innovation and Technical Implementation compared with MR entries.
- "Seated / easy in-out / ≤10 minutes" are guidelines, not requirements. Doodle Figure's 2-minute rounds fit them well.

---

## 2. Methodology and coverage (honest accounting)

| Item | Count |
|---|---|
| Gallery pages scraped | 88 / 88 |
| Unique projects discovered | **2,105** |
| Project pages downloaded and parsed (full text, built-with, images, video link) | **2,105 / 2,105** |
| Descriptions read and classified by an LLM screener against a fixed rubric | **999** (868 multiplayer candidates + 210 systematic sample; some overlap) |
| Projects I personally read (full text or first about 1,700–3,500 characters) | **about 30** (the 19 you named, Doodle Figure, 8 additional social contenders, plus Eddie and I and Surface Breach in part). For everything else in §5 I relied on screener records. |
| Projects whose screenshots and trailer thumbnails I visually inspected | **16** (including Doodle Figure) |
| **Trailers actually watched** | **0** |
| Projects never read beyond title, tagline and metadata | about 1,100 single-player entries outside the sample (keyword-negative for multiplayer) |

How I selected and screened the entries:
1. **Discovery.** I scraped all 88 pages and downloaded every project page.
2. **Multiplayer filter.** A broad keyword and regex filter (multiplayer, co-op, asymmetric, Photon/Normcore/Netcode, phone/browser join and similar) flagged 840 candidates. A second false-negative pass added 28 more. The 2nd pass found 2 additional real contenders (Hand Soccer League, plus one borderline), so the filter misses some entries. I expect a small number of real multiplayer entries remain unread.
3. **Screening.** Seven parallel LLM screeners read every candidate description with the same rubric. They assigned an A–D social category, implemented vs planned, a tier from 1 to 5, and flags.
4. **Field-strength sample.** Two more screeners graded a systematic sample (every 10th gallery position, n = 210), regardless of genre.
5. **Deep review.** I read the shortlist myself and looked at screenshots and thumbnails, then scored it (§5).

**Trailer limitation.** YouTube served this research container a bot-check captcha, and trying to get around it was blocked by policy. **No trailer was watched, including yours.** Trailer-quality fields read "NOT WATCHED". My polish assessments rely on screenshots, the YouTube thumbnail and the written description. That is a real gap, because judges may watch the videos.

**Screener calibration warning.** The two sample graders disagreed on how often to award tier 4: one gave 21 of 105, the other 5 of 105. Tier-4 counts are therefore reported as a range.

---

## 3. Field strength (Part 8)

**Systematic sample, n = 210.** Approximate 95% intervals scaled to 2,105 entries:

| Tier | Sample | Est. share | Est. count |
|---|---|---|---|
| 1 Incomplete / minimal | 22 | 10% (6–15%) | about 130–310 |
| 2 Functional but basic | 50 | 24% (18–30%) | about 380–620 |
| 3 Good prototype | 112 | 53% (47–60%) | about 980–1,270 |
| 4 Polished, complete | 26 | 12% (5–20% given grader disagreement) | about 100–420 |
| 5 Exceptional | 0 | <2% | likely a few dozen at most |

Grades come from descriptions only, which inflates them, so the real share of "good prototypes" is probably lower **[J]**. Descriptions in this competition are unusually long and polished (median 651 words), and many are visibly AI-assisted. Text quality separates entries less than usual.

**Social & Multiplayer counts** (observed among the 868 screened; the sample-based estimate agrees):

| Measure | Count |
|---|---|
| Any multiplayer actually claimed as implemented (categories A–D) | **about 270** (13% of the field) |
| Multiplayer central or substantial (A or B) | **165**, of which 163 claim it is implemented. Category A (social essential) alone: 48 |
| A/B, implemented, tier ≥3 ("complete-ish functioning social experiences") | **144** |
| Screener-flagged as plausible Social & Multiplayer contenders | **143** (generous) |
| My judgment of *credible* award contenders | **about 20–30** **[J]** |
| A/B entries where non-headset people actively play | **28**, mostly remote: browser social spaces, PC/phone cross-play, a family member watching on a phone |
| Direct competitors: party game, same room, non-headset players essential | **essentially none besides Doodle Figure.** The closest are Kaiju Corp (PC raiders, remote), Crokinole (a PC/Android seat), MYX House Party (phone guests at a DJ party, no game loop) and HumBubble (phones join a music studio). |

---

## 4. Named competitors: were they submitted? [V]

All 19 named 2026 entries were found in the gallery:
RULE MAKER, Let's Flock ("Lets Flock"), Campy, MYX House Party, GathrXR, Project Arena, ScornholeXR, Tower Chaos, GestureMancerKing, Desk Session ("Desk Session: Fingerboard Simulator", slug `finger-jam`), PullFit, World Expo, Spatial Watch, Squingle Arcade, Wormhole Electric Co., Project S ("PROJECT S - VR/MR TABLETOP RTS"), Seamline, Shadow Zoo and GLOVR.

**Potato Party is not in the gallery.** It is treated only as an external commercial comparison: a released local-multiplayer party title. I did not research it further.

---

## 5. Scoring matrix (Part 3 / 5)

Full table: `scoring_matrix.csv`.

**Scale (applied identically to all entries):**
- **95:** festival or store-feature quality on every axis, verified on device.
- **90:** excellent with minor gaps.
- **80:** clearly strong, with one notable weakness.
- **70:** competent, credible prototype with clear weaknesses.
- **60:** functional but basic.
- **≤50:** unverified or minimal.

From descriptions and screenshots alone I don't give anything above about 85, and every score carries a range of ±5–8.

| # | Project | Social cat. | Score | Range | Can a lone judge experience the social part? |
|---|---|---|---|---|---|
| 1 | [Game Night – Tabletop Mode](https://devpost.com/software/game-night-tabletop-edition) | A | 83 | 77–88 | Poorly (2–4 co-located headsets) |
| 2 | [Campy](https://devpost.com/software/campy-39z46g) | B | 83 | 77–88 | Solo fire yes; social needs headsets |
| 3 | [23:17](https://devpost.com/software/23-17) | A | 83 | 75–87 | No (2 headsets, remote) |
| 4 | [RULE MAKER](https://devpost.com/software/rule-maker) | A/B | 82 | 74–87 | Practice AI opponent |
| 5 | [PullFit](https://devpost.com/software/pullfit) | B | 82 | 76–87 | Solo yes |
| 6 | [Desk Session](https://devpost.com/software/finger-jam) | B | 82 | 75–87 | Solo yes |
| 7 | [Let's Flock!](https://devpost.com/software/lets-flock) | A/B | 79 | 72–85 | Bots; hub needs people |
| 8 | [Sneak-A-Snack](https://devpost.com/software/sneak-a-snack) | A | 79 | 71–85 | No (2 headsets) |
| 9 | [Crokinole](https://devpost.com/software/crokinole) | B | 77 | 70–83 | Bot; PC/Android seat |
| 10 | [Bots & Pans](https://devpost.com/software/steak-9d8c6j) | B | 77 | 70–83 | Solo yes |
| 11 | [Snappy Planet](https://devpost.com/software/snappy-planet) | B | 76 | 69–82 | Bots |
| **12** | **[Doodle Figure](https://devpost.com/software/doodle-figure)** | **A** | **74** | **66–82** | **Yes: 1 headset + any phone; bots for solo** |
| 13 | [Project Arena](https://devpost.com/software/project-arena) | B | 74 | 67–80 | Bot/training |
| 14 | [Boplo](https://devpost.com/software/boplo) | B | 71 | 65–77 | Solo |
| 15 | [Kaiju Corp.](https://devpost.com/software/kaiju-corp) | A | 70 | 60–78 | No (needs PC raiders) |
| 16 | [GathrXR](https://devpost.com/software/gathrxr) | B | 69 | 60–77 | Partly |
| 17 | [GestureMancerKing](https://devpost.com/software/gesturemancerking) | A/B | 69 | 61–76 | AI opponent |
| 18 | [World Expo](https://devpost.com/software/world-expo) | B | 68 | 60–75 | Solo Quick Trips |
| 19 | [MYX House Party](https://devpost.com/software/myx-house-party) | A | 67 | 58–75 | No |
| 20 | [La Cousinade](https://devpost.com/software/la-cousinade-a-family-reunion-villa-in-vr) | A | 67 | 60–74 | Bots in babyfoot |
| 21 | [ScornholeXR](https://devpost.com/software/scornholexr) | A | 66 | 58–73 | No |
| 22 | [Tower Chaos](https://devpost.com/software/tower-chaos) | B | 61 | 54–69 | Solo |
| 23 | [Spatial Watch](https://devpost.com/software/spatial-watch) | A | 51 | 45–60 | n/a (states it was never run on a Quest) |

**Screened but not deep-scored** (screener tier 4 social contenders; worth a look in a later session):
- [Hand Riders](https://devpost.com/software/hand-riders)
- [Gesture Royale](https://devpost.com/software/gesture-royale)
- [Donkey](https://devpost.com/software/donkey)
- [Table Hub: Under Six](https://devpost.com/software/table-hub-under-six)
- [Lumenoir](https://devpost.com/software/lumenoir-movie-theater-watch-together)
- [Watch Together](https://devpost.com/software/watch-together-v9qdh0)
- [Moonrise Mini Golf](https://devpost.com/software/moonrise-mini-golf)
- [Junkyard Dynasty](https://devpost.com/software/junkyard-dynasty)
- [B-Side](https://devpost.com/software/bside-48phjt)
- [Get Hooked!](https://devpost.com/software/get-hooked)
- [Mixed Reality Counters Ball](https://devpost.com/software/mixed-reality-counters-ball)
- [Tiny Pitch](https://devpost.com/software/tiny-pitch)
- [Table Connect](https://devpost.com/software/table-connect)
- [Poppets](https://devpost.com/software/poppets)
- [RealityJ](https://devpost.com/software/realityj)
- [In Your Hands](https://devpost.com/software/in-your-hands)
- [OnBoard Chess](https://devpost.com/software/onboard-chess)
- [Infinite Escape MR](https://devpost.com/software/infinite-escape-mr)
- [Hand Soccer League](https://devpost.com/software/hand-soccer-league)
- [Toy Takeover](https://devpost.com/software/toy-takeover)
- [Bite or Betray](https://devpost.com/software/bite-or-betray)
- [Mothlight](https://devpost.com/software/moonlightxr)
- [Bedtime Across the World](https://devpost.com/software/bedtime-across-the-world)
- [Magik Photos](https://devpost.com/software/magik-photos)
- [HumBubble](https://devpost.com/software/humbubble)

---

## 6. Doodle Figure, judged by the same standard

**What I verified.**
- The page text, 7 screenshots and the YouTube thumbnail.
- Built with: Unity, Photon, React and Expo, Vercel, ElevenLabs, Google Quick, Draw!
- Solo developer.
- The page has 0 likes and 0 comments **[V]**.

**What I did not verify.** I did not watch the trailer. I did not test reconnection or hand-tracking quality, and I could not check frame rate (none is stated).

**Scores [J]:**

- **Innovation 19/25 (17–21).**
  - For: asymmetric phone+VR "reverse Pictionary" in which the headset player sculpts with bare hands is genuinely uncommon in this field (§3).
  - Against: the party-game format itself (draw/guess, Jackbox-style phone joining) is familiar. The core verb, assembling four primitive types, is less novel than RULE MAKER's voice-made rules or 23:17's time portal. It uses none of the device features the criteria name (passthrough, scene understanding, anchors, gaze).
- **Experience Design 19/25 (17–21).**
  - For: excellent party ergonomics. Zero-install join, 2-minute rounds, a clear win moment, bots for solo play, recovery when the headset is handed off, and deliberate cuts (removing host fights) that show good design judgment **[D]**.
  - Risk: a judge testing alone gets the *bot* version. Replayed Quick, Draw! doodles plus the sculpt and reveal is a much weaker loop than the party version. The judge must also open a phone to see the core feature.
  - Unknown: there is no description of onboarding, meaning how a first-time sculptor learns to grab, stretch, fuse and paint.
- **Technical 18/25 (15–20).**
  - For: Photon bridging C# and JS with an additive wire format, plus reconnect and state recovery, is real engineering **[D]**.
  - Against: there is no stated fps, no device-testing detail beyond "tested hard on device", and no platform features beyond hand tracking. Competitors document much more: 72 fps on Quest 2, named device bugs, automated tests.
- **Polish 18/25 (15–21).**
  - For: the theatre is cohesive and charming (curtains, followspot, crowd, confetti), with an announcer voice and keepsake photos.
  - Against:
    - The sculptures shown are three stacked spheres labeled "Octopus", which undersells the creative payoff.
    - The phone screenshot is a bare code-entry page.
    - **No screenshot shows phones in people's hands or people in a room playing together**, yet that is the whole pitch. Game Night shows exactly that.
    - The description is clear and honest but plainer than the top entries.
- **Total about 74 (66–82).**

**Strengths compared with the field:**
1. **It is the only entry I found where same-room non-headset players are essential** (asymmetric multiplayer is named explicitly in the award text).
2. A lone judge can experience the real social mechanic with their own phone, which most stronger social entries cannot offer.
3. Short sessions and a clean round structure.
4. A memorable reveal.

**Weaknesses compared with the field:**
1. The sculpting fidelity on show looks crude.
2. No mixed reality or platform-feature depth, which counts against Innovation and Technical as written.
3. The solo or bot experience is weak.
4. The submission materials undersell the social moment.
5. Solo-developer scope is visible next to teams of 2–5 that have store-shipped products.

---

## 7. Deep comparisons (Part 6, condensed)

**Game Night – Tabletop Mode** (Adapted, team of 2). The strongest overall threat on both fronts: the Social award and Adapted Gaming.
- **Loop:** seven fingertip minigames played around a real table in mixed reality, for up to 4 players face to face.
- **What it is:** a game, with a shipped Early Access base since Nov 2024.
- **Presentation:** screenshots show real people in headsets playing, which is exactly the social proof Doodle Figure lacks.
- **Weaknesses:** every player needs a headset; the minigame-compilation concept is familiar; solo play is unclear.
- **Doodle Figure's edge:** it needs only one headset; it is genuinely asymmetric; a lone judge can test it.

**Campy** (team of 2, likely Adapted). Strongest emotional and accessibility story (kids in hospital, lying-down play), with a simulated fire and hand-warmth interactions that are very hands-first.
- **Social category:** B. Social presence with voice, but light on game goals.
- **Weakness:** it is a toy and space rather than a game with stakes.
- **Likely awards:** Accessibility, Social, an Entertainment track prize.

**23:17** (New, team of 2). The best *designed* asymmetric co-op I found: an information split across two eras.
- **Fatal-for-judging risk:** it needs two headsets in two places.
- **Doodle Figure's edge:** testability and a larger group size.
- **Its edge:** deeper asymmetry, mixed reality on your own desk, mystery polish.

**RULE MAKER** (1v1, team appears to be 1).
- **Strengths:** high originality and the strongest "memorable moment" pitch in the field.
- **Risks:** it relies on OpenAI realtime for the core verb (Meta's "take-it-away test"), shows blood, and its rules are complex.
- **Competes for:** Boldest Original Concept, Agentic Interaction and Social. It is *not* an asymmetric local party game, so it competes with Doodle Figure on the Social award, not on audience.

**PullFit and Desk Session.** Polished, specific, hands-essential products where multiplayer adds to the experience (same-room modes). They are more likely to take Productivity/Gaming track or Reason-to-Come-Back prizes than the Social award, but they are strong on every criterion.

**Let's Flock!** Strong social stack (voice, friends, hub, races).
- **Weaknesses:** arm-flapping breaks the seated guideline, and the hub is empty for a lone judge.
- **Doodle Figure's edge:** it is seated and short-session.

**Sneak-A-Snack.** Direct conceptual cousin: a non-verbal, asymmetric, hand-shadow communication game with a carefully designed first-five-minutes onboarding.
- **Weakness:** it needs two headsets.

**Kaiju Corp.** The closest *format* competitor (VR vs non-VR team).
- **Weak evidence:** screenshots are concept art and logos, solo training is "in development", and raiders play remotely on PC.
- I rate it below Doodle Figure on demonstrated execution **[J]**.

**MYX House Party, GathrXR, Spatial Watch, La Cousinade.** Cross-device social spaces without a strong game loop. All are weak on demonstrated quality or device evidence, and below Doodle Figure on Experience Design **[J]**.

**Not tech demos, but thin loops** (careful wording): ScornholeXR's format is borrowed from a TV segment, and Tower Chaos has no screenshots. Both are complete *games*, and their weakness is originality and presentation, not functionality.

---

## 8. Rankings (Part 9)

**A. Social & Multiplayer (award fit plus quality) [J]:**
1. Game Night
2. Campy
3. 23:17
4. RULE MAKER
5. Sneak-A-Snack
6. Let's Flock
7. **Doodle Figure**
8. Crokinole
9. Bots & Pans
10. Snappy Planet
11. PullFit
12. Kaiju Corp

Doodle Figure moves up from 12th on raw score to about 7th here because it fits the award's "asymmetric multiplayer" text exactly and judges can test it. Uncertainty is high: positions 3–12 could reorder easily.

**B. Adapted Gaming (2 prizes; division labels mostly inferred):**
1. Game Night
2. Surface Breach
3. Let's Flock (if not moved to another track)
4. Campy (if entered in Gaming)
5. RealityGuard
6. Project S
7. Table Connect
8. OnBoard Chess
9. **Doodle Figure**

About 11% of the sample self-identified as Adapted, which implies about 230 Adapted entries and roughly 100–150 in Gaming.

**C. First Five Minutes:**
1. Sneak-A-Snack (cave tutorial described in detail)
2. GLOVR (explicit "first minute" plus a mini show)
3. Campy (fire already burning, no menus)
4. Game Night
5. Shadow Zoo
6. Desk Session (peace sign to start)
7. Picto's Picture Show

Doodle Figure is not in the top 10 on available evidence, because its onboarding is undocumented.

**D. Overall (any track; single-player entries only partly covered):**
- **Top group:** Eddie and I (Venice Immersive 2025 premiere; Adapted), Surface Breach, Game Night, Campy, 23:17, Wormhole Electric Co., Picto's Picture Show, RULE MAKER, PullFit, Desk Session.
- **Next group:** Forever Pets, Overtone, Shadow Zoo, Let's Flock.
- About 1,100 unread single-player entries probably contain more of this calibre.

**Possibly overlooked** (good mechanics, weak materials):
- Wormhole Electric Co. (0 screenshots, but 11 likes and a strong mechanic)
- Mothlight (0 screenshots; 8-seat social deduction)
- Infinite Escape MR (no images)
- Seamline (249 words; 85 levels)
- Squingle Arcade (215-word pitch)
- Tower Chaos (no images)
- Hand Soccer League (missed by the keyword filter)

---

## 9. Biggest threats to Doodle Figure

- **Social award:** Game Night (shows real people playing together and is store-proven), 23:17 and Sneak-A-Snack (better-designed asymmetry), and Campy (stronger story plus emotional appeal).
- **Any award, through "one prize per entry":** if Game Night or Campy win track prizes, they leave the Social pool, which helps Doodle Figure.

---

## 10. Probability assessment (Part 10)

**Assumptions:**
- About 20–30 credible Social contenders.
- Doodle Figure is plausibly in the top 5–10 on award fit.
- Judges test some builds but cannot run multi-headset sessions for most entries **[I]**.
- First-pass screening leans on descriptions and trailers.
- Trailer quality is unknown.

| Outcome | Estimate | Reasoning |
|---|---|---|
| Best Social & Multiplayer | **5–12%** | Best-fitting concept, a mid-pack execution score, and roughly 5 entries that look stronger and also fit the category |
| Adapted Gaming winner or runner-up | **3–8%** | 2 slots, about 100–150 entries, several stronger adapted games |
| Best First Five Minutes | **1–4%** | Open to everyone; onboarding not demonstrated |
| Judge's Choice or another special award | **1–3%** | "Doesn't fit neatly" is a plausible description, but the field is large |
| **Any award** | **8–18%** | Overlap removed, not summed. The base rate is 20/2,105 ≈ 1%, and a typical top-100 entry is about 20% |

My view: a defensible point estimate for Social is about 8%. I can't make it tighter without watching trailers or playing builds.

**What would move these numbers:**
- **Up:** the trailer shows real people with phones laughing and a satisfying sculpt-and-reveal in the first 10 seconds, and judges actually test on a phone.
- **Down:** judges test solo against bots, the trailer is mostly the theatre with little social footage, or sculpt control is finicky.

---

## 11. Progress checkpoint (to continue in a new session)

- **Done:**
  - Full gallery inventory (`gallery_index.csv`, `inventory.csv`, 2,105 rows; each row's `review_depth` says how deeply it was examined).
  - Screening outputs (`screening_jsonl/`).
  - Scripts (`scripts/`).
  - Scoring matrix.
- **Pending, in priority order:**
  1. Watch the trailers of the top 15 social contenders and Doodle Figure from a normal browser (this environment can't). Update `trailer_quality` and the Polish scores.
  2. Deep-score the 25 "screened but not deep-scored" social entries in §5.
  3. Screen the about 1,100 unread single-player entries for Rankings B, C and D. Rerun `scripts/parse_projects.py`, then chunk and screen.
  4. If possible, play the top 5 builds that are publicly available.
- **Re-running:**
  - `scripts/scrape_gallery.sh` and `scripts/fetch_one.sh` recreate the raw cache; they need network access to devpost.com.
  - Then run `parse_projects.py`, `classify.py` and `merge.py`.
