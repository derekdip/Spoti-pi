import sys,glob,csv,re
from bs4 import BeautifulSoup
D,out=sys.argv[1],sys.argv[2]
rows={};order=[]
for p in range(1,89):
    s=BeautifulSoup(open(f'{D}/p{p}.html').read(),'lxml')
    for a in s.select('a.link-to-software'):
        u=a['href'].split('?')[0]
        title=(a.select_one('h5') or a).get_text(' ',strip=True)
        tag=a.select_one('p.tagline'); tag=tag.get_text(' ',strip=True) if tag else ''
        winner=bool(a.select_one('.winner'))
        likes=a.select_one('.like-count'); cm=a.select_one('.comment-count')
        thumb=a.select_one('img'); thumb=thumb.get('src') if thumb else ''
        if u in rows: continue
        rows[u]=dict(gallery_page=p,title=title,url=u,tagline=tag,likes=likes.get_text(strip=True) if likes else '',comments=cm.get_text(strip=True) if cm else '',thumb=thumb)
        order.append(u)
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[order[0]].keys())); w.writeheader()
    for u in order: w.writerow(rows[u])
print(len(order))
