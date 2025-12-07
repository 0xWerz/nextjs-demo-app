/**
 * VICTIM'S INTERNAL SECRET API
 * =============================
 * This simulates a sensitive internal service running on localhost.
 * In real scenarios this could be:
 * - Cloud metadata service (169.254.169.254)
 * - Internal admin API
 * - Database management interface
 * - Kubernetes API
 */

const http = require('http');

const SECRETS = {
  aws_access_key: 'AKIAIOSFODNN7EXAMPLE',
  aws_secret_key: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  database_password: 'super_secret_db_password_123',
  admin_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.victim_admin_token',
  internal_api_key: 'internal-api-key-that-should-never-leak',
};

const server = http.createServer((req, res) => {
  console.log(`[VICTIM API] ${new Date().toISOString()} Request: ${req.method} ${req.url}`);
  
  // Simulate cloud metadata endpoint
  if (req.url === '/latest/meta-data/iam/security-credentials/') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(SECRETS, null, 2));
    console.log('[VICTIM API] ⚠️  SECRETS LEAKED TO ATTACKER!');
    return;
  }
  
  // Default response
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Internal API - You should not be seeing this!');
});

const PORT = 8888;
server.listen(PORT, '127.0.0.1', () => {
  console.log('='.repeat(60));
  console.log(' VICTIM INTERNAL API (simulating cloud metadata)');
  console.log('='.repeat(60));
  console.log('');
  console.log('Listening on: http://127.0.0.1:' + PORT);
  console.log('');
  console.log('This contains sensitive secrets that should NEVER be');
  console.log('accessible from external requests.');
  console.log('');
  console.log('Secrets stored:', Object.keys(SECRETS));
  console.log('='.repeat(60));
});
