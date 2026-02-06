#!/bin/bash
# Deploy Course Companion Frontend to Production Server

set -e

echo "=== Packaging Frontend Build ==="
cd web-app

# Create a tarball of the build output
echo "Creating build archive..."
tar -czf ../frontend-build.tar.gz \
  .next \
  public \
  package.json \
  package-lock.json \
  .env.local \
  .env.production \
  next.config.js

echo "Build archive created: frontend-build.tar.gz"

# Upload to server
echo "Uploading to production server..."
scp ../frontend-build.tar.gz n00bi2761@92.113.147.250:~/course-companion/

# Extract and start on server
echo "Extracting and starting on server..."
ssh -o StrictHostKeyChecking=no n00bi2761@92.113.147.250 << 'ENDSSH'
cd ~/course-companion

# Kill existing frontend process on port 3225
lsof -ti:3225 | xargs -r kill -9

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

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install --production --silent
fi

# Start frontend on port 3225
echo "Starting frontend on port 3225..."
NODE_ENV=production nohup ./node_modules/.bin/next start -p 3225 > /tmp/frontend.log 2>&1 &

echo "Frontend started on port 3225"
sleep 2
ps aux | grep "next start" | grep -v grep

ENDSSH

echo ""
echo "=== Frontend Deployed! ==="
echo "Frontend URL: http://92.113.147.250:3225"
echo ""
