import logging

from app.collectors.gaming import collect_gaming
from app.collectors.runner import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    found, inserted = run_once("xiaoheihe", collect_gaming)
    logging.info("gaming collection complete: %s found, %s inserted", found, inserted)


if __name__ == "__main__":
    main()
