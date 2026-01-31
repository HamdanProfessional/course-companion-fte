# 🚀 Course Companion FTE Custom GPT - Quick Setup Checklist

## Before You Start

- [ ] Backend is deployed and accessible
- [ ] You have ChatGPT Plus or Team account
- [ ] You know your backend URL (e.g., `http://92.113.147.250:8180`)

---

## Setup Steps (5 Minutes)

### 1️⃣ Create New GPT
- [ ] Go to https://chat.openai.com
- [ ] Click "Explore GPTs" (left sidebar)
- [ ] Click "+ Create" (top right)

### 2️⃣ Basic Configuration
- [ ] **Name**: `Course Companion FTE`
- [ ] **Description**: Your AI-powered tutor for mastering AI Agent Development
- [ ] **Instructions**: Copy ALL content from `custom-gpt/instructions.md`

### 3️⃣ Configure Actions (API Tools)
- [ ] Scroll to "Actions" section
- [ ] Click "Create new action"
- [ ] **Domain**: Your backend URL (`http://92.113.147.250:8180`)
- [ ] **OpenAPI Schema**: Copy content from `custom-gpt/actions-schema.json`
- [ ] **IMPORTANT**: Update the server URL in the schema to your backend (already done!)

### 4️⃣ Profile (Optional)
- [ ] Add profile picture
- [ ] Set welcome message

### 5️⃣ Save & Test
- [ ] Click "Save" (top right)
- [ ] Test with: "Explain what MCP is"
- [ ] Test with: "Quiz me"
- [ ] Test with: "How am I doing?"

---

## Files to Copy

| From File | To Where |
|-----------|----------|
| `custom-gpt/instructions.md` | Instructions box (paste all) |
| `custom-gpt/actions-schema.json` | Actions → Create new action → OpenAPI schema |

---

## Quick Test Commands

Test these in your new GPT:

```
✅ "Explain what MCP is"
   → Should explain Model Context Protocol

✅ "Quiz me"
   → Should start a quiz

✅ "How am I doing?"
   → Should show progress and streak

✅ "I'm stuck"
   → Should ask guiding questions

✅ "What topics can you teach?"
   → Should list available topics
```

---

## Common Issues

**GPT can't connect to backend:**
- Check backend URL in schema has `https://`
- Test backend: `curl https://your-backend/api/v1/chapters`

**GPT isn't following instructions:**
- Make sure you copied the ENTIRE instructions.md file
- Try exact phrases from examples

**Getting 403 errors:**
- Backend access control is working (correct for free tier)
- First 3 chapters should be accessible

---

## Share Your GPT

Once working:
1. Click your GPT's name (top left)
2. Click "Edit"
3. Configure sharing (public/link only)
4. Copy share link
5. Share with students! 🎓

---

## Need Help?

- Full Guide: `custom-gpt/DEPLOYMENT_GUIDE.md`
- Backend Deployment: `backend/README.md`
- Course Repo: Main README.md

---

## Tips

💡 **Test with exact phrases** from examples first
💡 **Start conversations with clear intents** ("Explain...", "Quiz me", "How am I...")
💡 **Backend URL must use https://** (not http://)
💡 **Update schema server URL** before saving

---

## Success!

Your Course Companion FTE Custom GPT is ready to help students learn 24/7! 🎉
