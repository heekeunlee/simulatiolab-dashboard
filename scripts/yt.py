# 유튜브 공개 피드(키 필요 없음)에서 조회수·좋아요만 받아 yt.json 으로 저장
import json, re, urllib.request
from datetime import datetime, timezone, timedelta
CH = 'UCjTsqCOK6Bf1aVPx_mXgPig'
x = urllib.request.urlopen(urllib.request.Request(f'https://www.youtube.com/feeds/videos.xml?channel_id={CH}', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode()
un = lambda s: s.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
vs = []
for e in re.findall(r'<entry>(.*?)</entry>', x, re.S):
    g = lambda p: (re.search(p, e) or [None, None])[1]
    vs.append({'id': g(r'<yt:videoId>(.*?)<'), 'title': un(g(r'<title>(.*?)<') or ''), 'published': g(r'<published>(.*?)<'),
               'views': int(g(r'views="(\d+)"') or 0), 'likes': int(g(r'starRating count="(\d+)"') or 0)})
if vs:
    json.dump({'updated': datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M'), 'videos': vs}, open('yt.json', 'w'), ensure_ascii=False, indent=1)
print(len(vs), 'videos')
