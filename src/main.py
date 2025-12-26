from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.ml.loader import ml_models, ModelLoader
# from src.api.v1.router import api_router # We will create this later
import logging
import time
from prometheus_client import make_asgi_app, Counter, Histogram

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter("app_requests_total", "Total app requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["method", "endpoint"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🧠 Loading AI Models... (This takes time)")
    # Real loading logic
    ml_models["embedding"] = ModelLoader.load_embedding_model()
    ml_models["llm"] = ModelLoader.load_llm_model()
    logger.info("✅ AI Models Loaded")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Unloading Models...")
    ml_models.clear()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add Prometheus asgi app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Add middleware for simple logging/metrics (optional manual impl since prometheus middleware exists but we want manual control or just simple)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
        
        return response

app.add_middleware(MetricsMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

from src.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
