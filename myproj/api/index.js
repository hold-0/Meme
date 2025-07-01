// Vercel Serverless Function
export default async function handler(req, res) {
  const TOKEN = process.env.KAITO_API_TOKEN;
  const API_URL = "https://hub.kaito.ai/api/v1/gateway/ai/kol/mindshare/top-leaderboard";
  
  // CORS 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  try {
    // API에서 데이터 가져오기
    const apiResponse = await fetch(`${API_URL}?duration=7d&topic_id=M&top_n=100&customized_community=customized&community_yaps=true`, {
      headers: {
        'Authorization': TOKEN,
        'Accept': 'application/json'
      }
    });
    
    if (!apiResponse.ok) {
      throw new Error(`API Error: ${apiResponse.status}`);
    }
    
    const leaders = await apiResponse.json();
    const { url } = req;
    
    // 라우팅 처리
    if (url.includes('/search/')) {
      // 사용자 검색
      const username = url.split('/search/')[1];
      const foundUser = leaders.find(leader => 
        leader.username && leader.username.toLowerCase() === username.toLowerCase()
      );
      
      if (foundUser) {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.status(200).send(getUserDetailHTML(username, foundUser));
      } else {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.status(404).send(getUserNotFoundHTML(username));
      }
    } else if (url.includes('/debug')) {
      // 디버그 정보
      res.setHeader('Content-Type', 'application/json');
      res.json({
        token_exists: !!TOKEN,
        data_count: leaders.length,
        first_user: leaders[0] || null,
        url: url
      });
    } else {
      // 메인 페이지
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.status(200).send(getLeaderboardHTML(leaders));
    }
    
  } catch (error) {
    console.error('Error:', error);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(500).send(`
      <div style="padding:50px;text-align:center;font-family:Arial;">
        <h1>🚫 Error</h1>
        <p>${error.message}</p>
        <p>Token exists: ${!!TOKEN}</p>
      </div>
    `);
  }
}

