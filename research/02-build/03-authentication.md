# Authentication

**Source:** https://developers.openai.com/apps-sdk/build/auth
**Phase:** Build
**Last Updated:** February 2026

---

## Overview

Many Apps SDK apps can operate in read-only, anonymous mode. Customer-specific data or write actions should authenticate users using OAuth 2.1.

### OAuth Components

| Component | Role |
|-----------|------|
| **Resource Server** | Your MCP server - exposes tools, verifies access tokens |
| **Authorization Server** | Identity provider (Auth0, Okta, Cognito) - issues tokens |
| **Client** | ChatGPT - supports dynamic client registration and PKCE |

---

## Custom Auth with OAuth 2.1

### Protected Resource Metadata

Your MCP server must expose metadata at:

```
GET https://your-mcp.example.com/.well-known/oauth-protected-resource
```

**Response:**
```json
{
  "resource": "https://your-mcp.example.com",
  "authorization_servers": ["https://auth.yourcompany.com"],
  "scopes_supported": ["files:read", "files:write"],
  "resource_documentation": "https://yourcompany.com/docs/mcp"
}
```

**401 Challenge Response:**
```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://your-mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

---

### OAuth Metadata

Your identity provider must expose a discovery document:

**OAuth 2.0:**
```
https://auth.yourcompany.com/.well-known/oauth-authorization-server
```

**OpenID Connect:**
```
https://auth.yourcompany.com/.well-known/openid-configuration
```

**Response:**
```json
{
  "issuer": "https://auth.yourcompany.com",
  "authorization_endpoint": "https://auth.yourcompany.com/oauth2/v1/authorize",
  "token_endpoint": "https://auth.yourcompany.com/oauth2/v1/token",
  "registration_endpoint": "https://auth.yourcompany.com/oauth2/v1/register",
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["files:read", "files:write"]
}
```

**Required Fields:**
- `authorization_endpoint`, `token_endpoint` - OAuth flow URLs
- `registration_endpoint` - Enables Dynamic Client Registration (DCR)
- `code_challenge_methods_supported` - Must include `S256` for PKCE

---

### Redirect URIs

Allowlist these redirect URIs:

| Environment | URI |
|-------------|-----|
| **Production** | `https://chatgpt.com/connector_platform_oauth_redirect` |
| **App Review** | `https://platform.openai.com/apps-manage/oauth` |

---

### Echo `resource` Parameter

ChatGPT appends `resource` parameter to authorization and token requests:

```
resource=https%3A%2F%2Fyour-mcp.example.com
```

Configure your authorization server to:
1. Copy `resource` into access token (commonly `aud` claim)
2. Verify token was minted for your server
3. Reject tokens without expected audience or scopes

---

## OAuth Flow

```
1. ChatGPT queries protected resource metadata
   ────────────────────────────────────────>

2. ChatGPT registers via DCR, obtains client_id
   ────────────────────────────────────────>

3. User invokes tool → ChatGPT launches OAuth
   ────────────────────────────────────────>

4. ChatGPT exchanges code for access token
   ────────────────────────────────────────>

5. ChatGPT attaches token to MCP requests
   Authorization: Bearer <token>
```

### Your Server Responsibilities

On every request, verify:
1. **Signature validation** - JWKS from authorization server
2. **Issuer** - Matches expected `iss`
3. **Audience** - Token minted for your server
4. **Expiry** - Check `exp` and `nbf`
5. **Scopes** - Required permissions present

**On failure:** Return `401 Unauthorized` with `WWW-Authenticate` header

---

## Triggering Authentication UI

ChatGPT surfaces OAuth linking UI when both conditions are met:

1. **Metadata published** - `securitySchemes` + resource metadata document
2. **Runtime errors** - Tool response includes `_meta["mcp/www_authenticate"]`

### Tool Security Schemes

Two scheme types available:

| Scheme | Description |
|--------|-------------|
| `noauth` | Tool callable anonymously |
| `oauth2` | Tool needs OAuth access token |

**Example (Public + Optional Auth) - TypeScript:**
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

