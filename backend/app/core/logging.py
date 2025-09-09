import structlog
import logging
from typing import Any, Dict
import sys

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.processors.dict_tracebacks,
            structlog.dev.ConsoleRenderer() if sys.stderr.isatty() else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_request_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = get_request_id()
            scope["request_id"] = request_id
            
            logger = structlog.get_logger().bind(
                request_id=request_id,
                method=scope["method"],
                path=scope["path"],
            )
            
            logger.info("Request started")
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    logger.info("Request completed", status=message["status"])
                await send(message)
            
            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as e:
                logger.error("Request failed", error=str(e))
                raise
        else:
            await self.app(scope, receive, send)