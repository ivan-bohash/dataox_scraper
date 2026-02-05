import re

from selectolax.parser import HTMLParser


class LastPageFinder:
    def __init__(self):
        self.base_url = "https://auto.ria.com/uk/search/?indexName=auto"

    async def get_last_page(self, client):
        try:
            response = await client.get(self.base_url)
            tree = HTMLParser(response.text)

            last_page_node = tree.css_first('ul.pagination-inner li:last-child a')
            if last_page_node:
                raw_text = last_page_node.text(strip=True)
                return int(re.sub(r'\D', '', raw_text))

            return 1

        except Exception as e:
            print(f"Error getting last page: {e}")
            return 1