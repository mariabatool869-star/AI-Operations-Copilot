# Setup Amazon Bedrock (Claude) with your free AWS $200 credits
# ============================================================
# Your AWS credits pay for Claude through Amazon Bedrock.
# You do NOT need a separate Anthropic account or API key.

## 1. Install AWS CLI (one time)

Download and install: https://aws.amazon.com/cli/

Or with winget:
  winget install Amazon.AWSCLI

Close and reopen PowerShell after install, then check:
  aws --version

## 2. Create an IAM access key (in AWS Console)

1. Sign in: https://console.aws.amazon.com/
2. Go to IAM → Users → Create user (or use an existing user)
3. Attach permission policy: AmazonBedrockFullAccess
   (for learning; later you can tighten this)
4. Security credentials → Create access key → "Command Line Interface (CLI)"
5. Copy Access Key ID and Secret Access Key (shown once)

## 3. Configure credentials on this PC

  aws configure

Enter:
  AWS Access Key ID:     <paste>
  AWS Secret Access Key: <paste>
  Default region name:   us-east-1
  Default output format: json

## 4. Enable Claude on Bedrock (required once)

1. Open Amazon Bedrock console (same region, e.g. us-east-1):
   https://console.aws.amazon.com/bedrock/
2. Open Model catalog → pick an Anthropic Claude model (e.g. Claude Sonnet 4.5)
3. Submit the short Anthropic use-case form if asked (usually instant approval)
4. Optional: open Playground and send a test prompt
   (also helps unlock free-tier onboarding credits)

## 5. Run this project

From the project folder (with venv activated):

  python main.py

You should see:
  AI Operations Copilot — running in REAL Claude via Amazon Bedrock (AWS credits)

## Troubleshooting

- "AccessDeniedException" / model not enabled → finish step 4 in that region
- "ValidationException" on model id → set BEDROCK_MODEL to a model ID shown in your Bedrock console
- Still FALLBACK mode → aws configure did not save, or wrong profile; check:
    aws sts get-caller-identity
- Region mismatch → set AWS_REGION to the region where you enabled the model
