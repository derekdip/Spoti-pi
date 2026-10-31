"""Drawing bots on one shared canvas, and the room they leave when people arrive (docs/doodle-bots.md).

A round: one word, one canvas, several bots. The shared plan is a variation of the word from the bank
(a list of strokes in order) and a frame (where on the canvas the figure goes, and how big). No bot
knows the frame; each holds a belief about it, wrong by an amount set by its skill, and a team bot
corrects its belief from what is already on the canvas, by as much as its stubbornness allows. That one
mechanism gives the collaboration and the chaos: a good team converges on the first stroke's frame
(whoever drew first decides where the house is), a stubborn bot puts the roof where it believes the
house is, and a bot with its own plan draws a second house over the first.

Behaviours: team (draws the shared plan's next unclaimed stroke), solo (its own variation of the word,
in its own frame), misheard (its own variation of another word), plus two traits any bot can have:
copycat (retraces a stroke someone just drew) and fixer (redraws another bot's stroke where its own
belief says the stroke should be). A chaos level in [0, 1] sets how many bots are not team, how wrong
the beliefs start, and how stubborn they are.

The room: the game's room holds 8, one VR player and 7 web players; bots fill the web seats up to a
target when few people are present, and a bot leaves, at the end of its current stroke, whenever a
person joins and the web seats would be within one of full. Bots never block a person.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from .bank import bbox, BOX
from .edits import variation
from .hand import PERSONAS, execute_stroke, TRAVEL

CANVAS = (640.0, 420.0)
EXTRAS = 2              # details added to a finished plan, per round, at most
CALLOUTS = 3            # foreign strokes a team bot calls out per round before it gives up
SCRIBBLES = 2           # strokes a fixer scribbles out per round, at most
NAMES = ["Pip", "Mo", "Zed", "Lou", "Kit", "Bea", "Ash", "Rue", "Tam", "Jo"]
COLORS = ["#1e7b73", "#c0552b", "#5b4fb8", "#b8892f", "#a3326f", "#2f7fb8", "#5f8a2f", "#8a4a2f", "#2f8a7a", "#7a2f8a"]
LINES = dict(claim=["{part}!", "I'll do this bit", "on it", "mine", "watch this"], confused=["wait, where is it?", "is that the {word}?", "hm", "which way is up?", "ok ok"],
             fix=["that's not where it goes", "let me fix that", "no no, like this", "moving it"], copy=["same", "like that?", "me too", "copying you"],
             solo=["I'll just draw my own", "doing it my way", "mine's better", "another {word}"], misheard=["{word}? I heard {other}", "oh. {other}, right?", "drawing a {other}"],
             leave=["gotta go, have fun!", "people are here, bye", "I'll make room", "later!"], join=["hi!", "hello everyone", "what are we drawing?", "I'm here"],
             foreign=["hey, what's that?", "who drew that?", "that's not a {word}", "excuse me", "stop that", "not there!"], retreat=["oops", "fine, I'll go over here", "ok ok, my corner", "sorry!"],
             realise=["{word}? oh. {word}!", "ohh, {word}. got it", "wait, {word}? ok joining"], scribble=["nope", "undo!", "that's gone", "fixing this"])
CORNERS = [(105.0, 95.0), (535.0, 95.0), (105.0, 325.0), (535.0, 325.0)]       # where a solo bot does its own thing


@dataclass
class Frame:
    anchor: np.ndarray         # canvas position of the doodle box's centre
    scale: float               # canvas px per doodle px

    def map(self, strokes):
        return [(s - BOX / 2) * self.scale + self.anchor for s in strokes]


@dataclass
class Stroke:
    bot: str
    t: np.ndarray
    xy: np.ndarray
    kind: str                   # plan, extra, solo, misheard, copy, fix, scribble
    source_index: int = -1      # which stroke of the shared plan, for the frame inference and the fixer
    scribbled: bool = False


@dataclass
class Bot:
    name: str
    color: str
    persona: str
    behaviour: str              # team, solo, misheard
    skill: float
    stubborn: float
    copycat: float
    fixer: float
    belief: Frame = None
    own_plan: list = None       # for solo and misheard
    own_word: str = ""
    own_next: int = 0
    free_at: float = 0.0
    last_xy: np.ndarray = None
    strokes: int = 0
    leaving: bool = False
    bubbles: list = field(default_factory=list)
    noticed: set = field(default_factory=set)      # foreign strokes this team bot has called out
    called_out: int = 0                            # times this non-team bot was called out or scribbled over
    in_corner: bool = False

    def say(self, t, kind, **kw):
        line = LINES[kind][int(hash((self.name, len(self.bubbles))) % len(LINES[kind]))].format(**kw)
        self.bubbles.append((float(t), line))


def make_bots(n, chaos, rng, personas=None):
    """n bots at a chaos level: the share that is not team, their initial frame error and stubbornness."""
    names = list(rng.permutation(NAMES)[:n]); bots = []
    for i, nm in enumerate(names):
        r = rng.random(); p_off = 0.6 * chaos ** 2             # the share that is not team: 1 percent at chaos 0.15, 15 at 0.5, 43 at 0.85
        behaviour = "team" if r > p_off else ("solo" if r > p_off / 3 else "misheard")
        if i == 0:
            behaviour = "team"                      # someone has to start the figure
        skill = float(np.clip(rng.normal(0.8 - 0.6 * chaos, 0.15), 0.05, 1.0))
        bots.append(Bot(nm, COLORS[i % len(COLORS)], personas[i % len(personas)] if personas else str(rng.choice(list(PERSONAS))), behaviour, skill,
                        stubborn=float(np.clip(rng.normal(0.2 + 0.6 * chaos, 0.2), 0.0, 1.0)), copycat=float(0.25 * chaos * rng.random()), fixer=float(0.35 * chaos * rng.random())))
    return bots


def team_box(canvas, margin=20.0):
    """The box the team's figure occupies so far, grown by a margin; None before the first stroke."""
    pts = [s.xy for s in canvas if s.kind in ("plan", "extra", "fix")]
    if not pts:
        return None
    a = np.concatenate(pts, 0); return a.min(0) - margin, a.max(0) + margin


