# usage: sheet.py S slug  -> downloads gallery images + yt thumb, writes img/<slug>_sheet.jpg
import sys,json,os,urllib.request,io
from PIL import Image,ImageDraw
S,slug=sys.argv[1],sys.argv[2]
d={r['slug']:r for r in json.load(open(f'{S}/projects.json'))}[slug]
urls=[u for u in d.get('images','').split(';') if u][:8]
if d.get('yt_id'): urls=[f"https://i.ytimg.com/vi/{d['yt_id']}/maxresdefault.jpg"]+urls
ims=[]
for u in urls:
    try:
        b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
        im=Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((640,400)); ims.append(im)
    except Exception as e: print('fail',u,e)
if not ims: sys.exit('no images')
cols=3; rows=(len(ims)+cols-1)//cols
W=Image.new('RGB',(cols*650,rows*410),'white'); dr=ImageDraw.Draw(W)
for i,im in enumerate(ims):
    x,y=(i%cols)*650,(i//cols)*410; W.paste(im,(x,y)); dr.text((x+5,y+5),'YT THUMB' if (i==0 and d.get('yt_id')) else f'img{i}',fill='red')
W.save(f'{S}/img/{slug}_sheet.jpg',quality=80); print(f'{S}/img/{slug}_sheet.jpg',len(ims))
