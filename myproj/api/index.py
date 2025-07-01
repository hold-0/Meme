import json
import os
import asyncio
import httpx
from urllib.parse import urlparse, parse_qs

# 환경 변수
TOKEN = os.getenv("KAITO_API_TOKEN")
API_URL = "https://hub.kaito.ai/api/v1/gateway/ai/kol/mindshare/top-leaderboard"

async def fetch_data():
    """API에서 데이터 가져오기"""
    params = {
        "duration": "7d",
        "topic_id": "M",
        "top_n": 100,
        "customized_community": "customized",
        "community_yaps": "true"
    }
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(API_URL, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return []

def get_html(leaders=None, search_user=None, search_term=""):
    """HTML 생성"""
    if search_user:
        # 사용자 상세 페이지
        return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>User Search Result</title>
<style>body{{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;}}
.container{{max-width:800px;margin:0 auto;background:white;border-radius:15px;padding:30px;}}
.header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;margin:-30px -30px 30px;border-radius:15px 15px 0 0;}}
.back{{color:white;text-decoration:none;background:rgba(255,255,255,0.2);padding:10px 20px;border-radius:25px;display:inline-block;margin-top:15px;}}
.user-card{{background:#f8f9fa;border-radius:15px;padding:30px;text-align:center;}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:15px;margin-top:20px;}}
.stat{{background:white;padding:20px;border-radius:10px;text-align:center;}}</style></head>
<body><div class="container">
<div class="header"><h1>🔍 User Search Result</h1><p>Search term: <strong>{search_term}</strong></p>
<a href="/" class="back">← Back to Leaderboard</a></div>
<div class="user-card">
<img src="{search_user.get("icon","")}" style="width:100px;height:100px;border-radius:50%;margin-bottom:20px;" onerror="this.style.display='none'">
<h2>{search_user.get("name","Unknown")}</h2>
<a href="{search_user.get("twitter_user_url","#")}" target="_blank" style="color:#667eea;text-decoration:none;">@{search_user.get("username","Unknown")}</a>
<div style="background:#ffd700;color:#b8860b;padding:8px 16px;border-radius:25px;display:inline-block;margin:20px 0;font-weight:bold;">
🏆 Rank: #{search_user.get("rank","N/A")}</div>
<div class="stats">
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">{search_user.get("mention_count",0)}</div><div>Mentions</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">{search_user.get("follower_count",0):,}</div><div>Followers</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">{(search_user.get("mindshare",0)*100):.2f}%</div><div>Mindshare</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">{search_user.get("community_score",0):.2f}</div><div>Community Score</div></div>
</div></div></div></body></html>'''
    
    # 메인 리더보드 페이지
    leaders_html = ""
    if leaders:
        for leader in leaders[:50]:  # 50명만 표시
            rank = leader.get("rank", "N/A")
            leaders_html += f'''
<div style="display:flex;align-items:center;padding:15px;margin-bottom:10px;background:#f8f9fa;border-radius:10px;border-left:4px solid #667eea;">
<div style="font-size:1.5em;font-weight:bold;color:#495057;min-width:60px;text-align:center;">#{rank}</div>
<img src="{leader.get("icon","")}" style="width:50px;height:50px;border-radius:50%;margin:0 15px;object-fit:cover;" onerror="this.style.display='none'">
<div style="flex:1;">
<div style="font-weight:bold;color:#495057;">{leader.get("name","Unknown")}</div>
<a href="{leader.get("twitter_user_url","#")}" target="_blank" style="color:#667eea;text-decoration:none;">@{leader.get("username","Unknown")}</a>
</div>
<div style="text-align:center;padding:10px;background:white;border-radius:8px;min-width:80px;margin-left:10px;">
<div style="font-weight:bold;">{leader.get("mention_count",0)}</div>
<div style="font-size:0.8em;color:#6c757d;">Mentions</div>
</div>
<div style="text-align:center;padding:10px;background:white;border-radius:8px;min-width:80px;margin-left:10px;">
<div style="font-weight:bold;">{(leader.get("mindshare",0)*100):.2f}%</div>
<div style="font-size:0.8em;color:#6c757d;">Mindshare</div>
</div>
</div>'''
    else:
        leaders_html = '<div style="text-align:center;padding:40px;color:#6c757d;">Loading data...</div>'
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Kaito AI KOL Leaderboard</title>
<style>body{{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;}}
.container{{max-width:1000px;margin:0 auto;background:white;border-radius:15px;}}
.header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;border-radius:15px 15px 0 0;}}
.search{{padding:20px;background:#f8f9fa;text-align:center;}}
.search input{{padding:12px;border:2px solid #ddd;border-radius:8px;font-size:16px;width:250px;margin-right:10px;}}
.search button{{padding:12px 24px;background:#667eea;color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;}}</style></head>
<body><div class="container">
<div class="header"><h1>🏆 Kaito AI KOL Leaderboard</h1><p>Top influencers in crypto community</p></div>
<div class="search">
<input type="text" id="searchInput" placeholder="Search username (e.g. wanghebbf)">
<button onclick="searchUser()">Search</button>
</div>
<div style="padding:20px;">{leaders_html}</div>
</div>
<script>
function searchUser(){{
const username=document.getElementById('searchInput').value.trim();
if(username)window.location.href=`/search/${{encodeURIComponent(username)}}`;
}}
document.getElementById('searchInput').addEventListener('keypress',function(e){{
if(e.key==='Enter')searchUser();
}});
</script></body></html>'''

def handler(event, context):
    """Vercel 핸들러 함수"""
    try:
        # HTTP 메서드와 경로 파싱
        path = event.get('rawPath', event.get('path', '/'))
        
        # 데이터 가져오기
        leaders = asyncio.run(fetch_data())
        
        if path.startswith('/search/'):
            # 사용자 검색
            username = path.split('/search/')[-1]
            found_user = None
            
            for leader in leaders:
                if leader.get("username", "").lower() == username.lower():
                    found_user = leader
                    break
            
            if found_user:
                html = get_html(search_user=found_user, search_term=username)
            else:
                # 사용자 못 찾음
                html = f'''<!DOCTYPE html><html><head><title>User Not Found</title></head>
<body style="font-family:Arial;padding:50px;text-align:center;">
<h1>❌ User not found</h1><p>Username "{username}" is not in the leaderboard.</p>
<a href="/" style="color:#667eea;">← Back to Leaderboard</a></body></html>'''
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': html
            }
        
        elif path == '/debug':
            # 디버그 정보
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'token_exists': bool(TOKEN),
                    'data_count': len(leaders),
                    'first_user': leaders[0] if leaders else None
                })
            }
        
        else:
            # 메인 페이지
            html = get_html(leaders=leaders)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': html
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error: {str(e)}</h1>'
        }