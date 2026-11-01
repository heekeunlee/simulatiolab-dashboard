# 유튜브 공개 정보(키 필요 없음)로 조회수·좋아요·구독자를 받아 yt.json 저장 + history.json 에 시간별 기록을 쌓는다.
import json, os, re, urllib.request
from datetime import datetime, timezone, timedelta
CH = 'UCjTsqCOK6Bf1aVPx_mXgPig'
KST = timezone(timedelta(hours=9))
UA = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9'}
import time
def get(u, tries=8):   # 유튜브 피드가 가끔 404·500을 돌려줘서 몇 번 다시 시도한다
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode('utf-8', 'ignore')
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(6)
un = lambda s: s.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')

def num(t):
    t = t.replace(',', '')
    m = re.match(r'([\d.]+)([KM]?)', t)
    return int(float(m.group(1)) * {'': 1, 'K': 1e3, 'M': 1e6}[m.group(2)]) if m else None

vs = []
try:
    x = get(f'https://www.youtube.com/feeds/videos.xml?channel_id={CH}')
except Exception as e:
    print('feed 실패 → 영상 페이지에서 읽기:', e); x = ''
for e in re.findall(r'<entry>(.*?)</entry>', x, re.S):
    g = lambda p: (re.search(p, e) or [None, None])[1]
    vs.append({'id': g(r'<yt:videoId>(.*?)<'), 'title': un(g(r'<title>(.*?)<') or ''), 'published': g(r'<published>(.*?)<'),
               'views': int(g(r'views="(\d+)"') or 0), 'likes': int(g(r'starRating count="(\d+)"') or 0)})

old = json.load(open('yt.json')) if os.path.exists('yt.json') else {}
# 피드가 안 될 때(2026-11-01 유튜브 쪽 404·500이 잦음): 아는 영상 ID마다 영상 페이지의 공개 숫자(조회·좋아요)를 읽는다
if not vs:
    known = {v['id']: v for v in old.get('videos', [])}
    try:
        for sh in json.load(open('data.json')).get('shorts', []):
            if sh.get('youtube') and sh['youtube'] not in known: known[sh['youtube']] = {'id': sh['youtube'], 'title': sh.get('title') or '', 'published': None}
    except Exception: pass
    for vid, pv in known.items():
        try:
            w = get(f'https://www.youtube.com/watch?v={vid}', tries=3)
            g = lambda p: (re.search(p, w) or [None, None])[1]
            views, likes = g(r'"viewCount":"(\d+)"'), g(r'"likeCount":"(\d+)"')
            if views is None: raise ValueError('no viewCount')
            pub = pv.get('published') or g(r'"publishDate":"([^"]+)"')
            vs.append({'id': vid, 'title': pv.get('title') or un(g(r'<meta name="title" content="([^"]*)"') or ''), 'published': pub, 'views': int(views), 'likes': int(likes or pv.get('likes') or 0)})
        except Exception as e:
            print('영상 페이지 실패', vid, e)
            if pv.get('views') is not None: vs.append(pv)
    vs.sort(key=lambda v: v.get('published') or '', reverse=True)
    print('영상 페이지로 읽음:', len(vs))
ch = {'subscribers': (old.get('channel') or {}).get('subscribers')}
try:
    c = get('https://www.youtube.com/@simulatiolab')
    s = re.search(r'([\d.,]+[KM]?) subscribers?', c)
    if s: ch['subscribers'] = num(s.group(1))
except Exception as e:
    print('channel page 실패:', e)

now = datetime.now(KST)
if vs:
    json.dump({'updated': now.strftime('%Y-%m-%d %H:%M'), 'channel': ch, 'videos': vs}, open('yt.json', 'w'), ensure_ascii=False, indent=1)
    h = json.load(open('history.json')) if os.path.exists('history.json') else []
    h.append({'t': now.strftime('%Y-%m-%dT%H:%M'), 's': ch.get('subscribers'), 'v': {x['id']: x['views'] for x in vs}, 'l': {x['id']: x['likes'] for x in vs}})
    json.dump(h[-24 * 120:], open('history.json', 'w'), separators=(',', ':'))
print(len(vs), 'videos', ch)
