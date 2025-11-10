import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logging.getLogger("uvicorn.access").disabled = True

logger = logging.getLogger("librAI")

def get_logger(module_name: str = None):
    if module_name:
        return logging.getLogger(f"librAI.{module_name}")
    return logger