import asyncio
import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

from src.app.crawler import AutoRiaCrawler
from src.app.parser import AutoRiaParser
from src.database.db import save_cars_to_db


load_dotenv()


def create_db_dump():
    db_host = os.getenv("DB_HOST", "db")
    db_user = os.getenv("POSTGRES_USER")
    db_name = os.getenv("POSTGRES_DB")

    full_dump_path = "/app/dumps"

    if not os.path.exists(full_dump_path):
        os.makedirs(full_dump_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(full_dump_path, filename)

    command = [
        "pg_dump",
        "-h", db_host,
        "-U", db_user,
        "-d", db_name,
        "-f", filepath,
        "--clean",
        "--no-owner"
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("DB_PASSWORD")

    try:
        print(f"Start dump for {db_name} into {filename}")
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"Dump OK: {filepath}")
            return filepath
        else:
            print(f"Error dump: {result.stderr}")
            return None

    except Exception as e:
        print(f"Error while dumping: {e}")
        return None


def run_autoria_scraper():
    print("Starting scheduled scraping task")
    try:
        asyncio.run(execute_scraping())
        print("Scraping task success.")
    except Exception as e:
        print(f"Scraping task failed: {e}")

async def execute_scraping():
    parser = AutoRiaParser()
    crawler = AutoRiaCrawler(parser=parser, max_concurrent=2)

    cars_data = await crawler.run()
    count = len(cars_data)

    if count > 0:
        await save_cars_to_db(cars_data)
        print(f"Success save {count} to db.")
    else:
        print("No cars found")