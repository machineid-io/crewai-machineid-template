# MachineID.io + CrewAI Starter Template

A minimal CrewAI starter that shows how to wrap your agents with MachineID.io device registration and validation.

Use this template to prevent runaway fleets, enforce hard device limits, and ensure every CrewAI worker checks in before doing work.  
The free org key supports up to 3 devices, with higher limits available on paid plans.


## What this repo gives you

- crewai_agent.py:
  - Reads MACHINEID_ORG_KEY from the environment
  - Uses a default deviceId of crewai-agent-01 (override with MACHINEID_DEVICE_ID)
  - Calls POST /api/v1/devices/register with x-org-key and a deviceId
  - Calls GET /api/v1/devices/validate before running the Crew
  - Prints clear status:
    - ok / exists / restored
    - limit_reached (free tier = 3 devices)
    - allowed / not allowed

- A minimal requirements.txt using only:
  - crewai
  - requests

This mirrors the same register and validate flow as the machineid-python-starter, but wired into a real CrewAI agent and task.


## Quick start

1. Clone this repo or click "Use this template"

git clone https://github.com/machineid-io/crewai-machineid-template.git

cd crewai-machineid-template


2. Install dependencies

pip install -r requirements.txt


3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click "Generate free org key"  
Copy the key (it begins with org_)


4. Export your environment variables

export MACHINEID_ORG_KEY=org_your_org_key_here

export OPENAI_API_KEY=sk_your_openai_key_here

Optional:

export MACHINEID_DEVICE_ID=crewai-agent-01


5. Run the starter

python crewai_agent.py

You will see:

- A register call with plan and usage summary  
- A validate call  
- Either "not allowed / limit reached" or a CrewAI-generated output  


## How the script works

1. Reads MACHINEID_ORG_KEY from the environment  
2. Uses a default deviceId of crewai-agent-01  
3. Calls /api/v1/devices/register:
   - ok → new device created
   - exists → device already registered
   - restored → previously revoked device restored
   - limit_reached → free tier cap hit
4. Calls /api/v1/devices/validate:
   - allowed: true → CrewAI agent should run
   - allowed: false → CrewAI agent should stop or pause

The script only runs crew.kickoff() when the device is allowed.  
This is the exact control cycle used by real agent fleets.


## Using this in your own CrewAI agents

To integrate MachineID.io:

- Call register when your CrewAI worker starts  
- Call validate:
  - Before crew.kickoff(), or
  - Before each major task, or
  - On a time interval for long-running workers  
- Only continue execution when allowed is true  

This prevents accidental scaling, infinite agent spawning, and runaway cloud costs.


## Advanced: create orgs programmatically (optional)

Most humans generate a free org key from the dashboard.

Fully automated backends or meta-agents may instead call:

POST /api/v1/org/create

This returns an orgApiKey that works exactly like dashboard-created keys.


## Files in this repo

- crewai_agent.py — CrewAI starter with MachineID register and validate
- requirements.txt — Minimal dependencies
- LICENSE — MIT licensed


## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  
API → https://machineid.io/api  
Python starter template → https://github.com/machineid-io/machineid-python-starter


## How plans work (quick overview)

- Plans are per org, each with its own orgApiKey.  
- Device limits apply to unique deviceId values registered through /api/v1/devices/register.  
- When you upgrade or change plans, limits update immediately — your agents do not need new code, and your CrewAI workers continue running without modification.

MIT licensed · Built by MachineID.io
