// Next.js API Route
export default async function handler(req, res) {
  const TOKEN = process.env.KAITO_API_TOKEN;
  const API_URL = "https://hub.kaito.ai/api/v1/gateway/ai/kol/mindshare/top-leaderboard";
  
  try {
    // API에서 데이터 가져오기
    const response = await fetch(`${API_URL}?duration=7d&topic_id=M&top_n=100&customized_community=customized&community_yaps=true`, {
      headers: {
        'Authorization': TOKEN,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const leaders = await response.json();
    const { url } = req;
    
    // 라우팅 처리
    if (url.startsWith('/api/search/')) {
      // 사용자 검색
      const username = url.split('/api/search/')[1];
      const foundUser = leaders.find(leader => 
        leader.username && leader.username.toLowerCase() === username.toLowerCase()
      );
      
      if (foundUser) {
        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(getUserDetailHTML(username, foundUser));
      } else {
        res.setHeader('Content-Type', 'text/html');
        res.status(404).send(getUserNotFoundHTML(username));
      }
    } else if (url === '/api/debug') {
      // 디버그 정보
      res.json({
        token_exists: !!TOKEN,
        data_count: leaders.length,
        first_user: leaders[0] || null
      });
    } else {
      // 메인 페이지
      res.setHeader('Content-Type', 'text/html');
      res.status(200).send(getLeaderboardHTML(leaders));
    }
    
  } catch (error) {
    res.setHeader('Content-Type', 'text/html');
    res.status(500).send(`<h1>Error: ${error.message}</h1>`);
  }
}

function getLeaderboardHTML(leaders) {
  let leadersHTML = '';
  
  if (leaders && leaders.length > 0) {
    leaders.slice(0, 50).forEach(leader => {
      const rank = leader.rank || 'N/A';
      const mindsharePercent = ((leader.mindshare || 0) * 100).toFixed(2);
      
      leadersHTML += `
        <div style="display:flex;align-items:center;padding:15px;margin-bottom:10px;background:#f8f9fa;border-radius:10px;border-left:4px solid #667eea;">
          <div style="font-size:1.5em;font-weight:bold;color:#495057;min-width:60px;text-align:center;">#${rank}</div>
          <img src="${leader.icon || ''}" style="width:50px;height:50px;border-radius:50%;margin:0 15px;object-fit:cover;" onerror="this.style.display='none'">
          <div style="flex:1;">
            <div style="font-weight:bold;color:#495057;">${leader.name || 'Unknown'}</div>
            <a href="${leader.twitter_user_url || '#'}" target="_blank" style="color:#667eea;text-decoration:none;">@${leader.username || 'Unknown'}</a>
          </div>
          <div style="text-align:center;padding:10px;background:white;border-radius:8px;min-width:80px;margin-left:10px;">
            <div style="font-weight:bold;">${leader.mention_count || 0}</div>
            <div style="font-size:0.8em;color:#6c757d;">Mentions</div>
          </div>
          <div style="text-align:center;padding:10px;background:white;border-radius:8px;min-width:80px;margin-left:10px;">
            <div style="font-weight:bold;">${mindsharePercent}%</div>
            <div style="font-size:0.8em;color:#6c757d;">Mindshare</div>
          </div>
        </div>`;
    });
  } else {
    leadersHTML = '<div style="text-align:center;padding:40px;color:#6c757d;">Loading data...</div>';
  }
  
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Kaito AI KOL Leaderboard</title>
<style>
body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;}
.container{max-width:1000px;margin:0 auto;background:white;border-radius:15px;}
.header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;border-radius:15px 15px 0 0;}
.search{padding:20px;background:#f8f9fa;text-align:center;}
.search input{padding:12px;border:2px solid #ddd;border-radius:8px;font-size:16px;width:250px;margin-right:10px;}
.search button{padding:12px 24px;background:#667eea;color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;}
</style></head>
<body><div class="container">
<div class="header"><h1>🏆 Kaito AI KOL Leaderboard</h1><p>Top influencers in crypto community</p></div>
<div class="search">
<input type="text" id="searchInput" placeholder="Search username (e.g. wanghebbf)">
<button onclick="searchUser()">Search</button>
</div>
<div style="padding:20px;">${leadersHTML}</div>
</div>
<script>
function searchUser(){
const username=document.getElementById('searchInput').value.trim();
if(username)window.location.href=\`/api/search/\${encodeURIComponent(username)}\`;
}
document.getElementById('searchInput').addEventListener('keypress',function(e){
if(e.key==='Enter')searchUser();
});
</script></body></html>`;
}

function getUserDetailHTML(username, user) {
  const mindsharePercent = ((user.mindshare || 0) * 100).toFixed(2);
  
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>User Search Result</title>
<style>
body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;}
.container{max-width:800px;margin:0 auto;background:white;border-radius:15px;padding:30px;}
.header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;margin:-30px -30px 30px;border-radius:15px 15px 0 0;}
.back{color:white;text-decoration:none;background:rgba(255,255,255,0.2);padding:10px 20px;border-radius:25px;display:inline-block;margin-top:15px;}
.user-card{background:#f8f9fa;border-radius:15px;padding:30px;text-align:center;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:15px;margin-top:20px;}
.stat{background:white;padding:20px;border-radius:10px;text-align:center;}
</style></head>
<body><div class="container">
<div class="header"><h1>🔍 User Search Result</h1><p>Search term: <strong>${username}</strong></p>
<a href="/api" class="back">← Back to Leaderboard</a></div>
<div class="user-card">
<img src="${user.icon || ''}" style="width:100px;height:100px;border-radius:50%;margin-bottom:20px;" onerror="this.style.display='none'">
<h2>${user.name || 'Unknown'}</h2>
<a href="${user.twitter_user_url || '#'}" target="_blank" style="color:#667eea;text-decoration:none;">@${user.username || 'Unknown'}</a>
<div style="background:#ffd700;color:#b8860b;padding:8px 16px;border-radius:25px;display:inline-block;margin:20px 0;font-weight:bold;">
🏆 Rank: #${user.rank || 'N/A'}</div>
<div class="stats">
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">${user.mention_count || 0}</div><div>Mentions</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">${(user.follower_count || 0).toLocaleString()}</div><div>Followers</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">${mindsharePercent}%</div><div>Mindshare</div></div>
<div class="stat"><div style="font-size:1.5em;font-weight:bold;">${(user.community_score || 0).toFixed(2)}</div><div>Community Score</div></div>
</div></div></div></body></html>`;
}

function getUserNotFoundHTML(username) {
  return `<!DOCTYPE html>
<html><head><title>User Not Found</title></head>
<body style="font-family:Arial;padding:50px;text-align:center;">
<h1>❌ User not found</h1><p>Username "${username}" is not in the leaderboard.</p>
<a href="/api" style="color:#667eea;">← Back to Leaderboard</a></body></html>`;
}