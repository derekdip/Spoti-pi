import json,re,sys,csv
S=sys.argv[1]
d=json.load(open(f'{S}/projects.json'))
def cnt(t,pats): return sum(len(re.findall(p,t,re.I)) for p in pats)
MP=[r'multi-?player',r'\bco-?op\b',r'cooperative',r'\bpvp\b',r'versus',r'asymmetric',r'party game',r'\bfriends?\b',r'together',r'shared (space|presence|session|room|world)',r'co-?located|colocation|co-location',r'\bphoton\b',r'normcore',r'netcode|ngo\b|netcode for gameobjects',r'\bfusion\b',r'\bmirror networking\b',r'spatial anchors? shar|shared spatial anchor',r'lobby|room code|matchmak',r'online',r'players? (join|compete|team)',r'social']
ASYM=[r'asymmetric',r'(phone|browser|mobile|web).{0,40}(join|player|companion|play)',r'(join|play).{0,30}(phone|browser|smartphone)',r'non-?vr (player|friend)',r'without a headset',r'spectator',r'cast(ing)?\b',r'second screen',r'pass the headset']
NET=[r'\bphoton\b',r'normcore',r'netcode',r'\bfusion\b',r'websocket',r'webrtc',r'colyseus',r'mirror',r'firebase',r'multiplayer (building blocks|sdk)',r'shared spatial anchor',r'colocation']
ADAPT=[r'adapted',r'significantly updated',r'significant update',r'existing (game|app|project)',r'previous(ly)? (released|built|version)',r'already (published|released|on the store|live)',r'(published|live|available) on (the )?(meta|horizon|quest) (horizon )?store',r'(new|added) (features?|mode) (during|for) (the|this) (competition|contest)',r'before the competition',r'since september',r'what\'?s new',r'update[sd]? for (this|the) competition',r'changelog']
NEW=[r'new experience',r'built (from scratch|during|in) (the|this|\d+) (competition|weeks?)',r'(eight|8|six|6|seven|7) weeks',r'from scratch']
PROD=[r'productivity',r'workspace',r'task',r'focus',r'meditat',r'habit',r'routine',r'note',r'calendar',r'learn',r'fitness|workout|exercise']
ENT=[r'entertainment',r'cinema|movie|film',r'music',r'story|narrative',r'concert',r'video']
GAME=[r'\bgame\b',r'gameplay',r'level',r'score',r'puzzle',r'boss',r'enemy|enemies',r'high ?score']
HT=[r'hand[- ]?track',r'hands[- ]first',r'gesture',r'pinch',r'bare hands',r'no controllers?',r'controller-?free']
for r in d:
    if not r.get('fetched'): continue
    t=(r['title']+' '+r['tagline']+' '+r.get('desc','')+' '+r.get('built_with','').replace(';',' '))
    r['mp_score']=cnt(t,MP); r['asym_score']=cnt(t,ASYM); r['net_score']=cnt(t,NET)
    r['adapt_score']=cnt(t,ADAPT); r['new_score']=cnt(t,NEW)
    r['ht_score']=cnt(t,HT)
    g,e,p=cnt(t,GAME),cnt(t,ENT),cnt(t,PROD)
    r['track_guess']=max([('Gaming',g),('Entertainment',e),('Productivity',p)],key=lambda x:x[1])[0]+' (inferred)'
    r['div_guess']=('Adapted (inferred)' if r['adapt_score']>r['new_score'] else 'New (inferred)' if r['new_score']>0 else 'Unknown')
    mpflag = r['net_score']>0 or re.search(r'multi-?player|co-?op\b|cooperative|asymmetric|\bpvp\b|party game|co-?locat',t,re.I)
    r['mp_flag']=bool(mpflag)
    r['img_count']=len([x for x in r.get('images','').split(';') if x])
json.dump(d,open(f'{S}/projects.json','w'))
f=[r for r in d if r.get('fetched')]
print('fetched',len(f),'mp_flag',sum(r['mp_flag'] for r in f),'asym>0',sum(r['asym_score']>0 for r in f),'net>0',sum(r['net_score']>0 for r in f),'video',sum(bool(r['video']) for r in f))
