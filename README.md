# MachineID.io + CrewAI Starter Template
### Add hard device limits to CrewAI workers with one small register/validate block.

A minimal CrewAI starter that shows how to wrap your agents with MachineID device registration and validation.

Use this template to prevent runaway fleets, enforce hard device limits, and ensure every CrewAI worker checks in before doing work.  
The free org key supports **3 devices**, with higher limits available on paid plans.

---

## ⚠️ Python version requirement (important)

CrewAI installs most reliably on **Python 3.11**.

Python **3.12 / 3.13 / 3.14** may fail due to ecosystem-level constraints (PyO3, tokenizers, and transitive dependencies).

**Recommended installation:**

```bash
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
```

---

## What this repo gives you

- `crewai_agent.py`:
  - Reads `MACHINEID_ORG_KEY` from the environment  
  - Uses a default `deviceId` of `crewai:agent-01` (override with `MACHINEID_DEVICE_ID`)  
  - Calls **POST** `/api/v1/devices/register` with `x-org-key` and a `deviceId`  
  - Calls **POST** `/api/v1/devices/validate` before starting the Crew  
  - Enforces a **hard gate**:
    - If `allowed == false`, execution stops immediately  
  - Prints stable decision metadata:
    - `allowed`
    - `code`
    - `request_id`

- A minimal `requirements.txt` using only:
  - `crewai`
  - `requests`

This mirrors the same register + validate enforcement pattern used in the Python starter and other MachineID templates.

---

## Quick start

### 1. Clone this repo or click **“Use this template.”**

```bash
git clone https://github.com/machineid-io/crewai-machineid-template.git
cd crewai-machineid-template
```

---

### 2. Install dependencies (Python 3.11 required)

```bash
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
```

---

### 3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click **“Generate free org key”**  
Copy the key (it begins with `org_`)

---

### 4. Export required environment variables

```bash
export MACHINEID_ORG_KEY=org_your_org_key_here
export OPENAI_API_KEY=sk_your_openai_key_here
```

Optional override:

```bash
export MACHINEID_DEVICE_ID=crewai:agent-01
```

**One-liner:**

```bash
MACHINEID_ORG_KEY=org_xxx OPENAI_API_KEY=sk_xxx python crewai_agent.py
```

---

### 5. Run the starter

```bash
python crewai_agent.py
```

You will see:

- A register call  
- A validate decision  
- Either:
  - `allowed=true` → CrewAI starts  
  - `allowed=false` → process exits immediately  

---

## How the script works

1. Reads `MACHINEID_ORG_KEY` from the environment  
2. Uses a deterministic `deviceId` (`crewai:agent-01`)  
3. Calls `/api/v1/devices/register` (idempotent):
   - `ok` → new device created  
   - `exists` → device already registered  
4. Calls `/api/v1/devices/validate` (POST, canonical):
   - `allowed: true` → CrewAI may run  
   - `allowed: false` → process must exit  

There is **no restore, grace period, or soft failure path**.  
Validation is a **hard enforcement boundary**.

---

## Using this in your own CrewAI agents

To integrate MachineID:

- Register once when the worker starts  
- Validate immediately before `crew.kickoff()`  
- Exit immediately if `allowed == false`  

This pattern prevents:
- Accidental scaling
- Infinite worker spawning
- Uncontrolled cloud spend
- Runaway agent behavior

Drop the same register + validate block into any CrewAI worker or task runner.

---

## Files in this repo

- `crewai_agent.py` — CrewAI worker with hard-gate enforcement  
- `requirements.txt` — Minimal dependencies  
- `LICENSE` — MIT licensed  

---

## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ LangChain: https://github.com/machineid-io/langchain-machineid-template  
→ OpenAI Swarm: https://github.com/machineid-io/swarm-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`  
- Device limits apply to unique `deviceId` values registered through `/devices/register`  
- Plan changes take effect immediately — **no agent code changes required**

MIT licensed · Built by MachineID
