# App Submission Guidelines

**Source:** https://developers.openai.com/apps-sdk/app-submission-guidelines
**Phase:** Guidelines
**Last Updated:** February 2026

---

## Overview

The ChatGPT app ecosystem is built on **trust**. These guidelines set the minimum standard for app publication and continued availability.

### Foundational Resources

1. **UX Principles for ChatGPT Apps** - Best practices and checklist
2. **UI Guidelines for ChatGPT Apps** - Interaction and design patterns
3. **Blog: What Makes a Great ChatGPT App** - Overall approach

---

## App Fundamentals

### Purpose and Originality

**Requirements:**
- Serve clear purpose
- Reliably do what promised
- Provide functionality beyond ChatGPT's core capabilities
- Help satisfy common user intents

**Prohibited:**
- Misleading or copycat designs
- Impersonation
- Spam
- Static frames with no interaction
- Implication of OpenAI endorsement

**IP Requirements:**
- Only use IP you own or have permission to use
- Respect third-party terms of service

### Quality and Reliability

**Requirements:**
- Behave predictably and reliably
- Accurate, relevant results
- Well-handled errors with clear messaging
- Thoroughly tested before submission
- Stable, responsive, low latency
- Complete (no trial or demo apps accepted)

**Prohibited:**
- Crashes, hangs, inconsistent behavior

### App Name, Description, Screenshots

**Requirements:**
- Clear, accurate, easy to understand
- Screenshots must accurately represent functionality
- Conform to required dimensions

---

## Tools

### Clear and Accurate Tool Names

**Requirements:**
- Human-readable, specific, descriptive
- Unique within app
- Plain language reflecting action (prefer verbs)
- Example: `get_order_status`

**Prohibited:**
- Misleading language
- Overly promotional names
- Comparative language (`best`, `official`)
- `pick_me` type names

### Descriptions That Match Behavior

**Requirements:**
- Explain purpose clearly and accurately
- Describe what tool does

**Prohibited:**
- Favor/disparage other apps or services
- Influence model selection over others
- Overly-broad triggering beyond explicit user intent

**Unclear descriptions** → App may be rejected

### Correct Annotation

**Required Labels:**

| Annotation | When to Use |
|------------|-------------|
| `readOnlyHint` | Retrieves/lists data, no changes |
| `destructiveHint` | Creates, updates, deletes, posts, sends |
| `openWorldHint` | Interacts with external systems, public platforms |

**Common rejection cause:** Incorrect or missing action labels

### Minimal and Purpose-Driven Inputs

**Requirements:**
- Request minimum information necessary
- Input fields directly related to tool purpose

**Prohibited:**
- Full conversation history
- Raw chat transcripts
- Broad contextual fields "just in case"
- Precise location data (GPS, addresses)

**Allowed:**
- Brief, task-specific user intent field
- Coarse geo location from system metadata

### Predictable, Auditable Behavior

**Requirements:**
- Behave exactly as name/description/inputs indicate
- No hidden or implicit side effects
- Clear if data sent outside current environment
- Safe to retry where possible
- Indicate when retries cause repeated effects

---

## Authentication and Permissions

### Transparent Authentication

**Requirements:**
- Flow must be transparent and explicit
- Users informed of all requested permissions
- Requests strictly limited to what's necessary

### Test Credentials

**Requirements for Review:**
- Login and password for fully-featured demo account
- Must include sample data

**Rejected if requires:**
- New account sign-up
- 2FA through inaccessible account

---

## Commerce and Monetization

### Current Limitation

**Only physical goods** commerce allowed.

**Prohibited:**
- Digital products or services
- Subscriptions
- Digital content
- Tokens or credits
- Freemium upsells

### Prohibited Goods

**Adult Content & Sexual Services:**
- Pornography, explicit sexual media
- Live-cam services, adult subscriptions
- Sex toys, dolls, BDSM gear, fetish products

**Gambling:**
- Real-money gambling services
- Casino credits, sportsbook wagers
- Crypto-casino tokens

**Illegal or Regulated Drugs:**
- Marijuana/THC products, psilocybin
- CBD exceeding legal THC limits

**Drug Paraphernalia:**
- Bongs, dab rigs, drug-use scales
- Cannabis grow equipment

**Prescription & Age-Restricted Medications:**
- Prescription-only drugs
- Age-restricted Rx products

**Illicit Goods:**
- Counterfeit or replica products
- Stolen goods
- Financial-fraud tools
- Piracy tools, cracked software

