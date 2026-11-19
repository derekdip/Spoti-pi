import sys,json,urllib.request,io
from PIL import Image,ImageDraw
S=sys.argv[1]; out=sys.argv[2]; slugs=sys.argv[3:]
D={r['slug']:r for r in json.load(open(f'{S}/projects.json'))}
W=Image.new('RGB',(4*420,len(slugs)*250),'white'); dr=ImageDraw.Draw(W)
for i,s in enumerate(slugs):
    d=D[s]; urls=([f"https://i.ytimg.com/vi/{d['yt_id']}/maxresdefault.jpg"] if d.get('yt_id') else [])+[u for u in d['images'].split(';') if u][:3]
    for j,u in enumerate(urls[:4]):
        try:
            im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read())).convert('RGB')
            if im.size[0]<200: im=Image.new('RGB',(400,225),'gray')
            im.thumbnail((410,240)); W.paste(im,(j*420,i*250))
        except Exception as e: pass
    dr.rectangle((0,i*250,len(d['title'])*7+60,i*250+14),fill='black'); dr.text((3,i*250+1),d['title']+(' [YT]' if d.get('yt_id') else ''),fill='yellow')
W.save(out,quality=78); print(out)
