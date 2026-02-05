import asyncio
import warnings

from redis import Redis
from rq import Queue

from src.database.db import init_db
from src.scheduler.run_scheduler import init_schedule
from src.scheduler.tasks import run_autoria_scraper


# ignore future warnings in logs
warnings.simplefilter("ignore", category=FutureWarning)

# first time run
redis_conn = Redis(host='redis', port=6379)
q = Queue('default', connection=redis_conn)

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

    q.enqueue(run_autoria_scraper)



if __name__ == "__main__":
    asyncio.run(main())

