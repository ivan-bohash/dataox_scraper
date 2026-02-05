import asyncio
import warnings

from src.database.db import init_db
from src.scheduler.run_scheduler import init_schedule
from src.scheduler.tasks import execute_scraping


# ignore future warnings in logs
warnings.simplefilter("ignore", category=FutureWarning)

async def main():
    """
    Main function to start the app

    """

    await init_db()

    try:
        init_schedule()
        print("Success init scheduler")
    except Exception as e:
        print(f"Scheduler error: {e}")

    # to run scraping on first run
    await execute_scraping()


if __name__ == "__main__":
    asyncio.run(main())

