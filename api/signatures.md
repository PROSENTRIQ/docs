# Signatures: webhooks, SOAR and evidence

Prosentriq signs what it sends you, and checks the signature on what you send
it. There are two schemes:

| | Scheme | Key |
|---|---|---|
| Outgoing webhooks, incoming SOAR actions | HMAC-SHA256 with a shared secret, in the `X-Prosentriq-Signature` header | A per-destination or per-organization secret |
| Evidence packs, the Immunity Network feed, federation | Ed25519 over canonical JSON | The control plane's signing key, published |

## HMAC: `X-Prosentriq-Signature`

```
X-Prosentriq-Signature: t=1792300800,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
```

- `t` is the Unix time the request was signed.
- `v1` is the lowercase hex HMAC-SHA256 of the string `"<t>." + raw body`,
  keyed with the secret.
- A signature is accepted for 5 minutes either side of `t`.

### Verifying a webhook (receiver side)

When you add a webhook destination, Prosentriq generates a signing secret
(`whsec_…`) unless you give your own. It is shown **once**, when you create the
destination. Each delivery is a `POST` with:

| Header | |
|---|---|
| `Content-Type` | `application/json` |
| `User-Agent` | `Prosentriq-Webhooks/2` |
| `X-Prosentriq-Event` | The event type, for example `incident.opened` |
| `X-Prosentriq-Delivery` | A unique delivery id. Use it to drop duplicates |
| `X-Prosentriq-Signature` | As above |

Verify against the **raw** body bytes, before parsing the JSON:

```python
import hashlib, hmac, time

def verify(secret: str, header: str, body: bytes, tolerance: int = 300) -> bool:
    try:
        parts = dict(p.split("=", 1) for p in header.split(","))
        ts = int(parts["t"])
    except (ValueError, KeyError):
        return False
    if abs(time.time() - ts) > tolerance:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))
```

```javascript
// Node.js (Express: use express.raw({ type: "application/json" }) so req.body is a Buffer)
const crypto = require("crypto");
function verify(secret, header, body, tolerance = 300) {
  const parts = Object.fromEntries(header.split(",").map((p) => p.split("=", 2)));
  const ts = Number(parts.t);
  if (!ts || Math.abs(Date.now() / 1000 - ts) > tolerance) return false;
  const expected = crypto.createHmac("sha256", secret).update(`${ts}.`).update(body).digest("hex");
  const got = Buffer.from(parts.v1 || "", "utf8");
  return got.length === expected.length && crypto.timingSafeEqual(got, Buffer.from(expected, "utf8"));
}
```

Answer with any `2xx` status within 10 seconds. The payload format and retry
behaviour are in [Integrations](../guides/integrations.md#webhooks).

### Signing a SOAR request (sender side)

Rotate the organization's SOAR secret first (**Integrations → SOAR response actions → Rotate signing secret**, or
`POST /v2/soar/secret`). It is shown once. Then sign each request the same way:

```python
import hashlib, hmac, json, time, urllib.request

body = json.dumps({"action": "block", "target": "203.0.113.9", "ttl_seconds": 86400,
                   "reason": "Playbook 12: phishing infrastructure", "external_id": "case-4411"}).encode()
ts = int(time.time())
sig = hmac.new(SOAR_SECRET.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
req = urllib.request.Request("https://api.prosentriq.com/v2/soar/actions", data=body, method="POST", headers={
    "Authorization": f"Bearer {SOAR_API_KEY}",           # an API key with the soar scope
    "Content-Type": "application/json",
    "X-Prosentriq-Signature": f"t={ts},v1={sig}",
})
print(urllib.request.urlopen(req).read())
```

Each signature can be used once. See [SOAR response actions](../guides/soar.md).

## Ed25519: the control plane's signing key

Evidence packs, the Immunity Network feed and federation messages are signed
with Ed25519 over **canonical JSON**: keys sorted, no whitespace
(`","` and `":"` separators), UTF-8 without escaping non-ASCII characters.
A large document may instead be signed through a digest envelope: the
signature is then over the bytes `prosentriq-signed-digest/1\nsha512:` followed
by the lowercase hex SHA-512 of the canonical JSON, and the signature record
says `"digest": "sha512"`. Either way it is a plain Ed25519 signature.

### The hosted service's key

| | |
|---|---|
| Key id | `ed25519:3a25fd0db2998c1c` |
| Public key (raw Ed25519, base64) | `YKbnx1aWRT7gaTzLqqOBuV8xtPL2bTPL6cemluAvPwg=` |

It is also published on [prosentriq.com/security](https://prosentriq.com/security#signing-key),
in [security.txt](https://prosentriq.com/.well-known/security.txt), and by the
API at `GET /v2/public/signing-key` together with the key history and the
endorsements that link each key to the next. A key id is `ed25519:` plus the
first 16 hex digits of the SHA-256 of the raw public key.

A self-hosted control plane has its own key: `GET /v2/public/signing-key` on it.

### Verifying an evidence pack

A downloaded pack looks like this:

```json
{
  "pack": { … },
  "signature": { "alg": "Ed25519", "key_id": "ed25519:3a25fd0db2998c1c", "sha256": "…", "signature": "<base64>", "public_key": "<base64>" },
  "rfc3161_token_b64": null
}
```

Check it against the key **you** obtained from a published source, not the
`public_key` printed inside the file. Three ways:

1. **Offline, with the SDK** (`pip install --pre prosentriq-sdk`):

   ```python
   import base64, json
   from prosentriq_sdk.client import verify_signature

   doc = json.load(open("pack.json"))
   key = base64.b64decode("YKbnx1aWRT7gaTzLqqOBuV8xtPL2bTPL6cemluAvPwg=")
   print(verify_signature(doc["pack"], doc["signature"]["signature"], key))
   ```

2. **Offline, with any Ed25519 library**: canonicalize `pack` as described
   above, apply the digest envelope if the signature record says
   `"digest": "sha512"`, and verify.

3. **Online**: `POST /v2/public/evidence/verify` with
   `{"pack": …, "signature": "<base64>", "key_id": "ed25519:…"}` (or
   `"public_key"` instead of `"key_id"`). The answer is
   `{"valid": true, "checked_against_key": "…"}`.

If the pack carries an RFC 3161 timestamp token (`rfc3161_token_b64`), it
proves when the pack was signed. Check it with your TSA's certificate, for
example with `openssl ts -verify`.

### When the key changes

If a control plane changes its signing key, the previous key signs an
endorsement naming the next one. Sensors, auditors and federated control
planes follow that chain from the key they pinned, and old packs keep
verifying against the key that signed them. An unendorsed key is refused. See
[Signing keys](../self-hosting/signing-keys.md).
