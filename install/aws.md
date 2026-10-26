# AWS, agentless

The cloud collector reads AWS VPC Flow Logs and CloudTrail from S3 (or from
exported files) and sends them as Prosentriq events. Nothing is installed in
your instances. It ships in the [Python SDK](https://github.com/PROSENTRIQ/prosentriq-sdk-python)
as `prosentriq-sensor cloud`. Cloud collectors are free on every plan.

## What it detects

- **VPC Flow Logs** (the default v2 format, or any custom format with a header
  line) become network activity events. Rejected flows are also aggregated per
  source: one source touching 15 or more distinct ports is reported as a port
  scan, the same signal and threshold the host engine uses.
- **CloudTrail** records become cloud API activity events. Console logins
  become authentication events, so the brute-force-then-success chain applies
  to your AWS console too.

Each record gets a deterministic id, so re-reading a file never counts it
twice. The collector remembers what it has read in `/var/lib/prosentriq/cloud.state`
(`--state` to change it).

## Install and enroll

```bash
pip install --pre 'prosentriq-sdk[aws]'
prosentriq-sensor enroll --api-base https://api.prosentriq.com --enroll-key-file key.txt \
    --type cloud_collector --out aws.json
```

## Run it

```bash
prosentriq-sensor cloud --config aws.json --kind vpc-flow   --s3 my-flow-logs-bucket/AWSLogs/ --loop 300
prosentriq-sensor cloud --config aws.json --kind cloudtrail --s3 my-trail-bucket/AWSLogs/   --loop 300
```

`--loop 300` reads new objects every 5 minutes. `--path` reads exported files
from disk instead of S3.

## AWS permissions

The collector uses the standard AWS credential chain (instance profile, ECS
task role, environment or profile). It needs read access to the log objects:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": "arn:aws:s3:::my-flow-logs-bucket" },
    { "Effect": "Allow", "Action": ["s3:GetObject"], "Resource": "arn:aws:s3:::my-flow-logs-bucket/AWSLogs/*" }
  ]
}
```

If the bucket is encrypted with a customer-managed KMS key, also allow
`kms:Decrypt` on that key.

## Other clouds

Google Cloud and Azure collectors are not built yet. Until then, export their
logs to syslog or CEF and use the [log relay](log-sources.md), or send events
yourself with the [SDK](custom-sensor.md).
