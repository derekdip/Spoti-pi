import sys,csv,json,re,os
from bs4 import BeautifulSoup
S=sys.argv[1]
idx=list(csv.DictReader(open(f'{S}/gallery_index.csv')))
out=[]
def has(t,pats): return [p for p in pats if re.search(p,t,re.I)]
for r in idx:
    slug=r['url'].rstrip('/').split('/')[-1]; f=f'{S}/raw/proj/{slug}.html'
    rec=dict(r); rec['slug']=slug; rec['fetched']=os.path.exists(f)
    if not rec['fetched']: out.append(rec); continue
    s=BeautifulSoup(open(f).read(),'lxml')
    rec_bw=';'.join(x.get_text(strip=True) for x in s.select('#built-with li, #built-with .cp-tag'))
    d=s.select_one('#app-details-left')
    desc=''
    if d:
        bw=d.select_one('#built-with'); 
        if bw: bw.extract()
        desc=d.get_text('\n',strip=True)
    rec['desc']=desc
    rec['built_with']=rec_bw
    vids=[i['src'] for i in s.select('iframe') if 'youtube' in i.get('src','') or 'vimeo' in i.get('src','')]
    rec['video']=vids[0] if vids else ''
    m=re.search(r'embed/([\w-]{11})',rec['video']); rec['yt_id']=m.group(1) if m else ''
    rec['team_size']=len(s.select('.software-team-member'))
    rec['team']=';'.join(x.get_text(' ',strip=True) for x in s.select('.software-team-member .user-profile-link, .software-team-member a.user-profile-link'))[:200]
    rec['images']=';'.join(a.get('href') for a in s.select('#gallery a[data-lightbox], #gallery a') if a.get('href','').startswith('http'))[:2000]
    rec['links']=';'.join(a.get('href') for a in s.select('[data-role="software-urls"] a, .app-links a'))[:500]
    rec['desc_words']=len(desc.split())
    out.append(rec)
json.dump(out,open(f'{S}/projects.json','w'))
print(len(out), sum(1 for x in out if x['fetched']))
