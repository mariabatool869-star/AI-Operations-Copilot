"""
The Agent - ties all three tools together and reasons about which to call.

REAL PATH (preferred):
Uses Claude with real tool-calling via either:
  1) Amazon Bedrock (AWS credentials / your free AWS credits) — recommended
  2) Direct Anthropic API (ANTHROPIC_API_KEY)

FALLBACK PATH:
A simple, transparent, rule-based stand-in when no cloud credentials are set.
"""

import os
import json

from tools.sensor_tool import check_sensor_status
from tools.failure_risk_tool import predict_failure_risk
from tools.document_search_tool import search_maintenance_logs

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
AWS_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
# Set USE_BEDROCK=1 (default) to prefer Bedrock when AWS creds exist.
# Set USE_BEDROCK=0 to force direct Anthropic API when both are available.
USE_BEDROCK = os.environ.get("USE_BEDROCK", "1").strip().lower() not in ("0", "false", "no")
# DEMO_MODE=1 forces rule-based fallback (no Bedrock / Anthropic calls).
# Used by the public Streamlit demo so AWS credits are never spent.
DEMO_MODE = os.environ.get("DEMO_MODE", "0").strip().lower() in ("1", "true", "yes")

# Claude on Bedrock model ID (Sonnet 4.5). Change if your region uses a different ID.
BEDROCK_MODEL = os.environ.get(
    "BEDROCK_MODEL",
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
)
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")


def _has_aws_credentials() -> bool:
    if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
        return True
    # Shared credentials / SSO / instance profile via boto3
    try:
        import boto3

        session = boto3.Session()
        creds = session.get_credentials()
        return creds is not None
    except Exception:
        return False


def get_agent_mode() -> str:
    if DEMO_MODE:
        return "PUBLIC DEMO (fallback only — no cloud LLM calls)"
    if USE_BEDROCK and _has_aws_credentials():
        return "REAL Claude via Amazon Bedrock (AWS credits)"
    if ANTHROPIC_API_KEY:
        return "REAL Claude API (direct Anthropic key)"
    return (
        "FALLBACK (rule-based demo mode - set AWS credentials for Bedrock "
        "or ANTHROPIC_API_KEY for direct API)"
    )


# --- Tool definitions the AI is told about (name, description, inputs) ---
TOOL_DEFINITIONS = [
    {
        "name": "check_sensor_status",
        "description": "Check whether a named asset's current sensor readings (vibration, bearing temperature, pressure) look unusual compared to its normal operating baseline.",
        "input_schema": {
            "type": "object",
            "properties": {"asset_id": {"type": "string", "description": "Asset tag, e.g. 'P-104'"}},
            "required": ["asset_id"],
        },
    },
    {
        "name": "predict_failure_risk",
        "description": "Predict probability of mechanical failure given operating conditions (temperature, speed, torque, tool wear), using a model trained on real historical failure data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_type": {"type": "string", "enum": ["L", "M", "H"]},
                "air_temp_k": {"type": "number"},
                "process_temp_k": {"type": "number"},
                "rotational_speed_rpm": {"type": "number"},
                "torque_nm": {"type": "number"},
                "tool_wear_min": {"type": "number"},
            },
            "required": [
                "product_type",
                "air_temp_k",
                "process_temp_k",
                "rotational_speed_rpm",
                "torque_nm",
                "tool_wear_min",
            ],
        },
    },
    {
        "name": "search_maintenance_logs",
        "description": "Search historical maintenance/inspection log entries by meaning, to find past issues related to a topic or asset.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

TOOL_FUNCTIONS = {
    "check_sensor_status": lambda args: check_sensor_status(args["asset_id"]),
    "predict_failure_risk": lambda args: predict_failure_risk(**args),
    "search_maintenance_logs": lambda args: search_maintenance_logs(args["query"]),
}

SYSTEM_PROMPT = """You are an AI operations copilot for an industrial plant. Engineers ask you
about the status of assets. You have tools to check live sensor status, predict failure risk
from historical patterns, and search past maintenance logs. Use whichever tools are relevant
to answer thoroughly, then give a clear, plain-English summary with a recommendation. Always
state that final decisions must be confirmed by a qualified engineer - you assist, you do not
replace human judgment on safety-critical decisions."""


def _make_client_and_model():
    """Return (client, model_id) for real Claude tool-calling."""
    import anthropic

    if USE_BEDROCK and _has_aws_credentials():
        client = anthropic.AnthropicBedrock(aws_region=AWS_REGION)
        return client, BEDROCK_MODEL

    if ANTHROPIC_API_KEY:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return client, ANTHROPIC_MODEL

    raise RuntimeError("No Bedrock/AWS credentials or ANTHROPIC_API_KEY configured")


def run_agent_real(user_question: str) -> str:
    """Real implementation using Claude with tool calling (Bedrock or Anthropic API)."""
    client, model = _make_client_and_model()

    messages = [{"role": "user", "content": user_question}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_FUNCTIONS[block.name](block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})


def run_agent_fallback(user_question: str) -> str:
    """
    Transparent, rule-based stand-in for demonstration when no cloud API
    credentials are available. Mimics simple keyword-based tool selection.
    """
    question_lower = user_question.lower()
    findings = []

    import re

    asset_ids = re.findall(r"\b[A-Z]-?\d+\b", user_question.upper())

    if any(
        w in question_lower
        for w in ["sensor", "vibration", "reading", "status", "how is", "how's", "anomal", "current"]
    ):
        for asset_id in asset_ids or ["P-104"]:
            findings.append(("check_sensor_status", check_sensor_status(asset_id)))

    if any(w in question_lower for w in ["risk", "likely", "fail", "probability"]):
        findings.append(("predict_failure_risk", predict_failure_risk("M", 302.0, 312.0, 1350, 62.0, 200)))

    if any(w in question_lower for w in ["log", "history", "past", "previous", "leak", "corrosion"]):
        findings.append(("search_maintenance_logs", search_maintenance_logs(user_question)))

    if not findings:
        for asset_id in asset_ids or ["P-104"]:
            findings.append(("check_sensor_status", check_sensor_status(asset_id)))

    summary_lines = [
        "**Public demo mode** — rule-based tool selection (not live Claude / Bedrock).\n",
        "The same tools below power the real agent; only tool *choice* is keyword-based here.\n",
    ]
    for tool_name, result in findings:
        summary_lines.append(f"**Tool:** `{tool_name}`\n```json\n{json.dumps(result, indent=2)}\n```\n")
    summary_lines.append(
        "_Note: final maintenance decisions should be confirmed by a qualified engineer._"
    )
    return "\n".join(summary_lines)


def ask_copilot(user_question: str) -> str:
    # Public / Streamlit demo: never call Bedrock or Anthropic
    if DEMO_MODE:
        return run_agent_fallback(user_question)
    if (USE_BEDROCK and _has_aws_credentials()) or ANTHROPIC_API_KEY:
        try:
            return run_agent_real(user_question)
        except Exception as e:
            print(f"Real agent call failed ({e}), using fallback")
    return run_agent_fallback(user_question)


if __name__ == "__main__":
    print(ask_copilot("How is pump P-104 doing, and has it had any issues before?"))
    print("\n" + "=" * 60 + "\n")
    print(ask_copilot("What's the failure risk for compressor C-7?"))
