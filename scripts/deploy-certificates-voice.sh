#!/bin/bash
set -e

# Certificate API Fix + AI Mentor Voice Input Deployment Script
# Deploys:
# 1. Certificate API fix (Query parameter fix)
# 2. AI Mentor page with nebula theme and voice input

SERVER="n00bi2761@92.113.147.250"
BACKEND_PATH="/home/n00bi2761/course-companion/backend"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/cert-voice-deploy"

echo "=== Certificate API Fix + AI Mentor Voice Input Deployment ==="
echo "This will deploy:"
echo "  - Backend: Certificate API Query parameter fix"
echo "  - Frontend: AI Mentor with nebula theme and voice input"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Backend Files
echo ""
echo "2. Deploying backend certificate API fix..."
echo "   - api/v3/tutor/certificates.py (Query parameter fix)"

# Copy backend files
scp backend/src/api/v3/tutor/certificates.py $SERVER:$TEMP_DIR/

# Install backend files
echo ""
echo "3. Installing backend files..."
ssh $SERVER << EOF
cd $BACKEND_PATH
cp $TEMP_DIR/certificates.py src/api/v3/tutor/
echo "Backend certificate fix installed successfully"
EOF

# Deploy Frontend Files
echo ""
echo "4. Deploying frontend files..."
echo "   - ai-mentor/page.tsx (Nebula theme + voice input)"

# Copy frontend files
scp web-app/src/app/ai-mentor/page.tsx $SERVER:$TEMP_DIR/

# Install frontend files
echo ""
echo "5. Installing frontend files..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/page.tsx src/app/ai-mentor/
echo "Frontend AI Mentor updated successfully"
EOF

# Restart backend
echo ""
echo "6. Restarting backend service..."
ssh $SERVER << EOF
pkill -f 'uvicorn' || true
cd $BACKEND_PATH
nohup python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 3505 --reload > /tmp/backend.log 2>&1 &
sleep 3
ps aux | grep uvicorn | grep -v grep
echo "Backend restarted successfully"
EOF

# Rebuild frontend
echo ""
echo "7. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "8. Restarting frontend service..."
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
echo "9. Verifying deployment..."
echo "   Checking backend health..."
ssh $SERVER << EOF
curl -s http://localhost:3505/health || echo "Backend health check failed"
EOF

echo ""
echo "   Checking frontend..."
ssh $SERVER << EOF
curl -s -I http://localhost:3225 | head -1 || echo "Frontend check failed"
EOF

# Cleanup
echo ""
echo "10. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Deployed features:"
echo "  - Certificate API Query parameter fix (backend)"
echo "  - AI Mentor with nebula theme and voice input (frontend)"
echo ""
echo "AI Mentor features:"
echo "  - Dark space-themed gradients (nebula theme)"
echo "  - Voice input with Web Speech API"
echo "  - Microphone button with recording animations"
echo "  - Glowing effects on active elements"
echo "  - ChatGPT-like conversation interface"
echo "  - Proper cosmic-purple, cosmic-pink, cosmic-blue, cosmic-cyan colors"
echo ""
echo "Access at: http://92.113.147.250:3225/ai-mentor"
echo ""