def inside(box, xy):
    if box is None:
        return False
    c = xy.mean(0); return bool(np.all(c >= box[0]) and np.all(c <= box[1]))


def scribble_over(xy, rng):
    """A zigzag across a stroke's box: the fixer's undo."""
    lo, hi = xy.min(0) - 4, xy.max(0) + 4; n = int(rng.integers(3, 6)); pts = []
    for i in range(n + 1):
        x = lo[0] + (hi[0] - lo[0]) * i / n; pts.append([x, lo[1] if i % 2 == 0 else hi[1]])
    return np.array(pts, float)


def far_corner(anchor, rng, scale):
    """A frame in the canvas corner farthest from an anchor, at a smaller scale."""
    c = max(CORNERS, key=lambda c_: np.linalg.norm(np.array(c_) - anchor))
    return Frame(np.array(c, float) + rng.uniform(-15, 15, 2), scale * rng.uniform(0.5, 0.7))


def transplant(plan, donor, rng):
    """A stroke of the donor doodle that the plan does not have (the farthest, in where it sits and how
    big it is, from every plan stroke), mapped into the plan's box: a detail to add."""
    from .edits import _descriptor
    lo_p, hi_p = bbox(plan); lo_d, hi_d = bbox(donor); sp = np.maximum(hi_p - lo_p, 1.0); sd = np.maximum(hi_d - lo_d, 1.0)
    dp = [_descriptor(s, lo_p, sp) for s in plan]
    gaps = [min(np.linalg.norm(_descriptor(s, lo_d, sd) - d) for d in dp) for s in donor]
    j = int(np.argmax(gaps)) if rng.random() < 0.7 else int(rng.integers(len(donor)))
    return (donor[j] - lo_d) / sd * sp + lo_p


