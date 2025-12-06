# MachineID.io + CrewAI Starter Template
### Add device limits to CrewAI workers with one small register/validate block.

A minimal CrewAI starter that shows how to wrap your agents with MachineID.io device registration and validation.

Use this template to prevent runaway fleets, enforce hard device limits, and ensure every CrewAI worker checks in before doing work.  
The free org key supports **3 devices**, with higher limits available on paid plans.

> **⚠️ Python Version Note**  
> CrewAI installs cleanly on **Python 3.11**.  
> If your default system Python is 3.12 or 3.13, create a Python 3.11 venv to avoid dependency issues (tiktoken / PyO3 constraints).

---

## What this repo gives you

- `crewai_agent.py`:
  - Reads `MACHINEID_ORG_KEY` from the environment  
  - Uses a default `deviceId` of `crewai-agent-01` (override with `MACHINEID_DEVICE_ID`)  
  - Calls **POST** `/api/v1/devices/register` with `x-org-key` and a `deviceId`  
  - Calls **GET** `/api/v1/devices/validate` before running the Crew  
  - Prints clear status:
    - `ok` / `exists` / `restored`  
    - `limit_reached` (free tier = 3 devices)  
    - `allowed` / `not allowed`

- A minimal `requirements.txt` using only:
  - `crewai`  
  - `requests`

This mirrors the same register + validate pattern used in the Python and LangChain templates, but wired directly into a real CrewAI agent and task.

---

## Quick start

### 1. Clone this repo or click **“Use this template.”**

```bash
git clone https://github.com/machineid-io/crewai-machineid-template.git
cd crewai-machineid-template
```

---

### 2. Install dependencies (Python 3.11 recommended)

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click **“Generate free org key”**  
Copy the key (it begins with `org_`)

---

### 4. Export your environment variables

```bash
export MACHINEID_ORG_KEY=org_your_org_key_here
export OPENAI_API_KEY=sk_your_openai_key_here
export MACHINEID_DEVICE_ID=crewai-agent-01   # optional override
```

**One-liner (run immediately):**

```bash
MACHINEID_ORG_KEY=org_xxx OPENAI_API_KEY=sk_xxx python3.11 crewai_agent.py
```

---

### 5. Run the starter

```bash
python3.11 crewai_agent.py
```

You will see:

- A register call with plan + usage summary  
- A validate call  
- Either **“not allowed / limit reached”** or a CrewAI-generated output  

---

## How the script works

1. Reads `MACHINEID_ORG_KEY` from the environment  
2. Uses a default `deviceId` of `crewai-agent-01`  
3. Calls `/api/v1/devices/register`:
   - `ok` → new device created  
   - `exists` → device already registered  
   - `restored` → previously revoked device restored  
   - `limit_reached` → free tier cap hit  
4. Calls `/api/v1/devices/validate`:
   - `allowed: true` → CrewAI agent should run  
   - `allowed: false` → CrewAI agent should exit or pause  

This ensures each worker checks in before doing work and that scaling stays fully controlled.

---

## Using this in your own CrewAI agents

To integrate MachineID.io:

- Call **register** when your CrewAI worker starts  
- Call **validate**:
  - Before `crew.kickoff()`, or  
  - Before major tasks, or  
  - On intervals for long-running workers  
- Only continue execution when `allowed == true`  

This prevents accidental scaling, infinite worker spawning, and runaway cloud costs.

**Drop the same register/validate block into any Crew, Task, or background worker.**  
This is all you need to enforce simple device limits across your entire CrewAI fleet.

---

## Optional: fully automated org creation

Most users generate a free org key from the dashboard.

If you are building meta-agents or automated back-ends that need to bootstrap from zero, you can create an org + key programmatically:

```bash
curl -X POST https://machineid.io/api/v1/org/create \
  -H "Content-Type: application/json" \
  -d '{}'
```

The response contains a ready-to-use `orgApiKey`.

(This pattern will get its own dedicated template/repo in the future.)

---

## Files in this repo

- `crewai_agent.py` — CrewAI starter with MachineID register + validate  
- `requirements.txt` — Minimal dependencies  
- `LICENSE` — MIT licensed  

---

## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  
API → https://machineid.io/api

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ LangChain:      https://github.com/machineid-io/langchain-machineid-template  
→ OpenAI Swarm:   https://github.com/machineid-io/swarm-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`.  
- Device limits apply to unique `deviceId` values registered through `/api/v1/devices/register`.  
- When you upgrade or change plans, limits update immediately — your CrewAI workers do **not** need new code.

MIT licensed · Built by MachineID.io

