from redis import Redis
from rq_scheduler import Scheduler

from src.scheduler.tasks import create_db_dump, run_autoria_scraper


def init_schedule():
    redis_conn = Redis(host="redis", port=6379)
    scheduler = Scheduler(connection=redis_conn)

    for job in scheduler.get_jobs():
        scheduler.cancel(job)

    scheduler.cron(
        cron_string="0 12 * * *",
        func=create_db_dump,
        queue_name='default'
    )

    scheduler.cron(
        cron_string='0 12 * * *',
        func=run_autoria_scraper,
        id='scraper_daily'
    )

    print("Schedule set to 12:00 everyday")


if __name__ == "__main__":
    init_schedule()