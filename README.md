# AutoRia Scraper

This repository contains solutions for async data scraping from the AutoRia.
Implemented task queues to handle web scraping and database backups asynchronously.

## Tech Stack

Core: Python 3.11

Database: PostgreSQL

Task Management: Redis + RQ (Redis Queue)

Scheduling: RQ Scheduler

Containerization: Docker & Docker Compose

## How to run
Create a .env file in the root directory.

Copy .env.example to .env and update your credentials.

Make sure you have installed **Docker** and **Docker Compose**.

Open terminal and run:

    docker compose up --build

## How it Works
Initial Run: The app service initializes the database tables and starts the first scraping cycle.

Workers: The worker service listens to Redis and executes heavy tasks like scraping or database dumps.

Schedule: The scheduler ensures that a full database backup is generated every day at 12:00 PM.