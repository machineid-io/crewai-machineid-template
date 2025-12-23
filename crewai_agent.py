#!/usr/bin/env python3

import os
import sys
import time
from typing import Any, Dict

import requests

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

BASE_URL = os.getenv("MACHINEID_BASE_URL", "https://machineid.io").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


# -------------------------
# MachineID helpers
# -------------------------

def get_org_key() -> str:
    org_key = os.getenv("MACHINEID_ORG_KEY")
    if not org_key:
        raise RuntimeError(
            "Missing MACHINEID_ORG_KEY.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
        )
    return org_key.strip()


def get_device_id() -> str:
    return os.getenv("MACHINEID_DEVICE_ID", "crewai:agent-01").strip() or "crewai:agent-01"


def post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout_s: int = 10) -> Dict[str, Any]:
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    try:
        data = resp.json()
    except Exception:
        print("❌ Non-JSON response")
        print("HTTP:", resp.status_code)
        print(resp.text)
        raise

    if resp.status_code >= 400:
        return {
            "status": "error",
            "http": resp.status_code,
            "body": data,
        }

    return data


def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    print(f"→ Registering device '{device_id}'")
    data = post_json(
        REGISTER_URL,
        headers={"x-org-key": org_key, "Content-Type": "application/json"},
        payload={"deviceId": device_id},
    )

    status = data.get("status")
    print(f"✔ register status={status}")

    if status not in ("ok", "exists"):
        print("🚫 Register failed:", data)
        sys.exit(1)

    return data


def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    print(f"→ Validating device '{device_id}' (POST canonical)")
    data = post_json(
        VALIDATE_URL,
        headers={"x-org-key": org_key, "Content-Type": "application/json"},
        payload={"deviceId": device_id},
    )

    allowed = bool(data.get("allowed", False))
    code = data.get("code")
    request_id = data.get("request_id")

    print(f"✔ decision allowed={allowed} code={code} request_id={request_id}")
    return data


# -------------------------
# CrewAI demo
# -------------------------

def build_crewai_objects() -> Crew:
    llm = LLM(model="gpt-4o-mini")

    agent = Agent(
        role="CrewAI Worker",
        goal=(
            "Create short, practical 3-step plans that show developers how to keep "
            "their CrewAI agents under control using MachineID."
        ),
        backstory=(
            "You help developers run CrewAI agents safely. MachineID acts as an "
            "external device-level control plane: agents register on startup and "
            "validate before doing work so runaway execution is impossible."
        ),
        llm=llm,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Write a concise 3-step plan explaining how to use MachineID with CrewAI:\n"
            "- Register each agent on startup\n"
            "- Validate before doing work\n"
            "- Treat a failed validation as a hard stop\n"
        ),
        agent=agent,
        expected_output=(
            "Exactly 3 numbered steps, 1–2 sentences each, focused on register + "
            "validate as enforcement boundaries."
        ),
    )

    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
    )


# -------------------------
# Main
# -------------------------

def main() -> None:
    org_key = get_org_key()
    device_id = get_device_id()

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "…")
    print("Using base_url:", BASE_URL)
    print("Using device_id:", device_id)
    print()

    # 1) Register (idempotent)
    register_device(org_key, device_id)

    # 2) Validate (hard gate)
    time.sleep(1)
    val = validate_device(org_key, device_id)

    if not val.get("allowed", False):
        print("🚫 Execution denied. Crew will NOT start.")
        sys.exit(0)

    print("✅ Execution allowed. Starting CrewAI run.")
    print()

    crew = build_crewai_objects()
    result = crew.kickoff()

    print("✔ CrewAI result:")
    print(result)
    print()
    print("Done.")


if __name__ == "__main__":
    main()
