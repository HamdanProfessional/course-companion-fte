#!/bin/bash
set -e

# AI Mentor Page Redesign Deployment Script
# Deploys ChatKit-style AI Mentor page with chat history storage

SERVER="n00bi2761@92.113.147.250"
BACKEND_PATH="/home/n00bi2761/course-companion/backend"
FRONTEND_PATH="/home/n00bi2761/course-companion/frontend"
TEMP_DIR="/tmp/ai-mentor-deploy"

echo "=== AI Mentor Page Redesign Deployment ==="
echo "This will deploy:"
echo "  - Backend: Chat history API endpoints and models"
echo "  - Frontend: ChatKit-style AI Mentor page"
echo ""

# Create temporary directory
echo "1. Creating temporary deployment directory..."
ssh $SERVER "mkdir -p $TEMP_DIR"

# Deploy Backend Files
echo ""
echo "2. Deploying backend files..."
echo "   - database.py (ChatConversation and ChatMessage models)"
echo "   - api/v3/tutor/chat.py (new chat history endpoints)"
echo "   - api/v3/tutor/__init__.py (router registration)"
echo "   - api/v3/tutor/ai.py (updated to save chat history)"
echo "   - api/v3/certificate/verify.py (import fix)"

# Copy backend files
scp backend/src/models/database.py $SERVER:$TEMP_DIR/
scp backend/src/api/v3/tutor/chat.py $SERVER:$TEMP_DIR/
scp backend/src/api/v3/tutor/__init__.py $SERVER:$TEMP_DIR/
scp backend/src/api/v3/tutor/ai.py $SERVER:$TEMP_DIR/
scp backend/src/api/v3/certificate/verify.py $SERVER:$TEMP_DIR/

# Install backend files
echo ""
echo "3. Installing backend files..."
ssh $SERVER << EOF
cd $BACKEND_PATH
cp $TEMP_DIR/database.py src/models/
cp $TEMP_DIR/chat.py src/api/v3/tutor/
cp $TEMP_DIR/__init__.py src/api/v3/tutor/
cp $TEMP_DIR/ai.py src/api/v3/tutor/
mkdir -p src/api/v3/certificate
cp $TEMP_DIR/verify.py src/api/v3/certificate/
echo "Backend files installed successfully"
EOF

# Deploy Frontend Files
echo ""
echo "4. Deploying frontend files..."
echo "   - ai-mentor/page.tsx (ChatKit-style redesign)"
echo "   - lib/api-v3.ts (chat history API methods)"
echo "   - hooks/useV3.ts (chat history hooks)"

# Copy frontend files
scp web-app/src/app/ai-mentor/page.tsx $SERVER:$TEMP_DIR/
scp web-app/src/lib/api-v3.ts $SERVER:$TEMP_DIR/
scp web-app/src/hooks/useV3.ts $SERVER:$TEMP_DIR/

# Install frontend files
echo ""
echo "5. Installing frontend files..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
cp $TEMP_DIR/page.tsx src/app/ai-mentor/
cp $TEMP_DIR/api-v3.ts src/lib/
cp $TEMP_DIR/useV3.ts src/hooks/
echo "Frontend files installed successfully"
EOF

# Run database migrations
echo ""
echo "6. Running database migrations..."
ssh $SERVER << EOF
cd $BACKEND_PATH
python3 -m alembic revision --autogenerate -m "Add chat history tables"
python3 -m alembic upgrade head
echo "Database migrations completed"
EOF

# Restart backend
echo ""
echo "7. Restarting backend service..."
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
echo "8. Rebuilding frontend..."
ssh $SERVER << EOF
cd $FRONTEND_PATH
rm -rf .next
npm run build
echo "Frontend built successfully"
EOF

# Restart frontend
echo ""
echo "9. Restarting frontend service..."
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
echo "10. Verifying deployment..."
echo "   Checking backend health..."
ssh $SERVER << EOF
curl -s http://localhost:3505/health || echo "Backend health check failed"
EOF

echo ""
echo "   Checking frontend..."
ssh $SERVER << EOF
curl -s -I http://localhost:3225 | head -1 || echo "Frontend check failed"
EOF

echo ""
echo "   Testing chat history endpoint..."
ssh $SERVER << EOF
curl -s http://localhost:3505/api/v3/tutor/chat || echo "Chat endpoint test failed"
EOF

# Cleanup
echo ""
echo "11. Cleaning up temporary files..."
ssh $SERVER "rm -rf $TEMP_DIR"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "AI Mentor page is now live at: http://92.113.147.250:3225/ai-mentor"
echo ""
echo "Features deployed:"
echo "  - ChatKit-style interface"
echo "  - Chat history storage in database"
echo "  - Create/load/delete conversations"
echo "  - Conversation title editing"
echo "  - Real-time chat with AI mentor"
echo ""
echo "To verify:"
echo "  1. Visit http://92.113.147.250:3225/ai-mentor"
echo "  2. Start a new conversation"
echo "  3. Send a message"
echo "  4. Check that conversation appears in sidebar"
echo "  5. Refresh page and verify chat history persists"