function getLeaderboardHTML(leaders) {
  let leadersHTML = '';
  
  if (leaders && leaders.length > 0) {
    leaders.slice(0, 50).forEach(leader => {
      const rank = leader.rank || 'N/A';
      const mindsharePercent = ((leader.mindshare || 0) * 100).toFixed(2);
      const name = (leader.name || 'Unknown').replace(/[<>"'&]/g, ''); // XSS 방지
      const username = (leader.username || 'Unknown').replace(/[<>"'&]/g, '');
      
      leadersHTML += `
        <div style="display:flex;align-items:center;padding:15px;margin-bottom:10px;background:#f8f9fa;border-radius:10px;border-left:4px solid #667eea;">
          <div style="font-size:1.5em;font-weight:bold;color:#495057;min-width:60px;text-align:center;">#${rank}</div>
          <img src="${leader.icon || ''}" style="width:50px;height:50px;border-radius:50%;margin:0 15px;object-fit:cover;" onerror="this.style.display='none'" alt="Profile">
          <div style="flex:1;">
            <div style="font-weight:bold;color:#495057;">${name}</div>
            <a href="${leader.twitter_user_url || '#'}" target="_blank" rel="noopener" style="color:#667eea;text-decoration:none;">@${username}</a>
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
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kaito AI KOL Leaderboard</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;min-height:100vh;}
.container{max-width:1000px;margin:0 auto;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
.header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;border-radius:15px 15px 0 0;}
.search{padding:20px;background:#f8f9fa;text-align:center;border-bottom:1px solid #e9ecef;}
.search input{padding:12px 16px;border:2px solid #ddd;border-radius:8px;font-size:16px;width:280px;margin-right:10px;}
.search button{padding:12px 24px;background:#667eea;color:white;border:none;border-radius:8px;font-size:16px;cursor:pointer;transition:background 0.3s;}
.search button:hover{background:#5a6fd8;}
@media (max-width: 768px){
  .search input{width:200px;margin-bottom:10px;margin-right:0;}
  .search button{width:100px;}
}
</style></head>
<body><div class="container">
<div class="header">
  <h1>🏆 Kaito AI KOL Leaderboard</h1>
  <p>Top influencers in crypto community</p>
</div>
<div class="search">
  <input type="text" id="searchInput" placeholder="Search username (e.g. wanghebbf)">
  <button onclick="searchUser()">Search</button>
</div>
<div style="padding:20px;">${leadersHTML}</div>
</div>
<script>
function searchUser(){
  const username=document.getElementById('searchInput').value.trim();
  if(username) {
    window.location.href='/api/search/'+encodeURIComponent(username);
  } else {
    alert('Please enter a username');
  }
}
document.getElementById('searchInput').addEventListener('keypress',function(e){
  if(e.key==='Enter') searchUser();
});
</script></body></html>`;
}

function getUserDetailHTML(username, user) {
  const mindsharePercent = ((user.mindshare || 0) * 100).toFixed(2);
  const name = (user.name || 'Unknown').replace(/[<>"'&]/g, '');
  const usernameSafe = (user.username || 'Unknown').replace(/[<>"'&]/g, '');
  
  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>User Search Result - ${usernameSafe}</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:20px;min-height:100vh;}
.container{max-width:800px;margin:0 auto;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
.header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;border-radius:15px 15px 0 0;}
.back{color:white;text-decoration:none;background:rgba(255,255,255,0.2);padding:10px 20px;border-radius:25px;display:inline-block;margin-top:15px;transition:background 0.3s;}
.back:hover{background:rgba(255,255,255,0.3);}
.user-card{background:#f8f9fa;border-radius:15px;padding:30px;text-align:center;margin:30px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:15px;margin-top:20px;}
.stat{background:white;padding:20px;border-radius:10px;text-align:center;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
</style></head>
<body><div class="container">
<div class="header">
  <h1>🔍 User Search Result</h1>
  <p>Search term: <strong>${username}</strong></p>
  <a href="/api" class="back">← Back to Leaderboard</a>
</div>
<div class="user-card">
  <img src="${user.icon || ''}" style="width:100px;height:100px;border-radius:50%;margin-bottom:20px;border:3px solid #dee2e6;object-fit:cover;" onerror="this.style.display='none'" alt="Profile">
  <h2>${name}</h2>
  <a href="${user.twitter_user_url || '#'}" target="_blank" rel="noopener" style="color:#667eea;text-decoration:none;font-size:1.2em;">@${usernameSafe}</a>
  <div style="background:#ffd700;color:#b8860b;padding:8px 16px;border-radius:25px;display:inline-block;margin:20px 0;font-weight:bold;">
    🏆 Rank: #${user.rank || 'N/A'}
  </div>
  <div class="stats">
    <div class="stat">
      <div style="font-size:1.5em;font-weight:bold;color:#495057;">${user.mention_count || 0}</div>
      <div style="color:#6c757d;">Mentions</div>
    </div>
    <div class="stat">
      <div style="font-size:1.5em;font-weight:bold;color:#495057;">${(user.follower_count || 0).toLocaleString()}</div>
      <div style="color:#6c757d;">Followers</div>
    </div>
    <div class="stat">
      <div style="font-size:1.5em;font-weight:bold;color:#495057;">${mindsharePercent}%</div>
      <div style="color:#6c757d;">Mindshare</div>
    </div>
    <div class="stat">
      <div style="font-size:1.5em;font-weight:bold;color:#495057;">${(user.community_score || 0).toFixed(2)}</div>
      <div style="color:#6c757d;">Community Score</div>
    </div>
  </div>
</div>
</div></body></html>`;
}

function getUserNotFoundHTML(username) {
  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>User Not Found</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);margin:0;padding:50px;text-align:center;min-height:100vh;}
.card{background:white;border-radius:15px;padding:40px;max-width:500px;margin:0 auto;box-shadow:0 10px 30px rgba(0,0,0,0.1);}
</style></head>
<body>
<div class="card">
  <h1>❌ User not found</h1>
  <p>Username "<strong>${username}</strong>" is not in the leaderboard.</p>
  <p>Please check the spelling or try a different username.</p>
  <a href="/api" style="color:#667eea;text-decoration:none;background:#f8f9fa;padding:10px 20px;border-radius:8px;display:inline-block;margin-top:20px;">← Back to Leaderboard</a>
</div>
</body></html>`;
}