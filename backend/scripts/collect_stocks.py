import logging

from app.collectors.runner import run_once
from app.collectors.stocks import collect_stocks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    found, inserted = run_once("stocks", collect_stocks)
    logging.info("stocks collection complete: %s found, %s inserted", found, inserted)


if __name__ == "__main__":
    main()
