require('http').createServer((q,s)=>{s.setHeader('content-type','application/json');s.end(JSON.stringify({x_app:q.headers['x-app']||null,cookie:q.headers['cookie']||null,url:q.url}))}).listen(9000);
