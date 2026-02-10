#!/bin/bash
set -e

# Profile Page Certificate API Fix Deployment Script
# Fixes: Certificate eligibility API - user_id sent as query parameter instead of body

SERVER="n00bi2761@92.113.147.250"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/profile-fix-deploy"

echo "=== Profile Page Certificate API Fix Deployment ==="
echo "This will deploy:"
echo "  - Frontend: Fixed checkCertificateEligibility API call (query parameter fix)"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Frontend Files
echo ""
echo "2. Deploying frontend files..."
echo "   - lib/api-v3.ts (Certificate eligibility API fix)"

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
echo "   Checking frontend..."
ssh $SERVER << EOF
curl -s -I http://localhost:3225 | head -1 || echo "Frontend check failed"
EOF

# Cleanup
echo ""
echo "7. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Deployed fixes:"
echo "  - Certificate eligibility API now sends user_id as query parameter"
echo ""
echo "Profile page features:"
echo "  - Account information display"
echo "  - Password change (UI only)"
echo "  - Subscription tier display"
echo "  - Certificate generation (when eligible)"
echo "  - Certificate list display"
echo "  - Data export options"
echo ""
echo "Access at: http://92.113.147.250:3225/profile"
echo ""
