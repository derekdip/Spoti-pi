import json,csv,glob,sys,re
S=sys.argv[1]
d=json.load(open(f'{S}/projects.json'))
cls={}
for f in sorted(glob.glob(f'{S}/out/mp_*.jsonl'))+sorted(glob.glob(f'{S}/out/sample_*.jsonl')):
    src='mp-screen' if '/mp_' in f else 'sample'
    for line in open(f):
        line=line.strip()
        if not line: continue
        try: o=json.loads(line)
        except: continue
        o['_src']=src
        cls.setdefault(o['slug'],{}).update({k:v for k,v in o.items() if v not in (None,'')})
over={}
try: over={o['slug']:o for o in map(json.loads,open(f'{S}/out/deep.jsonl'))}
except FileNotFoundError: pass
F=['project_name','devpost_url','gallery_page','track','division','genre','multiplayer','multiplayer_category','multiplayer_type','non_vr_participants','hand_tracking','platforms','gameplay_loop','unique_mechanic','working_features_evidence','planned_features','hardware_testing','trailer_available','trailer_quality','technical_maturity_tier','competition_relevance','confidence','review_depth','team_size','screenshots','likes','built_with','notes']
def plat(r):
    t=(r.get('desc','')+' '+r.get('built_with','')).lower(); p=[]
    if re.search(r'quest|meta vr|horizon',t): p.append('Quest')
    if re.search(r'webxr|iwsdk|browser|three\.js',t): p.append('WebXR/browser')
    if re.search(r'pcvr|pc vr|steamvr',t): p.append('PCVR')
    if re.search(r'\bphone|mobile|ios|android app',t): p.append('phone(mentioned)')
    return ';'.join(p) or 'unknown'
def hw(r):
    t=r.get('desc','')
    m=re.findall(r'quest ?3s|quest ?3|quest ?2|quest pro|xr simulator|iwer|emulator',t,re.I)
    return ';'.join(sorted(set(x.lower() for x in m))) or 'not stated'
def planned(r):
    t=r.get('desc',''); i=t.lower().find("what's next")
    return re.sub(r'\s+',' ',t[i:i+220]) if i>=0 else 'not stated'
rows=[]
for r in d:
    c=cls.get(r['slug'],{}); o=over.get(r['slug'],{})
    get=lambda k,default='unknown': o.get(k, c.get(k, default))
    cat=get('mp_cat','not screened' if not (r['mp_flag'] or r['asym_score']>=2 or r['mp_score']>=4) else 'unknown')
    rows.append({
     'project_name':r['title'],'devpost_url':r['url'],'gallery_page':r['gallery_page'],
     'track':get('track',r.get('track_guess','unknown')),'division':get('division',r.get('div_guess','unknown')),
     'genre':get('genre'),'multiplayer':('no' if cat=='none' else 'yes' if cat in 'ABCD' and cat else 'keyword-negative (not read)' if cat=='not screened' else 'unclear'),
     'multiplayer_category':cat,'multiplayer_type':get('mp_type','n/a'),'non_vr_participants':get('non_vr_participants','unknown'),
     'hand_tracking':get('hand_tracking'),'platforms':plat(r),'gameplay_loop':get('loop'),'unique_mechanic':get('unique'),
     'working_features_evidence':get('evidence','not assessed'),'planned_features':planned(r),'hardware_testing':hw(r),
     'trailer_available':'yes ('+('YouTube' if r.get('yt_id') else 'Vimeo' if 'vimeo' in r.get('video','') else 'other')+')' if r.get('video') else 'no',
     'trailer_quality':o.get('trailer_quality','NOT WATCHED (YouTube blocked from research environment)'),
     'technical_maturity_tier':get('tier','not assessed'),
     'competition_relevance':o.get('competition_relevance', ('Social&MP contender' if c.get('social_contender') else '')+(' | party/asym competitor' if c.get('party_asym_competitor') else '')),
     'confidence':o.get('confidence','low (description only)' if c else 'not assessed'),
     'review_depth':o.get('review_depth', 'description screened ('+c.get('_src','')+')' if c else 'metadata+keyword only'),
     'team_size':r['team_size'],'screenshots':r['img_count'],'likes':r['likes'],
     'built_with':';'.join(dict.fromkeys(r['built_with'].split(';')))[:250],'notes':get('notes','')})
with open(f'{S}/inventory.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F); w.writeheader(); w.writerows(rows)
print(len(rows),'rows;',sum(1 for x in rows if x['review_depth'].startswith('description')),'screened')
