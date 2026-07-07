import asyncio
import json
import logging
import os
import signal
from contextlib import asynccontextmanager
from pathlib import Path


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse
from croo import AgentClient, Config, EventType, DeliverableType, DeliverOrderRequest, Event
from agent.graph import get_graph
from agent.tools import research_company, research_prospect, generate_precall_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def make_croo_client() -> AgentClient:
    return AgentClient(
        Config(
            base_url=os.environ["CROO_API_URL"],
            ws_url=os.environ["CROO_WS_URL"],
            rpc_url=os.environ.get("BASE_RPC_URL", ""),
        ),
        os.environ["CROO_SDK_KEY"],
    )


async def run_croo_listener():
    client = make_croo_client()
    stream = await client.connect_websocket()
    pending: dict[str, str] = {}  # negotiation_id → buyer's requirements

    def on_negotiation_created(e: Event) -> None:
        async def _handle():
            logger.info(f"New negotiation: {e.negotiation_id}")
            try:
                neg = await client.get_negotiation(e.negotiation_id)
                pending[e.negotiation_id] = neg.requirements
                result = await client.accept_negotiation(e.negotiation_id)
                logger.info(f"Order created: {result.order.order_id}")
            except Exception as err:
                logger.error(f"accept error: {err}")
        asyncio.create_task(_handle())

    def on_order_paid(e: Event) -> None:
        async def _handle():
            logger.info(f"Order {e.order_id} paid, running sales research agent...")
            try:
                requirements = pending.pop(e.negotiation_id, None)
                if not requirements:
                    neg = await client.get_negotiation(e.negotiation_id)
                    requirements = neg.requirements

                graph_result = await get_graph().ainvoke({"messages": [("user", requirements)]})
                response_key = "sales_research_response"
                sales_research = graph_result.get(response_key)

                if sales_research is None:
                    raise KeyError(f"Expected graph output under key '{response_key}'")

                await client.deliver_order(e.order_id, DeliverOrderRequest(
                    deliverable_type=DeliverableType.TEXT,
                    deliverable_text=json.dumps(sales_research.model_dump()),
                ))
                logger.info(f"Order {e.order_id} delivered!")
            except Exception as err:
                logger.error(f"deliver error: {err}")
        asyncio.create_task(_handle())

    def on_order_completed(e: Event) -> None:
        logger.info(f"Order {e.order_id} completed!")

    stream.on(EventType.NEGOTIATION_CREATED, on_negotiation_created)
    stream.on(EventType.ORDER_PAID, on_order_paid)
    stream.on(EventType.ORDER_COMPLETED, on_order_completed)

    stop = asyncio.Event()
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT, stop.set)
    await stop.wait()

    await stream.close()
    await client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_croo_listener())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ResearchCompanyRequest(BaseModel):
    companyUrl: str


class ResearchProspectRequest(BaseModel):
    linkedinUrl: str


class PrecallReportRequest(BaseModel):
    company: str
    prospect: str


class AgentRunRequest(BaseModel):
    companyUrl: str
    linkedinUrl: str


def validate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@app.get("/")
def root():
    return {"message": "Hello from Croo"}


