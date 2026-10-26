# Teams, roles, API keys, MFA and single sign-on

## Members and roles

Invite people in **Settings → Members**. An invitation is emailed and is valid
for 7 days. Each person has one role in the organization:

| Role | Can |
|---|---|
| **Owner** | Everything, including the plan and billing, SSO, branding, organization settings, support access and deleting the organization |
| **Admin** | Everything except the owner-only settings above |
| **Analyst** | Read everything, triage incidents, approve, reject and undo actions, block and isolate by hand, and manage rules, the allowlist and honeytokens |
| **Auditor** | Read everything, generate and download evidence, and manage auditor links. Changes nothing |

The full permission matrix is in the [API overview](../api/README.md#roles-and-permissions).
Nobody can give a role higher than their own. An organization always has at
least one owner.

An account belongs to one organization. MSP staff reach their customers'
organizations through the MSP (see [Managed service providers](msp.md)).

## Signing in

- **Email and password.** Passwords are hashed with Argon2id. Reset a lost
  password from the sign-in page; the link is single-use and expires.
- **Continue with Google or Continue with Microsoft** (work and school accounts).
- **Your own identity provider**, through single sign-on (below).

Console sessions last 12 hours. The session cookie is `HttpOnly`, `Secure` and
`SameSite=Strict`, and every change also needs a CSRF token.

## Two-factor authentication (TOTP)

**Settings → My security → Set up an authenticator app.** Scan the QR code
with any TOTP app (1Password, Google Authenticator, Authy, …), confirm with a
code, and store the single-use recovery codes it shows you. Each code can be
used only once, including during an outage.

Turn it on for every member. **Settings → Members** warns you about members
who haven't. Members who have set up MFA are asked for their code even when
they sign in through single sign-on.

## API keys

**Settings → API keys → Create key.** Give it a name that says what uses it
and the fewest [scopes](../api/README.md#api-key-scopes) it needs. The key is
shown once. Only its hash is stored, and the list shows when each key was last
used. Revoke a key at any time; it stops working at once.

## Single sign-on (Starter and up)

Prosentriq supports any OpenID Connect provider: Okta, Microsoft Entra ID,
Google Workspace, Auth0, JumpCloud, Keycloak and others. It uses the
authorization-code flow with PKCE, checks the ID token against the provider's
published keys, and checks a nonce.

### 1. Verify your email domains

**Settings → Single sign-on → Verified domains → Add domain.** Publish the TXT
record it shows in your DNS:

```
_prosentriq-challenge.example.com.  TXT  "prosentriq-domain-verification=<token>"
```

Then choose **Verify**. Keep the record published: it is re-checked daily. The
token is unique to your organization and domain.
New accounts are created through SSO only on verified domains, so your
identity provider can't vouch for addresses it doesn't own.

### 2. Register Prosentriq at your identity provider

Create an OIDC web application at your provider. Prosentriq shows you the
**redirect URI** to register once you save the settings below. It has the form
`https://api.prosentriq.com/v2/auth/sso/<your organization>/callback`.

### 3. Configure SSO in Prosentriq

In **Settings → Single sign-on** enter:

| Field | |
|---|---|
| Issuer URL | Your provider's issuer, for example `https://example.okta.com` |
| Client ID, client secret | From the application you created |
| Allowed email domains | Optional. Leave empty to allow any of your verified domains |
| Role for new users | `analyst` (default), `auditor` or `admin`. People who sign in for the first time join with this role |
| Require SSO for everyone except owners | Optional. Owners keep password sign-in as a way in if your provider is down |

Share the **sign-in URL** it shows you with your team.

On a downgrade below Starter, SSO pauses. Members then sign in with a password,
Google or Microsoft.

## Support access

Prosentriq staff can't see your incidents, hosts or integrations. They see only
how the service runs for you (plan, sensor health, usage). To let support look
at your data while helping you, an owner grants time-limited access in
**Settings → Support access**: 1 hour, 24 hours, 3 days or 7 days, with a
reason. Every look at your data is recorded in your audit log as a Prosentriq
staff action. Revoke a grant at any time.

## Branding

Owners can white-label the console and reports (product name and more) in
**Settings → Organization → Branding**. MSP customer organizations inherit their MSP's branding.
