import logging
import os

import logfire
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

# ----- Setup
logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"), service_name="fastapi", console=False
)
logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logfire.instrument_fastapi(app, capture_headers=True, extra_spans=True)
# -----

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@app.get("/")
async def hello_world() -> dict[str, str]:
    logger.info("Log inside endpoint", extra={"custom_key": "custom_value"})
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("app_logfire.app:app", port=8000, reload=True)
