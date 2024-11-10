from FacebookScrapper import FacebookPostScraper
from InstgramScrapper import InstagramPostScraper
from LinkedinScrapper import LinkedInPostScraper
from XScrapper import XScraper
import os
from dotenv import load_dotenv
from utils import get_date_7_days_before_today
from datetime import datetime, timezone
import re
load_dotenv()


# Initialize all the values

class SocialMediaScrapper():
    def __init__(self, api_key, cookies = None) -> None:
        pass
        self.fb = FacebookPostScraper(api_key)
        self.ins = InstagramPostScraper(api_key)
        self.x = XScraper(api_key)
        self.cookies = cookies
        if cookies:
            self.li = LinkedInPostScraper(api_key, cookies)
        else:
            self.li = None
    def convert_timestamp(self, timestamp_str):


        # Preprocess the timestamp to handle 'Z' and time zone offsets
        timestamp_processed = timestamp_str.strip()
        if timestamp_processed.endswith('Z'):
            timestamp_processed = timestamp_processed[:-1] + '+0000'
        else:
            # Handle time zone offset without colon (e.g., +0000 to +00:00)
            timestamp_processed = re.sub(
                r'([+-]\d{2})(\d{2})$',
                r'\1:\2',
                timestamp_processed
            )

        # Possible input formats
        possible_formats = [
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%a %b %d %H:%M:%S %z %Y',
        ]

        for fmt in possible_formats:
            try:
                dt = datetime.strptime(timestamp_processed, fmt)
                # Convert to UTC
                dt_in_utc = dt.astimezone(timezone.utc)
                # Format to standard ISO 8601 with milliseconds
                formatted_ts = dt_in_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                return formatted_ts
            except ValueError:
                continue
        raise ValueError('Timestamp format not recognized')

    
    def scrape_all_social_media(self, x_username = None, instgram_username = None, facebook_username = None, linkedin_username = None, max_n = 10, newer_than = get_date_7_days_before_today()):
        
        tweets = self.x.scrape_tweets(x_username, newer_than, max_n = max_n )

        insta_posts = self.ins.scrape_profile(instgram_username, newer_than,  max_n= max_n)

        fb_posts = self.fb.scrape_page_posts(facebook_username, newer_than,  max_n==max_n)

        if self.li:
            linkedin_posts = self.li.scrape_profile_posts(linkedin_username, newer_than,  max_n==max_n)
        else:
            linkedin_posts = None
        
        ans = (tweets or []) + (insta_posts or []) + (fb_posts or []) + (linkedin_posts or [])
        for post in ans:
            post['timestamp'] = self.convert_timestamp(post['timestamp'])
        return ans

if __name__ == "__main__":
    api_key = os.getenv("APIFY_API_KEY")
    cookies = ""

    sm = SocialMediaScrapper(api_key)
    handles = {
        "instgram_username": "steveyeun",
        # "facebook_username": "elon.musk.436479",
        # "linkedin_username": "prajwal-waykos",
        "x_username": "elonmusk"
    }
    output = sm.scrape_all_social_media(**handles)
    import json

    with open("output.json", "w+") as f:
        json.dump(output, f)