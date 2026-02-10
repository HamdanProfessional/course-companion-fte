#!/bin/bash
set -e

# Profile Page Certificate API Fix Deployment Script v2
# Fixes: All certificate API calls now include trailing slashes

SERVER="n00bi2761@92.113.147.250"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/certificate-fix-v2"

echo "=== Certificate API Trailing Slash Fix Deployment ==="
echo "This will deploy:"
echo "  - Frontend: Fixed all certificate API calls to include trailing slashes"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Frontend Files
echo ""
echo "2. Deploying frontend files..."
echo "   - lib/api-v3.ts (All certificate endpoints with trailing slashes)"

# Copy frontend files
scp web-app/src/lib/api-v3.ts $SERVER:$TEMP_DIR/

# Install frontend files
echo ""
echo "3. Installing frontend files..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/api-v3.ts src/lib/
echo "Frontend api-v3.ts updated successfully"
EOF

# Rebuild frontend
echo ""
echo "4. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "5. Restarting frontend service..."
ssh $SERVER << EOF
pkill -f 'next-server' || true
cd $FRONTEND_PATH
nohup npm start > /tmp/frontend.log 2>&1 &
sleep 5
ps aux | grep next-server | grep -v grep
echo "Frontend restarted successfully"
EOF

# Verify deployment
echo ""
echo "6. Verifying deployment..."
echo "   Testing certificate endpoints..."
ssh $SERVER << EOF
echo "Testing GET /api/v3/tutor/certificates/?user_id=test-id:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" "http://localhost:3505/api/v3/tutor/certificates/?user_id=6ad0fc59-90c8-4b3c-841a-4d6e46436d19"

echo "Testing POST /api/v3/tutor/certificates/check-eligibility/?user_id=test-id:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" -X POST "http://localhost:3505/api/v3/tutor/certificates/check-eligibility/?user_id=6ad0fc59-90c8-4b3c-841a-4d6e46436d19"
EOF

# Cleanup
echo ""
echo "7. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Fixed certificate endpoints:"
echo "  - GET /api/v3/tutor/certificates/?user_id={id}"
echo "  - POST /api/v3/tutor/certificates/check-eligibility/?user_id={id}"
echo "  - POST /api/v3/tutor/certificates/generate/?user_id={id}"
echo ""
echo "All endpoints now include trailing slashes for FastAPI compatibility."
echo ""
echo "Access profile at: http://92.113.147.250:3225/profile"
echo ""
