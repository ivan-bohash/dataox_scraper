import re


class AutoRiaParser:
    """
    Class to parse specific HTML elements and data cleaning
    """

    @staticmethod
    def extract_ids(html: str):
        match = re.search(
            r'"autoId":\s*"?(\d+)"?.*?"userId":\s*"?(\d+)"?.*?"phoneId":\s*"?(\d+)"?',
            html,
            re.DOTALL
        )

        if match:
            return match.group(1), match.group(2), match.group(3)
        return None, None, None

    @staticmethod
    def clean_odometer(text: str):
        if not text:
            return 0

        digits = re.sub(r'\D', '', text)

        if not digits:
            return 0

        return int(digits + "000") if "тис." in text else int(digits)

    @staticmethod
    def clean_phone(raw_phone: str):
        phone_number = re.sub(r'\D', '', raw_phone)

        if phone_number.startswith('0') and len(phone_number) == 10:
            return int(f"38{phone_number}")

        return int(phone_number) if phone_number else None