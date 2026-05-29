# Lab 02 - Setup & Run (CloudShell)

## 1. Clone and navigate

```bash
git clone https://bnilesh@github.com/bnilesh/mslearn-ai-agents.git
cd mslearn-ai-agents/Labfiles/02-build-ai-agent/Python
```

## 2. Configure environment

```bash
cp .env.sample .env
nano .env
```

Replace the three placeholder values:
- `AZURE_TENANT_ID` — Azure Portal → Microsoft Entra ID → Overview → Tenant ID
- `AZURE_CLIENT_ID` — Azure Portal → Microsoft Entra ID → App registrations → your app → Application (client) ID
- `AZURE_CLIENT_SECRET` — Azure Portal → App registrations → your app → Certificates & secrets → Value

Save: `Ctrl+X` → `Y` → `Enter`

## 3. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Run

```bash
python agent-acme-app.py
```

## If repo already cloned

```bash
cd mslearn-ai-agents
git pull
cd Labfiles/02-build-ai-agent/Python
source venv/bin/activate
python agent-acme-app.py
```
