import asyncio
import re

import httpx
from selectolax.parser import HTMLParser

from src.app.pagination import LastPageFinder


class AutoRiaCrawler:
    """
    Class to manage the crawling process

    """

    def __init__(self, parser, max_concurrent=3):
        self.base_url = "https://auto.ria.com/uk/search/?indexName=auto&page="
        self.car_url = "https://auto.ria.com"
        self.pop_up_url = "https://auto.ria.com/bff/final-page/public/auto/popUp"
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=max_concurrent)
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.parser = parser

    async def get_phone_number(self, client, url, html, title):
        """
        Function to get phone number from html

        """

        auto_id, user_id, phone_id = self.parser.extract_ids(html)

        if not all([auto_id, user_id, phone_id]):
            return None

        # JSON payload for pop-up API
        payload = {
            "blockId": "autoPhone",
            "popUpId": "autoPhone",
            "autoId": int(auto_id),
            "params": {
                "userId": str(user_id),
                "phoneId": str(phone_id),
                "title": title
            },
            "langId": 4,
            "device": "desktop-web"
        }

        try:
            res = await client.post(
                # Endpoint to fetch pop-up data which contains the phone number
                self.pop_up_url,
                json=payload,
                headers={**self.headers, "Referer": url},
            )
            if res.status_code == 200:
                phone_match = re.search(r'tel:([\+\d\s\(\)]+)', res.text)
                if phone_match:
                    return self.parser.clean_phone(phone_match.group(1).replace("%20", " "))

        except Exception as e:
            print(f"Phone error: {e}")

        return None

    async def fetch_car_info(self, client, url, max_reties=3):
        for attempt in range(max_reties):
            try:
                res = await client.get(url, timeout=10)
                if res.status_code != 200:
                    print(f"Error: {res.status_code} for {url}")
                    continue

                html = res.text
                tree = HTMLParser(html)

                # check car is active
                if tree.css_first("#bannerStatus"):
                    print(f"Car not active, skip: {url}")
                    return None

                # title
                title_node = tree.css_first("#basicInfoTitle h1")
                title = title_node.text(strip=True) if title_node else None

                # price
                price_usd_raw = tree.css_first("#basicInfoPrice strong").text(strip=True)
                price_usd = int(re.sub(r'\D', '', price_usd_raw))

                # odometer
                odometer_node = tree.css_first("#basicInfoTableMainInfo0 span").text(strip=True)
                digits = re.sub(r'\D', '', odometer_node)

                if digits:
                    if "тис." in odometer_node:
                        odometer = int(re.sub(r'\D', '', odometer_node) + '000')
                    else:
                        odometer = int(digits)
                else:
                    odometer = 0


                # username
                username = str(tree.css_first("#sellerInfoUserName span").text(strip=True))

                # phone number
                phone_number = await self.get_phone_number(client=client, url=url, html=html, title=title)

                # image url
                image_url = str(tree.css_first("#photoSlider .carousel__slide img").attributes.get("data-src"))

                # images count
                images_count_text = tree.css_first(".carousel__liveregion").text(strip=True)
                images_count = int(images_count_text.split()[-1])

                # car number
                car_number_node = tree.css_first(".car-number span")
                car_number = str(car_number_node.text(strip=True).replace(" ", "")) if car_number_node else None

                # car vin
                car_vin_node = tree.css_first("#badgesVin span.badge")
                car_vin = str(car_vin_node.text(strip=True)) if car_vin_node else None

                car_data = {
                    "url": url,
                    "title": title,
                    "price_usd": price_usd,
                    "odometer": odometer,
                    "username": username,
                    "phone_number": phone_number,
                    "image_url": image_url,
                    "images_count": images_count,
                    "car_number": car_number,
                    "car_vin": car_vin,
                }

                print(car_data)
                return car_data

            except Exception as e:
                print(f"Error parsing {url}: {e}")
                wait_time = (attempt + 1) * 2
                if attempt < max_reties - 1:
                    print(f"Sleeping for {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Unable to fetch {url} after {attempt} attempts")
                    return None

        return None


    async def run(self):
        async with httpx.AsyncClient(limits=self.limits, headers=self.headers) as client:
            last_page = LastPageFinder()
            total_pages = await last_page.get_last_page(client=client)

            print("Total pages: ", total_pages)

            all_results = []
            batch_size = 5

            # for testing case
            pages = 2

            for page in range(pages):
            # for page in range(total_pages):
                print(f"Fetching page {page}")
                res = await client.get(f"{self.base_url}{page}")
                tree = HTMLParser(res.text)

                links = [
                    f"{self.car_url}{n.attributes['href']}"
                    for n in tree.css("a.product-card")
                    if "href" in n.attributes
                ]

                for i in range(0, len(links), batch_size):
                    batch_links = links[i:i + batch_size]

                    tasks = [self.fetch_car_info(client, link, max_reties=3) for link in batch_links]

                    batch_result = await asyncio.gather(*tasks)
                    clean_result = [r for r in batch_result if r]
                    all_results.extend(clean_result)

                    await asyncio.sleep(1)

            print("Results: ", all_results)

            return all_results


