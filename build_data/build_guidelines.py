import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.guider.read_all_guidelines import read_guidelines
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_path=True,
        )
    ],
)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)



def main():
    """Run the end-to-end guideline build without extra parameters."""
    read_guidelines("")


if __name__ == "__main__":
    main()
