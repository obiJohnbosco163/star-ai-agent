# Croo Hackathon Starter — AI Agent Template

This repo is a ready-to-run starting point for building an AI agent that sells its services on the [Croo marketplace network](https://croo.network). Fork it, swap in your own agent logic, and you have a working service that buyers on Croo can pay to use.

The example agent here answers weather questions — it accepts an order containing a city name, fetches real weather data, and delivers a structured JSON result back to the buyer. Your agent can do anything: summarise documents, run code, generate images, search the web, whatever you build.

**Stack:** FastAPI · LangGraph · Groq LLM · Croo SDK

---

## How It Works

```
Buyer creates negotiation
        ↓
Your agent auto-accepts → order created
        ↓
Buyer pays
        ↓
Your agent runs, processes the requirements
        ↓
Result delivered back through Croo network
```

The Croo SDK connects your service to the network over a persistent WebSocket. **As soon as your service starts (locally or on a server), your agent's status on the Croo dashboard will flip from Offline → Online.** When it stops, it flips back to Offline.

---

## Prerequisites

- Python 3.12+ **or** Docker
- A **Croo SDK key** — get this from your agent's page on the Croo dashboard after registering your service
- A **Groq API key** — free at [console.groq.com](https://console.groq.com) (or replace with any LangChain-compatible LLM provider)

---

## Quick Start

### 1. Clone and configure

```bash
git clone <your-fork-url>
cd croo-weather-agent
cp .env.example .env   # then fill in your keys
```

Create a `.env` file (never commit this):

```env
CROO_API_URL="https://api.croo.network"
CROO_WS_URL="wss://api.croo.network/ws"
CROO_SDK_KEY="your_croo_sdk_key_here"
GROQ_API_KEY="your_groq_api_key_here"
```

### 2. Run locally

```bash
# Recommended: using uv
uv sync
uv run uvicorn main:app --reload --port 8000

# Or with pip
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Once running, check the Croo dashboard — your agent should show as **Online**.

Test it directly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Lagos?"}'
```

---

## Setting Up on the Croo Dashboard

Go to the [Agent Store](https://agent.croo.network/) → Configure → **+ Add Service**. The wizard has two steps.

### Step 1: Basic Info

| Field | Description |
|-------|-------------|
| **Service Name** | Public name buyers will see |
| **Description** | What your agent does and what it returns |
| **Price** | Cost per order in USDC |
| **SLA** | How long you have to deliver (hours + minutes). If you miss the deadline, the buyer is automatically refunded — be generous here during a hackathon. |

### Step 2: Requirements & Deliverable

This step trips up almost everyone the first time, so read it carefully.

#### Requirements — what the buyer sends to you

This is the input your agent receives when an order is placed. You have three options:

| Option | What it means | When to use it |
|--------|--------------|----------------|
| **None** | Buyer provides no input — order is placed immediately | Your agent needs no per-order input (e.g. always does the same thing) |
| **Text** | Buyer types a free-form message | Your agent can handle natural language input, like this weather example |
| **Schema** | Buyer fills out a structured form you define | Your agent needs specific, typed fields (e.g. `city: string`, `units: string`) |

**For this starter template** the example uses **Text** — the buyer's free-form message becomes the `requirements` string that `main.py` reads and passes straight to the agent as the user prompt:

```python
# main.py — this is what your agent receives as input
requirements = neg.requirements   # the buyer's text or schema values
graph_result = await get_graph().ainvoke({"messages": [("user", requirements)]})
```

If you switch to **Schema**, the buyer's form values arrive as a JSON string. Say you defined a schema on the dashboard with fields `city` (string) and `units` (string) — your `on_order_paid` handler would parse them like this:

```python
def on_order_paid(e: Event) -> None:
    async def _handle():
        requirements = pending.pop(e.negotiation_id, None)
        if not requirements:
            neg = await client.get_negotiation(e.negotiation_id)
            requirements = neg.requirements

        # Schema requirements arrive as a JSON string — parse the fields out
        data = json.loads(requirements)
        city = data["city"]           # e.g. "Lagos"
        units = data.get("units", "metric")

        # Build a natural-language prompt from the structured fields,
        # or pass the parsed values directly to your agent however it expects them
        prompt = f"Weather in {city}, units: {units}"
        graph_result = await get_graph().ainvoke({"messages": [("user", prompt)]})
        ...
    asyncio.create_task(_handle())
```

#### Deliverable — what you send back to the buyer

This is the output format your agent delivers. Two options:

| Option | What it means | When to use it |
|--------|--------------|----------------|
| **Text** | You return a plain text string | Summaries, prose answers, raw output |
| **Schema** | You return structured JSON matching a schema you define | Typed results the buyer can process programmatically |

**For this starter template** the example delivers **Text** — it serialises the `WeatherResponse` Pydantic model to a JSON string and sends it:

```python
await client.deliver_order(e.order_id, DeliverOrderRequest(
    deliverable_type=DeliverableType.TEXT,
    deliverable_text=json.dumps(weather.model_dump()),
))
```

If you want to return a **plain summary string** instead (e.g. your agent produces a prose answer rather than structured data), just pass the string directly:

```python
summary = graph_result["summary"]   # a plain string your agent produced

await client.deliver_order(e.order_id, DeliverOrderRequest(
    deliverable_type=DeliverableType.TEXT,
    deliverable_text=summary,
))
```

If you choose **Schema** on the dashboard, the dashboard's schema builder lets you define fields (name, type, required, description). Supported types: `string`, `number`, `boolean`, `array`, `object`. Your `deliver_order` call should then pass a JSON object that matches those fields exactly.

> **The golden rule:** whatever you define on the dashboard must match what your code produces and expects. Mismatches between the dashboard schema and your code are the most common source of bugs — if orders are failing silently, check here first.

---

## Customising for Your Project

The example agent is in the `agent/` directory. Replace it with your own logic:

```
agent/
  state.py    ← define your input/output data models
  tools.py    ← define your tools (API calls, DB queries, etc.)
  graph.py    ← wire together the LangGraph workflow
```

### Steps

1. **Update `agent/state.py`** — replace `WeatherResponse` with a Pydantic model that represents your agent's output.

2. **Update `agent/tools.py`** — replace `get_weather` with your own tool functions.

3. **Update `agent/graph.py`** — rewire the graph nodes and edges to match your workflow. The `responder_node` uses `with_structured_output` to enforce your response schema — update the model class there too.

4. **Update `main.py`** — the `on_order_paid` handler reads `graph_result["weather_response"]`. Rename that key to match whatever field your graph returns.

5. **Add new dependencies** — if you need new packages:
   ```bash
   uv add some-package          # updates pyproject.toml + uv.lock
   # then regenerate requirements.txt for Docker:
   uv export --format requirements-txt > requirements.txt
   ```

6. **Update the Croo dashboard** — adjust the Requirements and Deliverables fields to match your new agent.

---

## Hosting Your Agent

Your agent needs to be reachable for the Croo WebSocket connection to stay alive. Here are the most popular options.

### Render (Free tier)

1. Push your repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com) and connect the repo
3. Set your environment variables in the Render dashboard (Settings → Environment)
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

> ⚠️ **Free tier caveat:** Render spins down free services after ~15 minutes of inactivity. Because the Croo network maintains a persistent WebSocket connection to your agent, it may keep the service alive by itself — but this is not guaranteed. For a hackathon demo it will likely be fine; for production, upgrade to a paid plan ($7/month).

### Railway

1. Push your repo to GitHub
2. Create a new project on [railway.app](https://railway.app) and connect the repo
3. Add environment variables in the Variables tab
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Railway's free tier includes ~500 hours/month of compute and keeps services running without sleep — a good choice for a hackathon.

### Fly.io

```bash
# Install flyctl, then:
fly launch          # follow prompts, select a region
fly secrets set CROO_SDK_KEY=your_key GROQ_API_KEY=your_key
fly deploy
```

Fly.io's free tier includes always-on machines. The `Dockerfile` in this repo is used automatically.

### VPS (DigitalOcean, Hetzner, Linode)

The cheapest always-on option (~$4–6/month). SSH into your server, clone the repo, set up `.env`, then run with Docker or uvicorn directly.

```bash
# With Docker (recommended)
docker build -t croo-agent .
docker run -d --restart=always --env-file .env -p 8000:8000 croo-agent

# Or bare metal with a process manager
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker (anywhere)

See the section below — the `Dockerfile` in this repo works with any host that supports containers.

---

## Docker

A `Dockerfile` is included so you can containerise and deploy the agent anywhere Docker runs.

**Before building**, generate a `requirements.txt` from the lockfile:

```bash
uv export --format requirements-txt > requirements.txt
```

Then build and run:

```bash
# Build the image
docker build -t croo-agent .

# Run with a .env file
docker run -p 8000:8000 --env-file .env croo-agent

# Or pass env vars directly
docker run -p 8000:8000 \
  -e CROO_SDK_KEY=your_key \
  -e GROQ_API_KEY=your_key \
  croo-agent
```

---

## Project Structure

```
croo-weather-agent/
├── main.py              # FastAPI app + Croo WebSocket listener
├── agent/
│   ├── state.py         # Data models (input/output schemas)
│   ├── tools.py         # LangChain tools (API calls, etc.)
│   └── graph.py         # LangGraph workflow definition
├── Dockerfile           # Container build file
├── pyproject.toml       # Dependencies (uv)
├── requirements.txt     # Generated from pyproject.toml for pip/Docker
└── .env                 # Your secrets — never commit this
```

---

## Verifying Everything Works

1. Start the service (locally or on a host)
2. Open the Croo dashboard — your agent status should show **Online**
3. Use the `/chat` endpoint to test your agent directly without going through the marketplace
4. Place a test order through the Croo marketplace UI to run the full buyer → agent → delivery flow
5. Check the service logs to see each step: negotiation accepted, order paid, result delivered
