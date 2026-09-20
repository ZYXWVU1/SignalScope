import logging

from app.collectors.news import collect_news
from app.collectors.runner import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    found, inserted = run_once("technology_news", collect_news)
    logging.info("news collection complete: %s found, %s inserted", found, inserted)


if __name__ == "__main__":
    main()
