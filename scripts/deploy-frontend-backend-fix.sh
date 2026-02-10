#!/bin/bash
# Deploy Frontend with Correct Backend URL (Port 3505)

set -e

echo "=== Building Frontend with Correct Backend URL ==="
cd web-app

# Set the backend URL explicitly
export NEXT_PUBLIC_BACKEND_URL=http://92.113.147.250:3505
echo "Backend URL: $NEXT_PUBLIC_BACKEND_URL"

# Build the frontend
echo "Building frontend..."
npm run build

# Create deployment archive
echo "Creating deployment archive..."
tar -czf ../frontend-build.tar.gz \
  .next \
  public \
  package.json \
  package-lock.json \
  next.config.js

echo "Build archive created: frontend-build.tar.gz"

# Upload to server
echo "Uploading to production server..."
scp ../frontend-build.tar.gz n00bi2761@92.113.147.250:~/course-companion/

# Extract and restart on server
echo "Deploying on server..."
ssh -o StrictHostKeyChecking=no n00bi2761@92.113.147.250 << 'ENDSSH'
cd ~/course-companion

# Kill existing frontend process on port 3225
echo "Stopping existing frontend..."
lsof -ti:3225 | xargs -r kill -9 || true

# Backup old frontend if exists
if [ -d "frontend-old" ]; then
  rm -rf frontend-old
fi
if [ -d "frontend" ]; then
  mv frontend frontend-old
fi

# Create new frontend directory
mkdir -p frontend
cd frontend

# Extract build
tar -xzf ../frontend-build.tar.gz
rm ../frontend-build.tar.gz

# Start frontend on port 3225
echo "Starting frontend on port 3225..."
NODE_ENV=production NEXT_PUBLIC_BACKEND_URL=http://92.113.147.250:3505 nohup ./node_modules/.bin/next start -p 3225 > /tmp/frontend.log 2>&1 &

echo "Waiting for frontend to start..."
sleep 5

# Check if frontend is running
if lsof -i:3225 > /dev/null; then
  echo "✅ Frontend started successfully on port 3225"
  echo "Check logs: tail -f /tmp/frontend.log"
else
  echo "❌ Failed to start frontend"
  tail -20 /tmp/frontend.log
fi

ENDSSH

# Cleanup
rm ../frontend-build.tar.gz

echo ""
echo "=== Deployment Complete! ==="
echo "Frontend URL: http://92.113.147.250:3225"
echo "Backend URL: http://92.113.147.250:3505"
echo ""
