from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import httpx
import os
import asyncio

# 환경 변수
TOKEN = os.getenv("KAITO_API_TOKEN")
API_URL = "https://hub.kaito.ai/api/v1/gateway/ai/kol/mindshare/top-leaderboard"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URL 파싱
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/" or path == "/index.html":
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                # 리더보드 데이터 가져오기
                leaders = asyncio.run(self.fetch_leaderboard_data())
                html = self.get_leaderboard_html(leaders)
                self.wfile.write(html.encode())
                
            elif path.startswith("/search/"):
                username = path.split("/search/")[1]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                leaders = asyncio.run(self.fetch_leaderboard_data())
                found_user = self.find_user(leaders, username)
                html = self.get_user_detail_html(username, found_user)
                self.wfile.write(html.encode())
                
            elif path == "/debug":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                debug_info = {
                    "token_exists": bool(TOKEN),
                    "token_length": len(TOKEN) if TOKEN else 0,
                    "api_url": API_URL
                }
                self.wfile.write(json.dumps(debug_info).encode())
                
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 Not Found</h1>')
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<h1>Error: {str(e)}</h1>'.encode())
    
    async def fetch_leaderboard_data(self):
        """리더보드 데이터 가져오기"""
        if not TOKEN:
            return []
            
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
                    return []
                
                response_data = response.json()
                
                # 데이터 추출
                if isinstance(response_data, list):
                    return response_data
                elif isinstance(response_data, dict):
                    if "data" in response_data:
                        if isinstance(response_data["data"], list):
                            return response_data["data"]
                        elif "top_kols" in response_data["data"]:
                            return response_data["data"]["top_kols"]
                    elif "top_kols" in response_data:
                        return response_data["top_kols"]
                
                return []
        except Exception:
            return []
    
    def find_user(self, leaders, username):
        """사용자 찾기"""
        for leader in leaders:
            if leader.get("username", "").lower() == username.lower():
                return leader
        return None
    
    def get_leaderboard_html(self, leaders):
        """리더보드 HTML 생성"""
        leaders_html = ""
        
        if leaders:
            for leader in leaders[:50]:  # 처음 50명만 표시
                rank = leader.get("rank", "N/A")
                leaders_html += f'''
                <div style="display: flex; align-items: center; padding: 15px; margin-bottom: 10px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #667eea;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #495057; min-width: 60px; text-align: center;">#{rank}</div>
                    <img src="{leader.get("icon", "")}" alt="{leader.get("name", "")}" style="width: 50px; height: 50px; border-radius: 50%; margin: 0 15px; object-fit: cover;" onerror="this.style.display='none'">
                    <div style="flex: 1;">
                        <div style="font-weight: bold; color: #495057;">{leader.get("name", "Unknown")}</div>
                        <a href="{leader.get("twitter_user_url", "#")}" target="_blank" style="color: #667eea; text-decoration: none;">@{leader.get("username", "Unknown")}</a>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; min-width: 80px; margin-left: 10px;">
                        <div style="font-weight: bold; color: #495057;">{leader.get("mention_count", 0)}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Mentions</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; min-width: 80px; margin-left: 10px;">
                        <div style="font-weight: bold; color: #495057;">{(leader.get("mindshare", 0) * 100):.2f}%</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Mindshare</div>
                    </div>
                </div>
                '''
        else:
                            leaders_html = '<div style="text-align: center; padding: 40px; color: #6c757d;"><p>Loading data...</p></div>'
        
        return f'''
        <!DOCTYPE html>
        <html lang="en">
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
                    max-width: 1000px;
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
                    text-align: center;
                }}
                .search-input {{
                    padding: 12px 16px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    margin-right: 10px;
                    width: 250px;
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
                    <input type="text" class="search-input" id="searchInput" placeholder="Search username (e.g. wanghebbf)">
                    <button class="search-btn" onclick="searchUser()">Search</button>
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
                    }}
                }}
                document.getElementById('searchInput').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') searchUser();
                }});
            </script>
        </body>
        </html>
        '''
    
    def get_user_detail_html(self, username, user):
        """사용자 상세 HTML 생성"""
        if user:
            content = f'''
            <div style="background: #f8f9fa; border-radius: 15px; padding: 30px; text-align: center;">
                <img src="{user.get("icon", "")}" alt="{user.get("name", "")}" style="width: 100px; height: 100px; border-radius: 50%; margin-bottom: 20px; object-fit: cover;" onerror="this.style.display='none'">
                <h2>{user.get("name", "Unknown")}</h2>
                <a href="{user.get("twitter_user_url", "#")}" target="_blank" style="color: #667eea; text-decoration: none;">@{user.get("username", "Unknown")}</a>
                <div style="background: #ffd700; color: #b8860b; padding: 8px 16px; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold;">
                    🏆 Rank: #{user.get("rank", "N/A")}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-top: 20px;">
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold;">{user.get("mention_count", 0)}</div>
                        <div style="color: #6c757d;">Mentions</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold;">{user.get("follower_count", 0):,}</div>
                        <div style="color: #6c757d;">Followers</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold;">{(user.get("mindshare", 0) * 100):.2f}%</div>
                        <div style="color: #6c757d;">Mindshare</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 1.5em; font-weight: bold;">{user.get("community_score", 0):.2f}</div>
                        <div style="color: #6c757d;">Community Score</div>
                    </div>
                </div>
            </div>
            '''
        else:
            content = '''
            <div style="text-align: center; padding: 40px;">
                <h2>❌ User not found</h2>
                <p>The username you entered is not in the leaderboard.</p>
            </div>
            '''
        
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Search Result</title>
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
                    <h1>🔍 User Search Result</h1>
                    <p>Search term: <strong>{username}</strong></p>
                    <a href="/" class="back-button">← Back to Leaderboard</a>
                </div>
                <div style="padding: 30px;">
                    {content}
                </div>
            </div>
        </body>
        </html>
        '''