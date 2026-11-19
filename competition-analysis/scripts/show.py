import sys,json
S=sys.argv[1]; d={r['slug']:r for r in json.load(open(f'{S}/projects.json'))}
for slug in sys.argv[2:]:
    r=d[slug]; print('#'*10,r['title'],r['url'],'| team',r.get('team_size'),'| likes',r['likes'],'| imgs',r.get('img_count'),'| yt',r.get('yt_id'),'| words',r.get('desc_words'))
    print('TAG:',r['tagline']); print('BUILT:',r.get('built_with')); print(r.get('desc','')[:1700]); print()
