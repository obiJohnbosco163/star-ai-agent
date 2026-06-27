import asyncio
import json
import logging
import os
import signal
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from croo import AgentClient, Config, EventType, DeliverableType, DeliverOrderRequest, Event
from agent.graph import get_graph

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
            logger.info(f"Order {e.order_id} paid, running weather agent...")
            try:
                requirements = pending.pop(e.negotiation_id, None)
                if not requirements:
                    neg = await client.get_negotiation(e.negotiation_id)
                    requirements = neg.requirements

                graph_result = await get_graph().ainvoke({"messages": [("user", requirements)]})
                weather = graph_result["weather_response"]

                await client.deliver_order(e.order_id, DeliverOrderRequest(
                    deliverable_type=DeliverableType.TEXT,
                    deliverable_text=json.dumps(weather.model_dump()),
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


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Hello from Croo"}


@app.post("/chat")
async def chat(req: ChatRequest):
    result = await get_graph().ainvoke({"messages": [("user", req.message)]})
    return result["weather_response"]
