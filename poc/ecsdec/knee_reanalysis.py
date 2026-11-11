"""Re-analysis of the recorded long LoRA fits (ED4, ED5, ED6 pilot, the PyTorch cross-check).
Exploratory and after the fact: no new training, nothing here was predicted before it was computed.
Usage: python3 poc/ecsdec/knee_reanalysis.py [results_dir]   (default poc/results)
Parts: (1) per-condition knee, mean real share to the knee, gap at the knee;
(2) collapse: spread of test gain across matrices at matched training gain vs matched step;
(3) cheaper cross-fits (one matrix, two half-fits) against the median of eight, and the best common gain;
(4) at 8 contexts: the rule on all 8 against stopping on a 4+4 split, in nats of test gain."""
import sys, json, collections, numpy as np; RES = sys.argv[1] if len(sys.argv) > 1 else "poc/results"; R = RES
print("## (1) knee, share and gap per condition")
fits = []  # (source, cond, module, curve dict)
def add(src, cond, mods):
    for m, c in mods.items():
        if 'te' in c and 'tr' in c and len(c['te']) > 3: fits.append((src, cond, m, c))
def rows(p):
    d = json.load(open(f"{R}/{p}")); return d['rows'] if isinstance(d, dict) else d
for p in ['ed4/ed4.json', 'ed4/pilot2.json', 'ed4/pilot3.json']:
    for r in rows(p):
        if r.get('kind') == 'stopping' or 'traj' in r:
            if r.get('kind','stopping')=='stopping' and 'traj' in r: add(p.split('/')[0]+'/'+p.split('/')[1][:-5], r['name'], r['traj'])
for p, tag in [('ed5/ed5.json','ed5'), ('ed5/pilot.json','ed5pilot'), ('ed6/pilot/rows.json','ed6pilot'), ('ed6/xcheck_gpt2/rows.json','xcheck')]:
    for r in rows(p): add(tag, r['name'], r['full'])
out = []
for src, cond, m, c in fits:
    tr, te = np.array(c['tr']), np.array(c['te']); st = np.array(c['step']); nm = np.array(c.get('norm', [np.nan]*len(st)))
    gtr, gte = tr[0]-tr, te[0]-te
    k = int(np.argmax(gte))
    e = min(3, len(st)-1)  # step 30
    out.append(dict(src=src, cond=cond, m=m, step=int(st[k]), T=float(gtr[k]), P=float(gte[k]), ratio=float(gte[k]/gtr[k]),
                    early=float(gte[e]/gtr[e]), norm=float(nm[k]), last=int(st[-1]), interior=bool(k < len(st)-1)))
FITS = out
import collections
g = collections.defaultdict(list)
for o in out: g[(o['src'], o['cond'])].append(o)
cv = lambda x: float(np.std(x)/np.mean(x))
print(f"{'source/cond':32s} n  knee T* (cv)    P/T* (cv)     norm@peak(cv)  step range")
for key, L in g.items():
    T=[o['T'] for o in L]; Q=[o['ratio'] for o in L]; N=[o['norm'] for o in L]
    print(f"{key[0]+' '+key[1]:32s} {len(L)}  {np.mean(T):.2f} ({cv(T):.2f})   {np.mean(Q):.2f} ({cv(Q):.3f})   {np.mean(N):5.1f} ({cv(N):.2f})  {min(o['step'] for o in L)}-{max(o['step'] for o in L)}  {'' if all(o['interior'] for o in L) else 'EDGE'}")
print("\n## (2) collapse")
import json, numpy as np, collections

R = RES
def rows(p):
    d = json.load(open(f"{R}/{p}")); return d['rows'] if isinstance(d, dict) else d
curves = collections.defaultdict(dict)
for p, tag in [('ed4/ed4.json','ed4'),('ed4/pilot3.json','ed4p3'),('ed5/ed5.json','ed5'),('ed6/xcheck_gpt2/rows.json','xcheck'),('ed6/pilot/rows.json','ed6p')]:
    for r in rows(p):
        mods = r.get('full') or (r.get('traj') if r.get('kind')=='stopping' else None)
        if not mods: continue
        for m,c in mods.items():
            tr,te=np.array(c['tr']),np.array(c['te']); curves[(tag,r['name'])][m]=(np.array(c['step']),tr[0]-tr,te[0]-te)
cv=lambda x: float(np.std(x)/abs(np.mean(x)))
print("Collapse: spread of test gain across matrices, at matched training gain vs at matched step")
print(f"{'cond':28s} {'gap@knee mean(cv)':18s} {'sd@tau':>8s} {'sd@step':>8s}")
for key, M in curves.items():
    if len(M)<3: continue
    # gap at knee
    gaps=[]; 
    for m,(s,gt,ge) in M.items():
        k=int(np.argmax(ge)); gaps.append(gt[k]-ge[k])
    tmax=min(gt.max() for s,gt,ge in M.values())*0.95
    taus=np.linspace(0.1,tmax,30)
    A=np.array([np.interp(taus,gt,ge) for s,gt,ge in M.values()])   # tr gain is monotone enough
    smax=min(s[-1] for s,gt,ge in M.values()); steps=np.arange(10,smax+1,10)
    B=np.array([np.interp(steps,s,ge) for s,gt,ge in M.values()])
    # relative spread: sd across matrices / mean peak gain
    pk=np.mean([ge.max() for s,gt,ge in M.values()])
    print(f"{key[0]+' '+key[1]:28s} {np.mean(gaps):.2f} ({cv(gaps):.2f})        {A.std(0).mean()/pk:8.3f} {B.std(0).mean()/pk:8.3f}")
