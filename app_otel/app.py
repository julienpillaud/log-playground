import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

load_dotenv()

app = FastAPI()

# ----- Setup
# ----- Common setup
endpoint = os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]
os.getenv("OTEL_TOKEN")
headers = {"Authorization": os.environ["OTEL_TOKEN"]}
resource = Resource.create({"service.name": "fastapi"})

# ----- Tracing setup
tracer_provider = TracerProvider(resource=resource)
span_exporter = OTLPSpanExporter(
    endpoint=f"{endpoint}/v1/traces",
    headers=headers,
)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

# ----- Logging setup
logger_provider = LoggerProvider(resource=resource)
log_exporter = OTLPLogExporter(
    endpoint=f"{endpoint}/v1/logs",
    headers=headers,
)
record_processor = BatchLogRecordProcessor(log_exporter)
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
set_logger_provider(logger_provider)

# ---- FastAPI instrumentation
FastAPIInstrumentor.instrument_app(app)
# -----

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@app.get("/")
async def hello_world() -> dict[str, str]:
    logger.info("Log inside endpoint", extra={"custom_key": "custom_value"})
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("app_otel.app:app", port=8001, reload=True)