def infer_frame(plan, canvas_strokes, own_scale):
    """The frame the canvas implies: the shared plan's drawn strokes (in doodle coordinates) against
    where they were drawn. One stroke fixes the anchor (the second person aligns to the first); the
    scale needs two or more strokes and is the bot's own belief until then."""
    drawn = [s for s in canvas_strokes if s.kind == "plan" and s.source_index >= 0]
    if len(drawn) < 1:
        return None
    src = np.concatenate([plan[s.source_index] for s in drawn], 0); dst = np.concatenate([s.xy for s in drawn], 0)
    lo_s, hi_s = src.min(0), src.max(0); lo_d, hi_d = dst.min(0), dst.max(0)
    size_s = np.maximum(hi_s - lo_s, 8.0); size_d = np.maximum(hi_d - lo_d, 8.0)
    scale = float(np.clip(np.mean(size_d / size_s), 0.4, 2.5)) if len(drawn) > 1 else own_scale
    anchor = (lo_d + hi_d) / 2 - ((lo_s + hi_s) / 2 - BOX / 2) * scale
    return Frame(anchor, scale)


def run_round(word, bank, bots, chaos, rng, duration=45.0, t0=0.0, frame=None):
    """Simulate one round. Returns the canvas strokes (in drawing order) and the frame the plan used."""
    shareable = lambda w: [d for d in bank[w] if len(d) >= 4] or bank[w]       # a plan worth sharing has parts
    plan = variation(shareable(word), rng, p_drop=0.0)
    # the details: the plan's own minor strokes, held back to be added once the figure stands (coherent
    # by construction); at real chaos a bot may add a stroke from a different doodle instead
    from .edits import drop_minor
    details = []
    for _ in range(EXTRAS):
        fewer = drop_minor(plan, rng)
        if len(fewer) < len(plan):
            details.append(next(s for s in plan if not any(s is f for f in fewer))); plan = fewer
    plan = plan + details; n_core = len(plan) - len(details)
    frame = frame or Frame(np.array([CANVAS[0] / 2 + rng.uniform(-40, 40), CANVAS[1] / 2 + rng.uniform(-25, 25)]), rng.uniform(1.0, 1.25))
    claimed = {}; canvas = []
    for b in bots:
        err = (1.0 - b.skill) * np.array([rng.uniform(-110, 110), rng.uniform(-70, 70)])
        b.belief = Frame(frame.anchor + err, frame.scale * float(np.clip(rng.normal(1.0, 0.35 * (1 - b.skill)), 0.5, 1.8)))
        b.own_next = 0; b.strokes = 0; b.free_at = t0 + rng.uniform(0.3, 2.5); b.last_xy = None
        b.noticed = set(); b.called_out = 0; b.in_corner = False
        if b.behaviour == "solo":
            b.own_word = word; b.own_plan = variation(shareable(word), rng); b.say(b.free_at, "solo", word=word)
            b.belief = far_corner(b.belief.anchor, rng, frame.scale); b.in_corner = True     # a solo bot takes a corner and does its own thing
        elif b.behaviour == "misheard":
            others = [w for w in bank if w != word]; b.own_word = str(rng.choice(others)); b.own_plan = variation(shareable(b.own_word), rng); b.say(b.free_at, "misheard", word=word, other=b.own_word)
    t_end = t0 + duration
    while True:
        active = [b for b in bots if not b.leaving and b.free_at < t_end]
        if not active:
            break
        b = min(active, key=lambda x: x.free_at); t = b.free_at
        # the team bot looks at the canvas and corrects its belief
        if b.behaviour == "team":
            inf = infer_frame(plan, canvas, b.belief.scale)
            if inf is not None:
                w = (1.0 - b.stubborn) * 0.7
                b.belief = Frame(b.belief.anchor + w * (inf.anchor - b.belief.anchor), b.belief.scale + w * (inf.scale - b.belief.scale))
        action = None
        others = [s for s in canvas if s.bot != b.name]
        box = team_box(canvas)
        if b.behaviour == "team":
            # a foreign stroke inside the team's figure: call it out; a fixer may scribble it out
            foreign = [(i, s) for i, s in enumerate(canvas) if s.kind in ("solo", "misheard") and i not in b.noticed and inside(box, s.xy)]
            if foreign and len(b.noticed) < CALLOUTS:
                i, s = foreign[-1]; b.noticed.add(i)
                culprit = next((x for x in bots if x.name == s.bot), None)
                if culprit is not None: culprit.called_out += 1
                scribbles = sum(1 for x in canvas if x.kind == "scribble" and x.bot == b.name)
                if b.fixer > 0 and scribbles < SCRIBBLES and rng.random() < min(0.6, b.fixer * 3) and not s.scribbled:
                    s.scribbled = True; b.say(t, "scribble"); action = ("scribble", scribble_over(s.xy, rng), -1)
                else:
                    b.say(t, "foreign", word=word)
        elif b.called_out and not b.in_corner and rng.random() < (1.0 - b.stubborn):
            # called out or scribbled over: the misheard bot may realise, the solo bot retreats to a corner
            if b.behaviour == "misheard" and rng.random() < 0.6:
                b.say(t, "realise", word=word); b.behaviour = "team"; b.own_plan = None; b.called_out = 0
            else:
                b.say(t, "retreat"); b.belief = far_corner(b.belief.anchor, rng, frame.scale); b.in_corner = True; b.called_out = 0
        if b.fixer > 0 and others and rng.random() < b.fixer:
            # a stroke of the plan drawn far from where this bot believes it belongs
            for s in reversed(others[-4:]):
                if s.kind == "plan" and s.source_index >= 0:
                    want = b.belief.map([plan[s.source_index]])[0]
                    if np.linalg.norm(want.mean(0) - s.xy.mean(0)) > 28.0:
                        action = ("fix", want, s.source_index); break
        if action is None and b.copycat > 0 and others and rng.random() < b.copycat:
            s = others[-1 - int(rng.integers(min(3, len(others))))]
            action = ("copy", s.xy + (1.0 - b.skill) * rng.uniform(-18, 18, 2), s.source_index)
        if action is None:
            if b.behaviour == "team":
                nxt = next((i for i in range(len(plan)) if i not in claimed), None)
                if nxt is None:
                    # the figure and its details are drawn: at real chaos a bot may still add a stroke
                    # from a different doodle of the word, placed where that doodle had it; else idle, then done
                    extras = sum(1 for s in canvas if s.kind == "extra")
                    if chaos >= 0.4 and extras < EXTRAS and rng.random() < chaos * 0.5:
                        donor = shareable(word)[int(rng.integers(len(shareable(word))))]
                        xy = b.belief.map([transplant(plan, donor, rng)])[0]; action = ("extra", xy, -1)
                        b.say(t, "claim", part=["a chimney", "a window", "a detail", "one more thing", "the door"][int(rng.integers(5))])
                    else:
                        b.free_at = t + rng.uniform(2.0, 5.0)
                        if rng.random() < 0.3 + chaos:
                            continue
                        b.free_at = t_end; continue
                if action is None:
                    claimed[nxt] = b.name; action = ("plan", b.belief.map([plan[nxt]])[0], nxt)
                    if nxt >= n_core and rng.random() < 0.5:
                        b.say(t, "claim", part=["a detail", "one more thing", "a little extra", "the finishing touch"][int(rng.integers(4))])
                if action[0] == "plan" and b.strokes == 0 and b.skill < 0.5:
                    b.say(t, "confused", word=word)
                elif action[0] == "plan" and rng.random() < 0.3:
                    b.say(t, "claim", part=["roof", "the door", "a window", "this line", "the top", "the side", "this part"][nxt % 7])
            else:
                if b.own_next >= len(b.own_plan):
                    b.free_at = t_end; continue
                xy = b.belief.map([b.own_plan[b.own_next]])[0]; action = ("solo" if b.behaviour == "solo" else "misheard", xy, -1); b.own_next += 1
        kind, xy, idx = action
        if kind == "fix": b.say(t, "fix")
        if kind == "copy": b.say(t, "copy")
        travel = (np.linalg.norm(xy[0] - b.last_xy) / TRAVEL) if b.last_xy is not None else 0.0
        ts, pts = execute_stroke(xy, PERSONAS[b.persona], rng, t + travel)
        if ts[-1] > t_end + 2.0:
            b.free_at = t_end; continue
        canvas.append(Stroke(b.name, ts, pts, kind, idx)); b.strokes += 1; b.last_xy = pts[-1]
        b.free_at = ts[-1] + PERSONAS[b.persona]["think"] * rng.uniform(0.4, 1.6)
    return canvas, frame, plan