server.registerTool(
  "search",
  {
    title: "Public Search",
    description: "Search public documents.",
    inputSchema: {
      type: "object",
      properties: { q: { type: "string" } },
      required: ["q"],
    },
    securitySchemes: [
      { type: "noauth" },
      { type: "oauth2", scopes: ["search.read"] },
    ],
  },
  async ({ input }) => {
    return {
      content: [{ type: "text", text: `Results for ${input.q}` }],
      structuredContent: {},
    };
  }
);
```

**Example (Auth Required):**
```typescript
server.registerTool(
  "create_doc",
  {
    title: "Create Document",
    description: "Make a new doc in your account.",
    inputSchema: {
      type: "object",
      properties: { title: { type: "string" } },
      required: ["title"],
    },
    securitySchemes: [{ type: "oauth2", scopes: ["docs.write"] }],
  },
  async ({ input }) => {
    return {
      content: [{ type: "text", text: `Created doc: ${input.title}` }],
      structuredContent: {},
    };
  }
);
```

### Emit WWW-Authenticate

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Authentication required: no access token provided."
      }
    ],
    "_meta": {
      "mcp/www_authenticate": [
        "'Bearer resource_metadata=\"https://your-mcp.example.com/.well-known/oauth-protected-resource\", error=\"insufficient_scope\", error_description=\"You need to login to continue\"'"
      ]
    },
    "isError": true
  }
}
```

---

## Choosing an Identity Provider

### Recommended Providers

| Provider | Resources |
|----------|-----------|
| **Auth0** | [Configuring Auth0 for MCP](https://auth0.com/docs) |
| **Stytch** | [Stytch MCP Guide](https://stytch.com/docs) |
| **Okta** | Built-in OAuth 2.1 support |
| **Cognito** | AWS native integration |

**Strong recommendation:** Use an established identity provider rather than implementing from scratch.

---

## Client Identification

### Current State

Only reliable control is network-level filtering (allowlist ChatGPT's published egress IP ranges).

ChatGPT does **not** support:
- Client credentials grants
- Service accounts
- JWT bearer assertions
- Custom API keys
- mTLS certificates

### Future: Client Metadata Documents (CMID)

CMID will provide:
- Stable, signed declaration of ChatGPT's identity
- HTTPS-hosted metadata document
- Direct solution to client identification problem

**Status:** In draft. Continue supporting DCR until CMID lands.

---

## SDK Token Verification

### Python SDK

```python
from mcp.server.auth import verify_token

# In your tool handler
token = request.headers.get("Authorization", "").replace("Bearer ", "")
claims = await verify_token(token)

if not claims:
    return {"error": "invalid_token"}
```

### TypeScript SDK

```typescript
import { verifyToken } from "@modelcontextprotocol/sdk/auth";

// In your tool handler
const authHeader = request.headers.get("authorization") ?? "";
const token = authHeader.replace("Bearer ", "");

const claims = await verifyToken(token);

if (!claims) {
  return { error: "invalid_token" };
}
```

---

## Testing and Rollout

1. **Local Testing** - Development tenant with short-lived tokens
2. **Dogfood** - Gate access to trusted testers
3. **Rotation** - Plan for token revocation and refresh
4. **Debugging** - Use MCP Inspector Auth settings

### OAuth Debugging Checklist

- [ ] Protected resource metadata accessible
- [ ] OAuth discovery document returns expected fields
- [ ] `code_challenge_methods_supported` includes `S256`
- [ ] Redirect URIs allowlisted
- [ ] `resource` parameter echoed in token
- [ ] Token verification validates all claims

---

## Best Practices

1. **Verify tokens on every request** - Never skip validation
2. **Use PKCE** - Required for security
3. **Return helpful errors** - Guide users to fix auth issues
4. **Log verification failures** - Aid debugging
5. **Rotate tokens regularly** - Limit exposure window

---

## Common Pitfalls

### Mistake 1: Missing PKCE Support

❌ **Don't:** Omit `code_challenge_methods_supported`

✅ **Do:** Always include `S256` in supported methods

---

### Mistake 2: Not Echoing `resource`

❌ **Don't:** Ignore `resource` parameter in flow

✅ **Do:** Copy `resource` into token's `aud` claim

---

### Mistake 3: Skipping Token Verification

❌ **Don't:** Trust tokens without validation

✅ **Do:** Verify signature, issuer, audience, expiry, scopes

---

## Related Resources

- **Previous:** [Build ChatGPT UI](./02-chatgpt-ui.md)
- **Next:** [State Management](./04-state-management.md)
- **MCP Auth Spec:** [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)

---

## Token Verification Example

```typescript
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';

const client = jwksClient({
  jwksUri: 'https://auth.yourcompany.com/.well-known/jwks.json'
});

function verifyToken(token: string) {
  return new Promise((resolve, reject) => {
    jwt.verify(token, getKey, {
      issuer: 'https://auth.yourcompany.com',
      audience: 'https://your-mcp.example.com',
      algorithms: ['RS256']
    }, (err, decoded) => {
      if (err) {
        reject(err);
      } else {
        resolve(decoded);
      }
    });
  });
}

function getKey(header, callback) {
  client.getSigningKey(header.kid, (err, key) => {
    callback(null, key.publicKey || key.rsaPublicKey);
  });
}
```
