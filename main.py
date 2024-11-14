import asyncio
import os
import re
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from src import (
    FacebookPostScraper,
    InstagramPostScraper,
    LinkedInPostScraper,
    XScraper,
    get_date_7_days_before_today,
    GeminiRunnerClass,
)

load_dotenv()

class SocialMediaScrapper:
    def __init__(self, api_key, cookies=None) -> None:
        self.fb = FacebookPostScraper(api_key)
        self.ins = InstagramPostScraper(api_key)
        self.x = XScraper(api_key)
        self.cookies = cookies
        self.li = LinkedInPostScraper(api_key, cookies) if cookies else None
        self.prompt = (
            "Craft a compelling narrative around the individual's personality, interests, and "
            "experiences based on the images shared on various social media platforms. Uncover layers "
            "of their character traits, passions, and life journey from the visual storytelling "
            "presented. Remember to intrigue and engage with concise, impactful observations in a Json "
            "format."
        )
        self.gem = GeminiRunnerClass()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def convert_timestamp(self, timestamp_str):
        timestamp_processed = timestamp_str.strip()
        if timestamp_processed.endswith('Z'):
            timestamp_processed = timestamp_processed[:-1] + '+0000'
        else:
            timestamp_processed = re.sub(
                r'([+-]\d{2})(\d{2})$',
                r'\1:\2',
                timestamp_processed
            )
        possible_formats = [
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%a %b %d %H:%M:%S %z %Y',
        ]
        for fmt in possible_formats:
            try:
                dt = datetime.strptime(timestamp_processed, fmt)
                dt_in_utc = dt.astimezone(timezone.utc)
                formatted_ts = dt_in_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                return formatted_ts
            except ValueError:
                continue
        raise ValueError('Timestamp format not recognized')

    async def scrape_all_social_media(
        self,
        x_username=None,
        instgram_username=None,
        facebook_username=None,
        linkedin_username=None,
        max_n=10,
        newer_than=get_date_7_days_before_today(),
    ):
        loop = asyncio.get_running_loop()
        tasks = []

        if x_username:
            tasks.append(
                loop.run_in_executor(
                    self.executor,
                    self.x.scrape_tweets,
                    x_username,
                    newer_than,
                    max_n,
                )
            )
        if instgram_username:
            tasks.append(
                loop.run_in_executor(
                    self.executor,
                    self.ins.scrape_profile,
                    instgram_username,
                    newer_than,
                    max_n,
                )
            )
        if facebook_username:
            tasks.append(
                loop.run_in_executor(
                    self.executor,
                    self.fb.scrape_page_posts,
                    facebook_username,
                    newer_than,
                    max_n,
                )
            )
        if linkedin_username and self.li:
            tasks.append(
                loop.run_in_executor(
                    self.executor,
                    self.li.scrape_profile_posts,
                    linkedin_username,
                    newer_than,
                    max_n,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        ans = []
        for result in results:
            if isinstance(result, Exception):
                print(f"An exception occurred: {result}")
            else:
                ans.extend(result or [])
        for post in ans:
            post['timestamp'] = self.convert_timestamp(post['timestamp'])
        return ans

    async def get_stories_from_social_media(self, handles_dict):
        data = await self.scrape_all_social_media(**handles_dict)
        to_process = [i for i in data if i['type'].lower() == "photo"]
        if to_process:
            output = await self.gem.get_gemini_response_image(self.prompt, to_process)
            print(output)
        else:
            print("No Images to process")
            output = []
        return output

if __name__ == "__main__":
    api_key = os.getenv("APIFY_API_KEY")
    cookies = ""
    sm = SocialMediaScrapper(api_key)
    handles = {
        "instgram_username": "steveyeun",
        # "facebook_username": "elon.musk.436479",
        # "linkedin_username": "prajwal-waykos",
        "x_username": "elonmusk",
    }
    asyncio.run(sm.get_stories_from_social_media(handles))