@app.post("/api/research-company")
def research_company_route(req: ResearchCompanyRequest):
    try:
        if not validate_url(req.companyUrl):
            raise HTTPException(status_code=400, detail="Invalid company URL")

        snapshot = research_company.run(req.companyUrl)
        return {
            "snapshot": snapshot,
            "recentDevelopments": ["Recent hiring momentum and market focus."],
            "salesSignals": ["Scaling hiring needs", "Focus on recruiting velocity"],
            "talkingPoints": ["Brand fit for flexible recruiting support", "Faster talent acquisition"],
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Company research route failed")
        raise HTTPException(status_code=500, detail="Company research failed")


@app.post("/api/research-prospect")
def research_prospect_route(req: ResearchProspectRequest):
    try:
        if not validate_url(req.linkedinUrl):
            raise HTTPException(status_code=400, detail="Invalid LinkedIn URL")

        snapshot = research_prospect.run(req.linkedinUrl)
        return {
            "snapshot": snapshot,
            "background": ["Strong recruiting operations experience.", "Track record in hiring strategy."],
            "priorities": ["Improving hiring speed", "Reducing recruiting friction"],
            "conversationOpeners": ["Ask about hiring capacity and talent strategy."],
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Prospect research route failed")
        raise HTTPException(status_code=500, detail="Prospect research failed")


def parse_precall_report(output: str):
    parsed = {
        "whoYoureTalkingTo": "",
        "companyContext": "",
        "whyNow": "",
        "suggestedOpening": "",
        "keyTalkingPoints": [],
        "watchOutFor": [],
    }

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("1. Who You're Talking To:"):
            parsed["whoYoureTalkingTo"] = line.split(":", 1)[1].strip()
        elif line.startswith("2. Company Context:"):
            parsed["companyContext"] = line.split(":", 1)[1].strip()
        elif line.startswith("3. Why Now:"):
            parsed["whyNow"] = line.split(":", 1)[1].strip()
        elif line.startswith("4. Suggested Opening:"):
            parsed["suggestedOpening"] = line.split(":", 1)[1].strip()
        elif line.startswith("5. Key Talking Points:"):
            points = line.split(":", 1)[1].strip()
            parsed["keyTalkingPoints"] = [points] if points else []
        elif line.startswith("6. Watch Out For:"):
            watch = line.split(":", 1)[1].strip()
            parsed["watchOutFor"] = [watch] if watch else []

    return parsed


def map_sales_research_response_to_precall_report(payload: dict | object):
    if hasattr(payload, "model_dump"):
        data = payload.model_dump()
    elif isinstance(payload, dict):
        data = payload
    else:
        data = dict(payload)

    return {
        "whoYoureTalkingTo": data.get("who_you_are_talking_to", "") or data.get("whoYoureTalkingTo", ""),
        "companyContext": data.get("company_context", "") or data.get("companyContext", ""),
        "whyNow": data.get("why_now", "") or data.get("whyNow", ""),
        "suggestedOpening": data.get("suggested_opening", "") or data.get("suggestedOpening", ""),
        "keyTalkingPoints": data.get("key_talking_points", []) or data.get("keyTalkingPoints", []),
        "watchOutFor": data.get("watch_out_for", []) or data.get("watchOutFor", []),
    }


@app.post("/api/precall-report")
def precall_report_route(req: PrecallReportRequest):
    try:
        output = generate_precall_report.run(req.company, req.prospect)
        parsed = parse_precall_report(output)
        return parsed
    except Exception as err:
        logger.exception("Precall report route failed")
        raise HTTPException(status_code=500, detail="Report generation failed")


@app.post("/api/run-agent")
async def run_agent_route(req: AgentRunRequest):
    try:
        if not validate_url(req.companyUrl) or not validate_url(req.linkedinUrl):
            raise HTTPException(status_code=400, detail="Both company and LinkedIn URLs must be valid URLs")

        prompt = (
            f"Company URL: {req.companyUrl}\n"
            f"Prospect LinkedIn URL: {req.linkedinUrl}"
        )
        result = await get_graph().ainvoke({"messages": [("user", prompt)]})
        response = result.get("sales_research_response")

        if response is None:
            raise HTTPException(status_code=500, detail="No sales research response was generated")

        report = map_sales_research_response_to_precall_report(response)
        return {
            "report": report,
            "companyUrl": req.companyUrl,
            "linkedinUrl": req.linkedinUrl,
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Run agent route failed")
        raise HTTPException(status_code=500, detail="Agent execution failed") from err


@app.post("/chat")
async def chat(req: ChatRequest):
    result = await get_graph().ainvoke({"messages": [("user", req.message)]})
    return result.get("sales_research_response")