def canvas_strokes_xy(canvas):
    return [s.xy for s in canvas]


# ---- the room
WEB_SEATS = 7
FILL_TO = 4             # bots fill the room to this many web players when fewer people are present
RESERVE = 1             # seats kept free for people once any person is present


def room_target(humans, fill_to=FILL_TO, reserve=RESERVE, seats=WEB_SEATS):
    """How many bots the room should hold with this many people in it: the bots stay as people arrive
    (company for the first few), and leave one by one once the web seats are within the reserve of
    full, so that a person can always join. With 4 bots and 7 seats: 0 to 2 people keep 4 bots, the
    third person sends one away, and the sixth sends the last."""
    return int(max(0, min(fill_to, seats - reserve - humans)))


def simulate_room(bank, rng, rounds=5, round_s=40.0, arrivals=None, chaos=0.45, seed=0):
    """A session: rounds of drawing while people arrive; bots join and leave by the rule. Returns the
    event log the viewer plays: strokes with times, bubbles, and join/leave events."""
    words = list(bank); arrivals = sorted(arrivals or []); humans = []; bots = make_bots(FILL_TO, chaos, rng)
    roster = {b.name: dict(color=b.color, persona=b.persona, behaviour=b.behaviour, skill=round(b.skill, 2), stubborn=round(b.stubborn, 2)) for b in bots}
    events = [dict(t=0.0, type="join", who=b.name, bot=True, color=b.color) for b in bots]
    strokes, bubbles = [], []
    t = 0.0; arr_i = 0
    for r in range(rounds):
        word = words[r % len(words)]
        # people who arrive during this round
        due = [a for a in arrivals[arr_i:] if a < t + round_s]; arr_i += len(due)
        canvas, frame, plan = run_round(word, bank, bots, chaos, rng, duration=round_s, t0=t)
        for s in canvas:
            strokes.append(dict(bot=s.bot, t=s.t.round(3).tolist(), xy=s.xy.round(1).tolist(), kind=s.kind, round=r))
        for b in bots:
            bubbles += [dict(t=tb, who=b.name, text=tx, round=r) for tb, tx in b.bubbles]; b.bubbles = []
        events.append(dict(t=t, type="word", word=word, round=r))
        for a in due:
            name = f"Guest {int(rng.integers(10, 99))}"; humans.append(name); events.append(dict(t=a, type="join", who=name, bot=False))
            # a bot leaves at the end of its current stroke when the seats are within reserve of full
            while len(bots) > room_target(len(humans)):
                leaver = max(bots, key=lambda b: b.strokes)                      # the bot that has drawn most hands over
                end = max([s["t"][-1] for s in strokes if s["bot"] == leaver.name and s["round"] == r and s["t"][0] <= a] + [a])
                events.append(dict(t=float(end), type="leave", who=leaver.name, bot=True)); bubbles.append(dict(t=float(end), who=leaver.name, text=LINES["leave"][len(events) % 4], round=r))
                bots.remove(leaver); leaver.leaving = True
            # and bots join when the room is emptier than its target (a person left; not simulated here)
        t += round_s + 4.0
    return dict(canvas=CANVAS, seats=WEB_SEATS, fill_to=FILL_TO, reserve=RESERVE, strokes=strokes, bubbles=bubbles, events=events, bots=roster)
