#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const HOMEPAGE_PATH = path.join(__dirname, 'frontend', 'public', 'index-root.html');

const server = http.createServer((req, res) => {
  // Serve the homepage at root
  if (req.url === '/' || req.url === '/index.html') {
    fs.readFile(HOMEPAGE_PATH, (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading homepage');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  } 
  // Serve static files (images, etc.)
  else if (req.url.startsWith('/')) {
    const filePath = path.join(__dirname, 'frontend', 'public', req.url);
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      // Determine content type
      let contentType = 'application/octet-stream';
      if (filePath.endsWith('.jpg') || filePath.endsWith('.jpeg')) {
        contentType = 'image/jpeg';
      } else if (filePath.endsWith('.png')) {
        contentType = 'image/png';
      } else if (filePath.endsWith('.gif')) {
        contentType = 'image/gif';
      } else if (filePath.endsWith('.css')) {
        contentType = 'text/css';
      } else if (filePath.endsWith('.js')) {
        contentType = 'application/javascript';
      }
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`\n🚀 Homepage server running at:`);
  console.log(`   http://localhost:${PORT}\n`);
});

