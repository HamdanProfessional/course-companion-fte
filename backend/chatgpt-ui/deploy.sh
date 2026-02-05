#!/bin/bash
# Deploy Course Companion FTE UI to server

UI_DIR="chatgpt-app/ui"
SERVER_HOST="n00bi2761@92.113.147.250"
SERVER_PATH="/home/n00bi2761/course-companion/ui"

echo "Building UI component..."
cd "$UI_DIR"
npm run build

echo "Uploading to server..."
ssh -o StrictHostKeyChecking=no "$SERVER_HOST" "mkdir -p $SERVER_PATH"

scp -o StrictHostKeyChecking=no \
  dist/component.js \
  index.html \
  "$SERVER_HOST:$SERVER_PATH/"

echo "UI deployed to https://sse.testservers.online/ui/"
echo "✅ Done!"
