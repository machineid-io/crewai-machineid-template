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
    return org_key.strip()


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
    if plan_tier is not None:
        print("  planTier    :", plan_tier)
    if limit is not None:
        print("  limit       :", limit)
    if devices_used is not None:
        print("  devicesUsed :", devices_used)
    if remaining is not None:
        print("  remaining   :", remaining)
    print()

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
    allowed = bool(data.get("allowed", False))
    reason = data.get("reason", "unknown")
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

    # Uses OpenAI via CrewAI's LLM wrapper.
    # Requires OPENAI_API_KEY in your environment.
    llm = LLM(model="gpt-4o-mini")

    planning_agent = Agent(
        role="CrewAI Worker",
        goal=(
            "Create short, practical 3-step plans that show developers how to keep "
            "their CrewAI agents under control using MachineID.io."
        ),
        backstory=(
            "You help developers run CrewAI agents safely. MachineID.io sits in front "
            "of their agents as a device-level gatekeeper: each agent registers on "
            "startup and validates before doing work, so they can avoid runaway "
            "spawning and keep fleets predictable."
        ),
        llm=llm,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Generate a concise 3-step plan for how a developer can use MachineID.io "
            "together with CrewAI agents to keep scaling under control. Focus on:\n"
            "- Registering each agent (deviceId) when it starts\n"
            "- Validating before doing work or starting a major task\n"
            "- Treating a failed validation or limit_reached status as the hard stop "
            "to avoid spawning more agents.\n\n"
            "Do not mention dashboards, analytics, or built-in spend monitoring. "
            "Explain MachineID.io as a device-level limiter and gate, not an analytics tool."
        ),
        agent=planning_agent,
        expected_output=(
            "A short markdown list with exactly 3 numbered steps. Each step should be "
            "1–2 sentences, practical, and focused on using register + validate as "
            "control points around CrewAI agents."
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
    allowed = bool(val.get("allowed", False))
    reason = val.get("reason", "unknown")

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
