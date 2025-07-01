from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
import os
import json
import asyncio

# 환경 변수에서 API 토큰 가져오기
TOKEN = os.getenv("KAITO_API_TOKEN")
API_URL = "https://hub.kaito.ai/api/v1/gateway/ai/kol/mindshare/top-leaderboard"

app = FastAPI()

# HTML 템플릿 (간소화 버전)
def get_leaderboard_html(leaders=None, error=None):
    leaders_html = ""
    if error:
        leaders_html = f'<div style="padding: 20px; background: #f8d7da; color: #721c24; border-radius: 8px; margin: 20px; text-align: center;"><h3>error</h3><p>{error}</p></div>'
    elif leaders:
        for leader in leaders:
            rank = leader.get("rank", "N/A")
            leaders_html += f'''
            <div style="display: flex; align-items: center; padding: 15px; margin-bottom: 10px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #667eea;">
                <div style="font-size: 1.5em; font-weight: bold; color: #495057; min-width: 60px; text-align: center;">#{rank}</div>
                <img src="{leader.get("icon", "")}" alt="{leader.get("name", "")}" style="width: 60px; height: 60px; border-radius: 50%; margin: 0 15px; border: 3px solid #dee2e6; object-fit: cover;" onerror="this.style.display='none'">
                <div style="flex: 1;">
                    <div style="font-size: 1.1em; font-weight: bold; color: #495057; margin-bottom: 5px;">{leader.get("name", "Unknown")}</div>
                    <a href="{leader.get("twitter_user_url", "#")}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 500;">@{leader.get("username", "Unknown")}</a>
                    <div style="color: #6c757d; font-size: 0.9em; margin-top: 5px; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{leader.get("bio", "")}</div>
                </div>
                <div style="display: flex; gap: 20px;">
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; min-width: 80px;">
                        <div style="font-size: 1.2em; font-weight: bold; color: #495057;">{leader.get("mention_count", 0)}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Mentions</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; min-width: 80px;">
                        <div style="font-size: 1.2em; font-weight: bold; color: #495057;">{leader.get("follower_count", 0):,}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Followers</div>
                    </div>
                </div>
            </div>
            '''
    else:
        leaders_html = '<div style="text-align: center; padding: 40px; color: #6c757d;"><p>data loading...</p></div>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kaito AI KOL Leaderboard</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .search-container {{
                padding: 20px;
                background: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                text-align: center;
            }}
            .search-input {{
                padding: 12px 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                margin-right: 10px;
                width: 300px;
            }}
            .search-btn {{
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 Kaito AI KOL Leaderboard</h1>
                <p>Top influencers in crypto community</p>
            </div>
            <div class="search-container">
                <input type="text" class="search-input" id="searchInput" placeholder="search username (eg. @HodlethKR)">
                <button class="search-btn" onclick="searchUser()">search</button>
            </div>
            <div style="padding: 20px;">
                {leaders_html}
            </div>
        </div>
        <script>
            function searchUser() {{
                const username = document.getElementById('searchInput').value.trim();
                if (username) {{
                    window.location.href = `/search/${{encodeURIComponent(username)}}`;
                }} else {{
                    alert('type username');
                }}
            }}
            document.getElementById('searchInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    searchUser();
                }}
            }});
        </script>
    </body>
    </html>
    '''

def get_user_detail_html(username, user=None, error=None):
    if error:
        content = f'<div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 10px; text-align: center;"><h3>오류 발생</h3><p>{error}</p></div>'
    elif user:
        content = f'''
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; padding: 30px; text-align: center;">
            <img src="{user.get("icon", "")}" alt="{user.get("name", "")}" style="width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 20px; border: 5px solid #dee2e6; object-fit: cover;" onerror="this.style.display='none'">
            <div style="font-size: 1.5em; font-weight: bold; color: #495057; margin-bottom: 10px;">{user.get("name", "Unknown")}</div>
            <a href="{user.get("twitter_user_url", "#")}" target="_blank" style="font-size: 1.2em; color: #667eea; text-decoration: none; font-weight: 500; margin-bottom: 15px; display: inline-block;">@{user.get("username", "Unknown")}</a>
            <div style="display: inline-block; padding: 8px 16px; background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: #b8860b; border-radius: 25px; font-weight: bold; font-size: 1.1em; margin-bottom: 20px;">🏆 순위: #{user.get("rank", "N/A")}</div>
            <div style="background: white; padding: 15px; border-radius: 10px; color: #6c757d; line-height: 1.5; margin-bottom: 20px; border-left: 4px solid #667eea;"><strong>소개:</strong><br>{user.get("bio", "")}</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px;">
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #495057; margin-bottom: 5px;">{user.get("mention_count", 0)}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">mention count</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #495057; margin-bottom: 5px;">{user.get("follower_count", 0):,}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">follower</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #495057; margin-bottom: 5px;">{user.get("mindshare", 0):.3f}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">Mindshare</div>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #495057; margin-bottom: 5px;">{user.get("community_score", 0):.2f}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">Community Score</div>
                </div>
            </div>
        </div>
        '''
    else:
        content = '''
        <div style="text-align: center; padding: 40px; color: #6c757d;">
            <h2>username not found</h2>
            <p>username is incorrect or not in top 100</p>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>result - Kaito AI KOL</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .back-button {{
                display: inline-block;
                margin-top: 15px;
                padding: 10px 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 search result</h1>
                <p>검색어: <strong>{username}</strong></p>
                <a href="/" class="back-button">← back to leaderboard</a>
            </div>
            <div style="padding: 30px;">
                {content}
            </div>
        </div>
    </body>
    </html>
    '''

async def fetch_leaderboard_data():
    """리더보드 데이터를 가져오는 함수"""
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
            
            if response.status_code != 200:
                return None, f"API Error: {response.status_code}"
            
            response_data = response.json()
            
            # 데이터 추출
            leaders = []
            if isinstance(response_data, list):
                leaders = response_data
            elif isinstance(response_data, dict):
                if "data" in response_data:
                    if isinstance(response_data["data"], list):
                        leaders = response_data["data"]
                    elif "top_kols" in response_data["data"]:
                        leaders = response_data["data"]["top_kols"]
                elif "top_kols" in response_data:
                    leaders = response_data["top_kols"]
                elif "results" in response_data:
                    leaders = response_data["results"]
            
            return leaders, None
            
    except Exception as e:
        return None, str(e)

@app.get("/", response_class=HTMLResponse)
async def leaderboard():
    leaders, error = await fetch_leaderboard_data()
    return HTMLResponse(get_leaderboard_html(leaders, error))

@app.get("/search/{username}", response_class=HTMLResponse)
async def search_user(username: str):
    leaders, error = await fetch_leaderboard_data()
    
    if error:
        return HTMLResponse(get_user_detail_html(username, None, error))
    
    # 사용자 찾기
    found_user = None
    if leaders:
        for leader in leaders:
            if leader.get("username", "").lower() == username.lower():
                found_user = leader
                break
    
    return HTMLResponse(get_user_detail_html(username, found_user, None))

@app.get("/debug")
async def debug_api():
    """디버깅용 엔드포인트"""
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
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.json() if response.status_code == 200 else response.text,
                "token_exists": bool(TOKEN),
                "token_length": len(TOKEN) if TOKEN else 0
            }
    except Exception as e:
        return {"error": str(e)}

# Vercel 핸들러
app.title = "Kaito AI KOL Leaderboard"