print("\n## (3) cheaper cross-fits")
import json, numpy as np, collections
R = RES
def rows(p):
    d=json.load(open(f"{R}/{p}")); return d['rows'] if isinstance(d,dict) else d
conds={}  # name -> (full: {m:(gt,ge,steps)}, half: [(m,knee,steps_to_knee)])
def curve(c):
    tr,te=np.array(c['tr']),np.array(c['te']); return tr[0]-tr, te[0]-te, np.array(c['step'])
def hknee(c):
    k=int(np.argmin(c['ho'])); return c['tr'][0]-c['tr'][k], c['step'][-1]
for p,tag in [('ed5/ed5.json','ed5'),('ed6/xcheck_gpt2/rows.json','xcheck')]:
    for r in rows(p):
        full={m:curve(c) for m,c in r['full'].items()}
        half=[(name.split(' ',3)[-1],)+hknee(c) for name,c in r['half'].items()]
        conds[tag+' '+r['name']]=(full,half)
# ED4: full from ed4.json stop rows, halves from knee_check_scored
kc=json.load(open(f"{R}/ed4/knee_check_scored.json"))
for r in rows('ed4/ed4.json'):
    if r.get('kind')!='stopping': continue
    full={m:curve(c) for m,c in r['traj'].items()}
    half=[(h['module'],h['knee_gain'],h['traj']['step'][-1]) for h in kc if h['cond']==r['name']]
    conds['ed4 '+r['name']]=(full,half)
def kept(gt,ge,g):
    pk=ge.max()
    if not (gt>=g).any(): return ge[-1]/pk
    i=int(np.argmax(gt>=g))
    if i==0: return 0.0
    w=(g-gt[i-1])/(gt[i]-gt[i-1]); return (ge[i-1]+w*(ge[i]-ge[i-1]))/pk
for name,(full,half) in conds.items():
    mods=sorted(set(h[0] for h in half))
    def score(g): return [kept(*full[m][:2],g) for m in full]
    allk=[h[1] for h in half]; cost_all=sum(h[2] for h in half)
    s=score(np.median(allk))
    print(f"\n{name}: {len(half)} half-fits; median-of-all g*={np.median(allk):.2f} kept mean {np.mean(s):.3f} min {min(s):.2f}  cost {cost_all} half-steps")
    for m in mods:
        ks=[h[1] for h in half if h[0]==m]; c=sum(h[2] for h in half if h[0]==m); s=score(np.mean(ks))
        print(f"   only {m:42s} g*={np.mean(ks):.2f} kept mean {np.mean(s):.3f} min {min(s):.2f}  cost {c}")
    # oracle shared tau: best single g for all matrices
    gs=np.linspace(0.3,3,271); best=max(gs,key=lambda g:np.mean(score(g)))
    print(f"   oracle common g={best:.2f} kept mean {np.mean(score(best)):.3f} min {min(score(best)):.2f}")
print("\n## (4) rule against a 4+4 split, ED4 at 8 contexts")
import json, numpy as np
R = RES
full={r['name']:r for r in json.load(open(f'{R}/ed4/ed4.json'))['rows'] if r.get('kind')=='stopping'}
kc=json.load(open(f'{R}/ed4/knee_check_scored.json'))
def at_gain(c,g):
    gt=c['tr'][0]-np.array(c['tr']); ge=c['te'][0]-np.array(c['te'])
    i=int(np.argmax(gt>=g)) if (gt>=g).any() else len(gt)-1
    if i==0: return 0.0
    w=min(1,(g-gt[i-1])/(gt[i]-gt[i-1])); return ge[i-1]+w*(ge[i]-ge[i-1])
for cond,r in full.items():
    H=[h for h in kc if h['cond']==cond]; gstar=float(np.median([h['knee_gain'] for h in H]))
    print(f"\n{cond}  g*={gstar:.2f}   test gain in nats (same 96 test contexts)")
    print(f"  {'matrix':8s} {'rule, n=8':>10s} {'holdout 4+4 (A->B, B->A)':>26s} {'full-8 peak':>12s}")
    for m,c in r['traj'].items():
        hs=[h for h in H if h['module']==m]
        ho=[ (h['traj']['te'][0]-h['traj']['te'][int(np.argmin(h['traj']['ho']))]) for h in hs]
        te=np.array(c['te']); print(f"  {m:8s} {at_gain(c,gstar):10.3f} {" ".join(f"{x:8.3f}" for x in ho):>26s}      {te[0]-te.min():8.3f}")