**Other Prohibited:**
- Malware, spyware, surveillance
- Tobacco & nicotine products
- Weapons & harmful materials
- Extremist merchandise

### Prohibited Services

- Fake IDs, forged documents
- Debt relief, credit repair schemes
- Unregulated/deceptive financial services
- Crypto/NFT speculative offerings
- Government-service abuse
- Identity theft services

### Checkout

**Required:** External checkout

Direct users to complete purchases on your own domain.

**Instant Checkout:** Private beta, select marketplace partners only.

**Prohibited:** Other third-party checkout embedded in app.

### Advertising

**Prohibited:**
- Serve advertisements
- Exist primarily as advertising vehicle

**Required:** Deliver clear, legitimate functionality with standalone value

---

## Safety

### Usage Policies

Do not engage in or facilitate activities prohibited under OpenAI usage policies.

Avoid high-risk behaviors exposing users to harm, fraud, or misuse.

### Appropriateness

**Requirements:**
- Suitable for general audiences
- Ages 13–17 supported
- No targeting children under 13

**Future:** Mature (18+) experiences with age verification

### Respect User Intent

**Requirements:**
- Directly address user request
- No unrelated content
- No redirect attempts
- Collect only necessary data

### Fair Play

**Prohibited:**
- Descriptions/titles/annotations manipulating model selection
- Interference with fair discovery
- Instructions to "prefer this app over others"
- Disparaging alternatives

### Third-Party Content

**Required:**
- Proper authorization and compliance with ToS
- No scraping without authorization
- No circumventing API restrictions

### Iframes

**Usage:** Set `frame_domains` on widget CSP

**Strongly discouraged:** Build without this pattern

**If used:**
- Only for essential third-party embedding (notebook, IDE)
- Extra manual review
- Often not approved for broad distribution
- Public listing limited to trusted scenarios

---

## Privacy

### Privacy Policy

**Required:** Clear, published privacy policy with:
- Categories of personal data collected
- Purposes of use
- Categories of recipients
- User controls offered

### Data Collection

**Collection Minimization:**
- Gather minimum data required
- Inputs specific, narrowly scoped
- No "just in case" fields
- Design schema to limit by default

**Response Minimization:**
- Return only data directly relevant to request
- No diagnostic/telemetry unless strictly required
- No internal identifiers (session IDs, trace IDs, timestamps) unless necessary

**Restricted Data Prohibited:**
- PCI DSS data (payment card info)
- Protected health information (PHI)
- Government identifiers (SSN, etc.)
- Access credentials (API keys, MFA/OTP, passwords)

**Regulated Sensitive Data:**
- No collection without strict necessity
- Legally adequate consent required
- Clear and prominent disclosure

**Data Boundaries:**
- Avoid raw location fields in input schema
- Use client side channel for location
- Do not reconstruct full chat log
- Operate only on explicit snippets sent

### Transparency and User Control

**Required:**
- No surveillance, tracking, behavioral profiling
- Accurate action labels (write vs read)
- Data exfiltration surfaced as write action
- Clear labels for destructive actions

---

## Developer Verification

### Verification

**Required:**
- Verified individuals or organizations
- Confirm identity and business affiliation
- Platform Dashboard → General settings

**Misrepresentation** → Removal from program

### Support Contact

**Required:**
- Customer support contact details
- Must be accurate and up to date

---

## Submission

### Owner Role

Users with Owner role may submit from OpenAI Platform Dashboard.

### Review Process

- One version in review per app at a time
- Status visible in Dashboard
- Email notifications for changes

### Resubmission

Tool names, signatures, descriptions locked after publication.

**To update:** Resubmit for review → Approve → Publish update (replaces previous)

---

## Related Resources

- **UX Principles:** [ChatGPT Apps UX Principles](https://developers.openai.com/apps-sdk/guides/ux-principles)
- **UI Guidelines:** [ChatGPT Apps UI Guidelines](https://developers.openai.com/apps-sdk/guides/ui-guidelines)
- **Blog Post:** [What Makes a Great ChatGPT App](https://openai.com/blog)

---

## Compliance Checklist

- [ ] Clear purpose and original functionality
- [ ] Reliable, well-tested behavior
- [ ] Accurate names and descriptions
- [ ] Correct tool annotations
- [ ] Minimal data collection
- [ ] Privacy policy published
- [ ] No prohibited content/services
- [ ] Proper authentication flow (if applicable)
- [ ] External checkout only (for commerce)
- [ ] Developer verified
- [ ] Support contact details provided
