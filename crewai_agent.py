import os
import sys
import time
from typing import Any, Dict

import requests

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

BASE_URL = "https://machineid.io"
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


def get_org_key() -> str:
    org_key = os.getenv("MACHINEID_ORG_KEY")
    if not org_key:
        raise RuntimeError(
            "Missing MACHINEID_ORG_KEY. Set it in your environment or via a .env file.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
        )
    return org_key


def get_device_id() -> str:
    return os.getenv("MACHINEID_DEVICE_ID", "crewai-agent-01")


def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {
        "x-org-key": org_key,
        "Content-Type": "application/json",
    }
    payload = {
        "deviceId": device_id,
    }

    print(f"→ Registering device '{device_id}' via {REGISTER_URL} ...")
    resp = requests.post(REGISTER_URL, headers=headers, json=payload, timeout=10)
    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from register response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    plan_tier = data.get("planTier")
    limit = data.get("limit")
    devices_used = data.get("devicesUsed")
    remaining = data.get("remaining")

    print(f"✔ register response: status={status}, handler={handler}")
    print("Registration summary:")
    print(f"  planTier    : {plan_tier}")
    print(f"  limit       : {limit}")
    print(f"  devicesUsed : {devices_used}")
    print(f"  remaining   : {remaining}")
    print()

    if status == "limit_reached":
        print("🚫 Plan limit reached on register. Your CrewAI agents should treat this as 'do not start'.")
    return data


def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {
        "x-org-key": org_key,
    }
    params = {
        "deviceId": device_id,
    }

    print(f"→ Validating device '{device_id}' via {VALIDATE_URL} ...")
    resp = requests.get(VALIDATE_URL, headers=headers, params=params, timeout=10)
    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from validate response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    allowed = data.get("allowed")
    reason = data.get("reason")
    print(f"✔ validate response: status={status}, handler={handler}, allowed={allowed}, reason={reason}")
    print()
    return data


def build_crewai_objects() -> Crew:
    """
    Build a minimal CrewAI setup:
    - One agent
    - One task
    - One crew
    """

    # Use OpenAI via CrewAI's LLM wrapper.
    # Requires OPENAI_API_KEY in your environment.
    llm = LLM(model="gpt-4o-mini")

    planning_agent = Agent(
        role="Planning Agent",
        goal="Create short, safe, actionable plans.",
        backstory=(
            "You are a helpful AI assistant that designs small, practical plans "
            "for developers running automated agents and workers."
        ),
        llm=llm,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Generate a short, 3-step plan for how a developer could safely use "
            "CrewAI agents together with MachineID.io to avoid runaway costs."
        ),
        agent=planning_agent,
        expected_output=(
            "A concise markdown list with exactly 3 bullet points, each 1–2 sentences."
        ),
    )

    crew = Crew(
        agents=[planning_agent],
        tasks=[task],
        process=Process.sequential,
    )
    return crew


def main() -> None:
    # 1) Load org key and device ID
    org_key = get_org_key()
    device_id = get_device_id()

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "...")
    print("Using deviceId:", device_id)
    print()

    # 2) Register device with MachineID.io
    reg = register_device(org_key, device_id)
    reg_status = reg.get("status")

    if reg_status == "limit_reached":
        print("🚫 Plan limit reached on register. CrewAI run will NOT start.")
        sys.exit(0)

    # Optional small pause to mirror real startup behavior
    print("Waiting 2 seconds before validating...")
    time.sleep(2)

    # 3) Validate device before kicking off the Crew
    val = validate_device(org_key, device_id)
    allowed = val.get("allowed")
    reason = val.get("reason")

    print("Validation summary:")
    print("  allowed :", allowed)
    print("  reason  :", reason)
    print()

    if not allowed:
        print("🚫 Device is NOT allowed. CrewAI run will NOT start.")
        sys.exit(0)

    print("✅ Device is allowed. Building CrewAI objects and starting the run...")
    print()

    # 4) Build and run the CrewAI workflow
    crew = build_crewai_objects()

    try:
        result = crew.kickoff()
    except Exception as e:
        print("❌ Error while running CrewAI crew:", str(e))
        sys.exit(1)

    print("✔ CrewAI result:")
    print(result)
    print()
    print("Done. crewai_agent.py completed successfully.")


if __name__ == "__main__":
    main()
