# Submit Your App

**Source:** https://developers.openai.com/apps-sdk/deploy/submission
**Phase:** Deploy
**Last Updated:** February 2026

---

## Overview

Submit your app to the ChatGPT Apps Directory for public access.

**Important:** Only submit if you intend the app to be accessible to all users.

---

## Pre-Submission Requirements

### Organization Verification

Your organization must be verified on the OpenAI Platform.

**Steps:**
1. OpenAI Platform Dashboard → General settings
2. Complete individual or business verification
3. Verified identity available for app submission

### Owner Role

You must have **Owner** role in organization to:
- Complete verification
- Create and submit apps for review

**Note:** Current owners must grant Owner role to others who need to submit apps.

---

## MCP Server Requirements

| Requirement | Description |
|-------------|-------------|
| **Public domain** | Hosted on publicly accessible domain |
| **No testing endpoints** | Not using local or testing URLs |
| **CSP defined** | Allow exact domains you fetch from (security requirement) |

---

## Submission Process

### Step 1: Prepare

- MCP server deployed publicly
- OAuth metadata configured (if using OAuth)
- App tested thoroughly in Developer Mode
- Screenshots captured

### Step 2: Start Review

From OpenAI Platform Dashboard:

1. Add MCP server details
2. Add OAuth metadata (if selected)
3. Confirm compliance with OpenAI policies
4. Complete required fields in submission form
5. Check all confirmation boxes
6. Click **Submit for review**

### Step 3: Review Queue

- App enters review queue
- Status visible in Dashboard
- Email notifications for status changes

**Note:** Only one version in review per app at a time.

### Data Residency

**Important:** Projects with EU data residency cannot submit for review.
- Use global data residency project
- Create new project in current organization from Dashboard

---

## After Submission

### Review Process

| Stage | Description |
|-------|-------------|
| **Automated scans** | Security and policy checks |
| **Manual review** | Understand app functionality |
| **Policy check** | Verify compliance with guidelines |
| **Feedback** | Receive feedback if rejected |

### Publish Approved App

Once approved:

1. Click **Publish** button in Dashboard
2. App becomes discoverable in ChatGPT Apps Directory
3. Users can find via:
   - Direct link
   - Search by name

### Enhanced Distribution

Apps demonstrating:
- Strong real-world utility
- High user satisfaction

May be eligible for:
- Directory placement
- Proactive suggestions

---

## Maintenance

### App Removal

Apps may be removed for:
- Inactivity
- Instability
- Policy non-compliance
- Legal/security concerns
- Any reason without notice

### Resubmission for Changes

Once published:
- Tool names locked
- Signatures locked
- Descriptions locked

**To update:**
1. Resubmit app for review
2. Wait for approval
3. Publish update (replaces previous version)

---

## Submission Checklist

- [ ] Organization verified
- [ ] Owner role granted
- [ ] MCP server publicly accessible
- [ ] CSP configured correctly
- [ ] App tested in Developer Mode
- [ ] Golden prompts validated
- [ ] Screenshots captured
- [ ] Compliance confirmed
- [ ] All form fields completed
- [ ] Confirmation boxes checked

---

## Best Practices

1. **Test thoroughly** - Use Developer Mode extensively
2. **Follow guidelines** - Review app submission guidelines
3. **Provide accurate info** - Names, descriptions, screenshots
4. **Prepare for review** - Have demo account ready
5. **Monitor status** - Check Dashboard and email

---

## Common Reasons for Rejection

| Issue | Prevention |
|-------|------------|
| Missing CSP | Configure `widgetCSP` correctly |
| Test endpoints | Use production URLs only |
| Unclear descriptions | Write clear, accurate tool descriptions |
| Poor UX | Test thoroughly in Developer Mode |
| Policy violation | Review submission guidelines |

---

## Related Resources

- **Previous:** [Test Your Integration](./03-testing-integration.md)
- **Guidelines:** [App Submission Guidelines](../../04-guidelines/01-submission-guidelines.md)
- **Policies:** [OpenAI Usage Policies](https://openai.com/policies)

---

## Submission Flow Diagram

```
┌─────────────────┐
│ Build & Test    │
│ (Developer Mode)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Org      │
│ & Owner Role    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Submit App      │
│ (Dashboard)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Review Queue    │
│ (Automated +    │
│  Manual)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Approved?       │
└──┬──────────────┘
   │
   ├─ No → Feedback → Resubmit
   │
   ▼ Yes
┌─────────────────┐
│ Publish App     │
│ (Directory)     │
└─────────────────┘
```
