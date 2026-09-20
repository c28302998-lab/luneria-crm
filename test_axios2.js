const axios = require('axios');
const http = require('http');
const FormData = require('form-data');

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', chunk => body += chunk.toString());
  req.on('end', () => {
    console.log("Headers:", req.headers['content-type']);
    console.log("Body length:", body.length);
    res.end('ok');
  });
});

server.listen(3000, async () => {
  const api = axios.create({
    baseURL: 'http://localhost:3000',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  const fd = new FormData();
  fd.append('test', '123');

  await api.post('/', fd, {
    headers: { 'Content-Type': undefined }
  });
  
  server.close();
});
