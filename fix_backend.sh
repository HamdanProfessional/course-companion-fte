#!/bin/bash
# Complete backend restart script

sshpass -p "2763" ssh -o StrictHostKeyChecking=no n00bi2761@92.113.147.250 << 'ENDSSH'
echo "=== Killing all uvicorn processes ==="
# Try to kill as n00bi2761 user
pkill -9 -u n00bi2761 uvicorn
sleep 1

# Try to use systemctl to stop service
systemctl --user stop course-companion-backend 2>/dev/null || echo "User service not running"

echo "=== Checking for remaining processes ==="
ps aux | grep uvicorn | grep -v grep

echo "=== Starting new backend ==="
cd ~/course-companion/backend
nohup /usr/bin/python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 > backend.log 2>&1 &
sleep 3

echo "=== Verifying new backend ==="
ps aux | grep uvicorn | grep -v grep
echo ""
echo "=== Backend log (last 10 lines) ==="
tail -10 ~/course-companion/backend/backend.log

echo ""
echo "=== Testing health endpoint ==="
curl -s http://localhost:3505/health || echo "Health check failed"

echo ""
echo "=== Testing auth endpoint ==="
curl -s -X POST http://localhost:3505/api/v1/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=testuser@test.com&password=test123456&role=student" || echo "Auth test failed"

echo ""
echo "=== Done ==="
ENDSSH
