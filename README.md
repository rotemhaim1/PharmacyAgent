# Pharmacy Agent (FastAPI + React + SSE)

This project implements a **stateless**, **streaming** conversational AI “pharmacist assistant” that can respond in **English and Hebrew**, and can execute workflows via tools against a small **synthetic SQLite database**.

## Architecture
- **Backend**: FastAPI + SSE streaming endpoint `POST /chat/stream`
- **Agent**: OpenAI streaming + tool-calling; tools are deterministic and DB-backed
- **Database**: SQLite (seeded with 10 users + 5 medications + inventory + example prescriptions)
- **Frontend**: React (Vite) chat UI that sends full `messages[]` each turn (stateless backend)

## Multi-step flow demonstrations (required)

### Flow A — Stock availability + reservation
- **Goal**: resolve medication → check inventory → reserve for pickup.

Example (EN):
1. User: “Do you have ibuprofen in stock at Tel Aviv - Dizengoff?”
2. Agent calls:
   - `get_medication_by_name(query="ibuprofen")`
   - `check_inventory(medication_id=..., store_name="Tel Aviv - Dizengoff")`
3. Agent: “Tel Aviv - Dizengoff has **low / in_stock / out** …”
4. User: “Reserve 1 for pickup.”
5. Agent calls `reserve_inventory(medication_id=..., store_name="Tel Aviv - Dizengoff", quantity=1)` and confirms reservation id.

Example (HE):
1. משתמש: “יש איבופרופן במלאי בתל אביב - דיזנגוף?”
2. הסוכן קורא לכלים כמו למעלה ומחזיר סטטוס מלאי.

### Flow B — Prescription requirement + request creation
- **Goal**: resolve medication → confirm Rx/OTC → identify user → create prescription request.

Example (EN):
1. User: “Do I need a prescription for amoxicillin?”
2. Agent calls:
   - `get_medication_by_name(query="amoxicillin")`
   - `check_prescription_requirement(medication_id=...)`
3. Agent: “Prescription required (Rx). If you want, I can create a request—what’s your phone number?”
4. User: “+972501000001”
5. Agent calls:
   - `get_user_by_phone(phone="+972501000001")`
   - `create_prescription_request(user_id=..., medication_id=..., pickup_store="...")`

### Flow C — Usage instructions + policy-compliant refusal
- **Goal**: provide label-style instructions; refuse personalized medical advice.

Example (EN):
1. User: “How do I take omeprazole 20 mg?”
2. Agent calls `get_medication_by_name(...)` and answers using `label_instructions` and `warnings`.
3. User: “Is it safe for me during pregnancy?”
4. Agent: refusal + direct to pharmacist/doctor + offer factual info (Rx requirement, ingredients, stock).

## Evaluation plan (required)

### Test matrix
Run at least **2 variations per flow**, in **English and Hebrew**:
- Flow A: different stores; out-of-stock; reservation success/failure
- Flow B: Rx medication; unknown phone; request created
- Flow C: label instruction question; advice-seeking question to verify refusal

### Policy adherence checks
Use prompts that attempt to elicit medical advice (pregnancy, interactions, child dosing, chronic conditions). Verify:
- The agent **refuses medical advice**
- Redirects to **licensed pharmacist/doctor**
- Offers factual alternatives (ingredients, label instructions, stock, Rx requirement)

### Tool correctness checks
- Tools are called when needed and with valid arguments
- Ambiguity/not-found leads to clarifying questions (name/strength/form)
- Inventory reservation decrements stock and produces a reservation id

### UX/latency checks
- Measure **time-to-first-token** and overall response latency
- Verify streaming feels smooth and the UI stays responsive

## Screenshots (required)
Capture and include 2–3 screenshots of the UI showing:
- A tool-using stock check + reservation
- Rx requirement + prescription request flow
- A refusal to provide medical advice (policy compliance)

## Notes
- Backend is **stateless**: the frontend sends `messages[]` every turn.
- Configure the OpenAI key via `OPENAI_API_KEY` (preferred). A local `api-key.txt` file is also supported for convenience.

## Agent Requirements (from the PDF) checklist
Below is the “Agent Requirements” checklist and how this project meets each item:

- **Provide factual information about medications**: Uses DB-backed catalog fields (`medications.*`) and tool calls; system prompt restricts to factual info.
- **Explain dosage and usage instructions**: Responds using `label_instructions` and `warnings` fields (label-style guidance only).
- **Confirm prescription requirements**: Uses `check_prescription_requirement` tool (`otc_or_rx`).
- **Check availability in stock**: Uses `check_inventory` tool (store inventory table).
- **Identify active ingredients**: Uses `get_medication_by_name` tool result (`active_ingredients` from DB).
- **No medical advice, no encouragement to purchase, no diagnosis**: Enforced by the system prompt in `[backend/app/policy.py](backend/app/policy.py)`.
- **Redirect to a healthcare professional / resources for advice requests**: System prompt instructs refusal + redirect when asked for personalized advice.

## Run locally (dev)

### Backend
From repo root:

```bash
python -m pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
From repo root:

```bash
cd frontend
npm install
npm run dev
```

Optional: set `VITE_API_BASE_URL` to your backend URL (defaults to `http://localhost:8000`).

## Run with Docker (required)

```bash
docker build -t pharmacy-agent .
docker run --rm -p 8000:8000 pharmacy-agent
```

Then open `http://localhost:8000` (the backend serves the built frontend in the container).

## Run with Docker Compose (persistent DB)
This keeps the SQLite DB in a named volume so it **persists across container restarts**.

```bash
docker compose up --build
```

To reset the DB:

```bash
docker compose down -v
```

### Windows PowerShell examples

The Docker image copies `api-key.txt` into the container and the entrypoint exports it into `OPENAI_API_KEY` automatically, so you don’t need to pass `-e` when running.

If you still want to override the key explicitly:

```powershell
$env:OPENAI_API_KEY = (Get-Content .\api-key.txt -Raw).Trim()
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=$env:OPENAI_API_KEY pharmacy-agent
```

> Note: baking API keys into an image is convenient for a home assignment, but **not recommended for production**. In production, prefer `-e OPENAI_API_KEY=...` or a secrets manager.


