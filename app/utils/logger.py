import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("whatsapp-jarvis")

def get_logger(name: str):
    return logging.getLogger(f"whatsapp-jarvis.{name}")
