import sys
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.guider.md_repair import repair_markdown_file
from src.assets import AssetsInfo

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)


def main():
    source_dir = Path(AssetsInfo.doc_path)
    dest_dir = Path(AssetsInfo.good_guide_path)
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    existing = {p.name for p in dest_dir.glob("*.md")} if dest_dir.exists() else set()

    for md_file in sorted(source_dir.glob("*.md")):
        if md_file.name in existing:
            logger.info("Skipping %s (already cleaned)", md_file.name)
            continue
        logger.info("Processing %s", md_file.name)
        repair_markdown_file(str(md_file))


if __name__ == "__main__":
    main()

