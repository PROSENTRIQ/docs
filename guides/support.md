# Getting help

Open a support case in the console and the whole conversation stays there,
with an email whenever someone answers.

## Opening a case

**Help → Contact support** (or **Support → New case**). Say what's happening,
how serious it is, and describe it. You can attach how the service runs for
you: your plan, the versions and health of your sensors, open circuit breakers
and failed deliveries. That's what support can already see; never host names,
addresses or security events.

- **Prosentriq is blocking something it shouldn't**: stop it first. Undo the
  block in **Approvals & actions** (it lifts on every host at once), lower the
  **Autonomy Dial**, or, on a host you can't reach otherwise, run
  `sudo prosentriq-ctl kill-switch`. Then open the case as **Urgent**.
- **A sensor won't install, connect or report**: on the host's dashboard,
  **Help → Copy diagnostics for support**, and paste them into the case. They
  hold the engine's state, never the host's name, addresses or traffic.
- **A detection looks wrong**: use **Ask support** on the incident.

Never put passwords, API keys or codes in a case. Prosentriq never asks for
them; the console asks you to check if something looks like one.

Can't sign in? Write to support@prosentriq.com from your account's address.

## Severity and response times

| Severity | Means |
|---|---|
| Urgent | Production is affected: legitimate traffic is being blocked, or Prosentriq is down for you |
| High | Something important doesn't work and there's no workaround |
| Normal | A question, or a problem with a workaround |

| Plan | First reply |
|---|---|
| Free | As soon as we can, on business days |
| Starter | By the next business day |
| Pro | Within 4 business hours |
| Enterprise | Urgent: within 1 hour, round the clock. Others: within 4 business hours. A named contact |

Business hours are Monday to Friday, 09:00 to 18:00 East Africa Time (UTC+3),
except Kenyan public holidays. The case shows when to expect the first reply.

## Following a case

The case page updates by itself: new replies appear within seconds, and you
see when support has it open. Reply from the page (Ctrl or ⌘ + Enter sends).
Replies to our emails aren't read, so the conversation stays in one place.

**Mark resolved** when you're done. You can reopen a resolved case, or just
reply to it, for 14 days; after that it closes and you open a new one. A case
waiting on you for 10 days resolves by itself.

## When support needs to see your data

Prosentriq staff never see your incidents, hosts or integrations unless an
owner allows it. When it would help, support asks on the case: what, for how
long and why. An owner allows or declines it there; owners also get an email.
Access ends when it expires or when you revoke it in **Support → Data access**,
and every look is in your audit log. See [Support access](access.md#support-access).

## If you buy through an MSP

Your managed service provider answers your cases first, and can bring in
Prosentriq. If it does, we see that case's conversation and answer it in the
same thread, on your plan's response time.

## If you are an MSP

Your customers' cases appear in **Support → Customers' cases**, and your
support email (set in your branding, or your owners and admins) gets an email
for each. Answer them there. **Escalate to Prosentriq** when you need us: we
then see that conversation, and nothing else of your customers'. A case you
open while working in a customer's organization comes straight to us.
