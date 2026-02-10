#!/bin/bash
set -e

# UI/Frontend Bug Fixes Deployment v2 - Proper file deployment
# Fixes: Email validation, certificate name validation, console logs removed, React hooks warnings fixed

SERVER="n00bi2761@92.113.147.250"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/ui-bug-fixes-v2"

echo "=== UI/Frontend Bug Fixes Deployment v2 ==="
echo "This will deploy:"
echo "  - Register page: Email validation added"
echo "  - Profile page: Certificate name validation improved"
echo "  - Progress/Subscription/Adaptive pages: Console logs removed"
echo "  - Multiple pages: React hooks warnings fixed"
echo ""

# Create temporary directory with subdirectories
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Create subdirectories for each file
ssh $SERVER "mkdir -p $TEMP_DIR/{register,profile,progress,subscription,adaptive-learning,ai-mentor,certificate-verify,leaderboard}"

echo ""
echo "2. Deploying frontend files to proper locations..."

# Upload each file to its own subdirectory
scp web-app/src/app/register/page.tsx $SERVER:$TEMP_DIR/register/
scp web-app/src/app/profile/page.tsx $SERVER:$TEMP_DIR/profile/
scp web-app/src/app/progress/page.tsx $SERVER:$TEMP_DIR/progress/
scp web-app/src/app/subscription/page.tsx $SERVER:$TEMP_DIR/subscription/
scp web-app/src/app/adaptive-learning/page.tsx $SERVER:$TEMP_DIR/adaptive-learning/
scp web-app/src/app/ai-mentor/page.tsx $SERVER:$TEMP_DIR/ai-mentor/
scp web-app/src/app/certificate/verify/[id]/page.tsx $SERVER:$TEMP_DIR/certificate-verify/
scp web-app/src/app/leaderboard/page.tsx $SERVER:$TEMP_DIR/leaderboard/

# Install frontend files to correct locations
echo ""
echo "3. Installing frontend files to correct locations..."
ssh $SERVER << 'EOF'
cd /home/n00bi2761/course-companion/frontend

# Copy each file to its correct location
cp /tmp/ui-bug-fixes-v2/register/page.tsx src/app/register/
cp /tmp/ui-bug-fixes-v2/profile/page.tsx src/app/profile/
cp /tmp/ui-bug-fixes-v2/progress/page.tsx src/app/progress/
cp /tmp/ui-bug-fixes-v2/subscription/page.tsx src/app/subscription/
cp /tmp/ui-bug-fixes-v2/adaptive-learning/page.tsx src/app/adaptive-learning/
cp /tmp/ui-bug-fixes-v2/ai-mentor/page.tsx src/app/ai-mentor/
mkdir -p src/app/certificate/verify/[id]/
cp /tmp/ui-bug-fixes-v2/certificate-verify/page.tsx src/app/certificate/verify/[id]/
cp /tmp/ui-bug-fixes-v2/leaderboard/page.tsx src/app/leaderboard/

echo "Frontend files updated successfully"
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
NODE_OPTIONS="--max-old-space-size=384" nohup npm start > /tmp/frontend.log 2>&1 &
sleep 5
ps aux | grep next-server | grep -v grep
echo "Frontend restarted successfully"
EOF

# Verify deployment
echo ""
echo "6. Verifying deployment..."
ssh $SERVER << EOF
echo "Testing pages:"
for page in register profile progress subscription leaderboard; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3225/$page")
  echo "  /$page: HTTP $status"
done
EOF

# Cleanup
echo ""
echo "7. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Fixed UI/Frontend bugs:"
echo "  ✓ Register page email validation"
echo "  ✓ Profile certificate name validation"
echo "  ✓ Console logs removed from production pages"
echo "  ✓ React hooks warnings fixed"
echo ""
echo "Access at: http://92.113.147.250:3225"
echo ""
