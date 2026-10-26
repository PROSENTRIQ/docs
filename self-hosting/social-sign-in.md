# Social sign-in: Continue with Google and Microsoft

The hosted service already offers both. This page is for Enterprise customers
who want them on their own control plane.

The buttons appear on the console's sign-in and sign-up pages once a
provider's client ID and secret are configured. Each provider is independent:
enable one, both or neither.

## What users get

- **Work accounts only**: Google Workspace, and Microsoft 365 / Entra ID.
  Personal Gmail, Outlook.com and other personal Microsoft accounts are refused.
- **Sign-up**: the user enters an organization name, accepts the Terms and
  continues with their provider. The account and organization are created and
  the acceptance is recorded.
- **Sign-in**: the provider identity is linked to the account the first time.
  An existing password account with the same email is linked only when the
  provider vouches for the email; otherwise Prosentriq emails a confirmation
  link first.
- **No shortcuts**: TOTP MFA, an organization's enforced SSO and the Terms
  still apply.

## Redirect URIs

Register these with the providers, with your console's URL. They must match
exactly: scheme, host, no trailing slash.

```
https://<your console>/v2/auth/social/google/callback
https://<your console>/v2/auth/social/microsoft/callback
```

The console's web server passes `/v2` through to the API; the shipped
configurations do this.

Provider consoles rename menus from time to time. If a label below doesn't
match, look for the closest equivalent.

## Google (Google Workspace accounts)

1. **Project.** At https://console.cloud.google.com, create a project. Use a
   separate one for test environments.
2. **Branding** (Google Auth Platform → Branding): your app name, a support
   email, your home page, privacy policy and terms URLs, and your authorized
   domain (proven in Google Search Console).
3. **Audience**: *External* if users from other Workspace organizations sign
   in, otherwise *Internal*. For External, **Publish app** to move it to
   *In production*.
4. **Data access (scopes)**: only `openid`, `email` and `profile`. These are
   non-sensitive, so no security assessment is needed.
5. **Clients → Create client → Web application**, with the Google redirect URI
   above. No JavaScript origins are needed.
6. Set:
   ```
   PROSENTRIQ_GOOGLE_CLIENT_ID=…apps.googleusercontent.com
   PROSENTRIQ_GOOGLE_CLIENT_SECRET=…
   ```

A Workspace administrator can block third-party apps (Admin console →
Security → API controls). If users see "access blocked", their administrator
must mark the app as trusted.

## Microsoft (work and school accounts)

1. **Register the app** at https://entra.microsoft.com → App registrations →
   New registration. Supported account types: **Accounts in any organizational
   directory (Multitenant)**, or single-tenant for your own directory only. Do
   **not** include personal Microsoft accounts. Redirect URI: platform **Web**,
   the Microsoft redirect URI above.
2. **Client secret**: Certificates & secrets → New client secret. Copy its
   **Value** at once (it is shown once; not the Secret ID). Secrets expire after
   at most 24 months, so note the rotation date.
3. **Optional claims** (important for security): Token configuration → Add
   optional claim → **ID** token → **`email`** and **`xms_edov`**. `xms_edov`
   tells Prosentriq that the user's tenant has verified the domain of their
   email. Without it Prosentriq can't trust the email claim (the "nOAuth"
   attack), and every first Microsoft sign-in needs an emailed confirmation.
   If `xms_edov` isn't listed, add it in **Manifest** under
   `optionalClaims.idToken`: `{"name": "xms_edov", "essential": false}`.
4. **API permissions**: keep only Microsoft Graph delegated `openid`, `email`
   and `profile`.
5. **Publisher verification** (Branding & properties) is recommended for
   multitenant apps: many tenants only let users consent to verified publishers.
6. Set:
   ```
   PROSENTRIQ_MICROSOFT_CLIENT_ID=00000000-…
   PROSENTRIQ_MICROSOFT_CLIENT_SECRET=…
   ```

If a tenant requires admin consent, an administrator approves the app once:
`https://login.microsoftonline.com/<tenant id>/adminconsent?client_id=<client id>`

## Apply

Put the variables where the rest of your configuration lives (the Compose
`.env`, the Helm chart's Secret, or the systemd environment file) and restart
the API. In production the API refuses to start if a provider has an ID
without a secret, or a secret without an ID.
