from apify_client import ApifyClient
import re
import os
from dotenv import load_dotenv
load_dotenv()

class LinkedInPostScraper:
    def __init__(self, api_token, cookies):
        """
        Initializes the LinkedInPostScraper with the provided Apify API token.

        :param api_token: Your Apify API token.
        """
        if not api_token:
            raise ValueError("API token must be provided.")
        
        if not cookies:
            raise ValueError("Cookies Are Required")
        
        self.client = ApifyClient(api_token)
        self.cookies = cookies
        self.types = ["image", "document"]

    def scrape_profile_posts(self, username,newer_than = None,  max_n=10):
        """
        Scrapes public posts from the given LinkedIn profile URL.

        :param profile_url: The URL of the LinkedIn profile to scrape.
        :param max_n: The maximum number of posts to retrieve.
        :return: A list of dictionaries containing post details.
        """
        profile_url = f'https://www.linkedin.com/in/{username}'
        # Validate the profile URL
        if not self._is_valid_linkedin_profile_url(profile_url):
            raise ValueError("Invalid LinkedIn profile URL.")

        # Prepare the actor input
        run_input = {
            "urls": [profile_url],
            "maxPosts": max_n,
            "resultsLimit": max_n,
            "proxyConfiguration": {
                "useApifyProxy": True,
                # Uncomment and specify proxy groups if needed
                # "apifyProxyGroups": ["RESIDENTIAL"]
            },
            "cookie": self.cookies,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyCountry": "US",
    }
        }

        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor("curious_coder/linkedin-post-search-scraper").call(run_input=run_input)
        except Exception as e:
            print(f"An error occurred while running the actor: {e}")
            return None

        items = self.get_items(run)
        posts = self.extract_posts(items)
        return posts

    def get_items(self, run):
        """
        Retrieves items from the dataset associated with the Actor run.

        :param run: The Actor run object.
        :return: A list of items retrieved from the dataset.
        """
        items = []
        try:
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                print("No dataset ID found in the run object.")
                return items

            dataset_client = self.client.dataset(dataset_id)
            for item in dataset_client.iterate_items():
                items.append(item)
        except Exception as e:
            print(f"An error occurred while fetching items from the dataset: {e}")

        return items

    def extract_posts(self, items):
        """
        Extracts posts from the scraped profile data.

        :param items: A list of items from the dataset.
        :return: A list of dictionaries containing post details.
        """

        posts = []
        for item in items:
            content_type = item.get("type", None)


            if content_type in self.types:
                output_format = {
                "type": content_type,
                "content_urls": [],
            }
                timestamp = item.get("postedAtISO", None)
                output_format['timestamp'] = timestamp
                output_format['social_media'] = "linkedin"
                location = item.get("location", None)
                output_format['location'] = location
                if content_type == "image":
                    output_format['content_urls'] = item['images']
                elif content_type == "document":
                    output_format['content_urls'] = item['document']['coverPages']
                
                posts.append(output_format)
            


        return posts

    def _is_valid_linkedin_profile_url(self, url):
        """
        Validates if the provided URL is a valid LinkedIn profile URL.

        :param url: The URL to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^https?://(www\.)?linkedin\.com/in/[^/]+/?$'
        return re.match(pattern, url) is not None

if __name__ == "__main__":
    # Import the class

    
    cookies =  [
    {
        "domain": ".linkedin.com",
        "expirationDate": 1732020332.104127,
        "hostOnly": False,
        "httpOnly": False,
        "name": "lms_ads",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AQGfXbaOemugAwAAAZKp9i_PEWZn6c6aHj0hGmsuFgn1_4DM902uUce11nN9r-Zh5AwJjGULf-f8-n6PoUk1f7kf9GZq3Nn6"
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1760971443.784895,
        "hostOnly": False,
        "httpOnly": False,
        "name": "bcookie",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "\"v=2&65f2d9f9-4741-4dd3-82e3-017ae87ccd56\""
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1729436658.300949,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__cf_bm",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "YAE5Bk47VszgANFjNoZFzP3kG_VsOB_j8TIgOIA8UKg-1729434862-1.0.1.1-FKqmlQZnItfZzB1GMiDey8doH_Pr2Htq6tqMZDpuNLMElg4fd9Todf9gca.2JlE1Deh2z3ntsEaRAP0sU15PEA"
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1732020332.104297,
        "hostOnly": False,
        "httpOnly": False,
        "name": "lms_analytics",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AQGfXbaOemugAwAAAZKp9i_PEWZn6c6aHj0hGmsuFgn1_4DM902uUce11nN9r-Zh5AwJjGULf-f8-n6PoUk1f7kf9GZq3Nn6"
    },
    {
        "domain": ".linkedin.com",
        "hostOnly": False,
        "httpOnly": True,
        "name": "fptctx2",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "taBcrIH61PuCVH7eNCyH0HyAAKgSb15ZEqidLg30r8NTC%252fLinsDSB37%252fHAbSGY7SGUwxYuJNA1ilyLpvC4h5Ln8d4q8bxEQ30UltbJhQVqCqHN8TIUsjpsf60tx%252fLQbOhnVlZ3tjmvbyc2ziaF0a%252bpdM2EO0ZtYrZASsT%252fFbhkT5TFLU4ldXRMhl%252bLfUJJhekt%252bc9qFr0K0ew4hswhmJdoOkUDsM4yLqdPI2X1l%252bZnO2sZCiuMa5OCmpPCDi7gkoceblLp%252bTGA2k%252fmcTsSz9Oo3lRwh1oEZ2gzhp9nE4D%252fiFIzBee9vrMWSruqg%252bUwj51tP%252fh1LSHuGTSIG06A4b9%252b%252fJ2ZXnVoBt6PkfN4gTY9Y%253d"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1760450027.395348,
        "hostOnly": False,
        "httpOnly": True,
        "name": "li_at",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AQEDATSE47wBen_-AAABkmc-UuMAAAGSr1sBWU4AtW0Hfb0jQyTwhiBO2dFU49xAnrN8k96vfKTKmFdBHXqIWJit2MMWaq5_AoAJoz3IvyA61Xf6n_HyLXSOKry-9_Lm_qaKKfqZPPyOv9Cj4EIxVmkh"
    },
    {
        "domain": ".linkedin.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "lang",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "v=2&lang=en-us"
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1729486170.582884,
        "hostOnly": False,
        "httpOnly": False,
        "name": "lidc",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "\"b=VB84:s=V:r=V:a=V:p=V:g=4077:u=602:x=1:i=1729435525:t=1729486175:v=2:sig=AQED6Z1F24_rfH5KRGqfyu4cAf_aKU7K\""
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1732020331.796071,
        "hostOnly": False,
        "httpOnly": False,
        "name": "AnalyticsSyncHistory",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AQL8DWijEy16jgAAAZKp9i6dpR5sU80NZm0IWfrY0sxgvpJOo_8T6KsQsm_FKMWnvN48r-GfOL-2GbLH1qZvTg"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1760964332.104362,
        "hostOnly": False,
        "httpOnly": True,
        "name": "bscookie",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "\"v=1&20241007051941468a2eb7-4ff6-4758-863c-5ad38b46bb38AQEWE-S0jw6kLzlMYKVdeEcQchsWmG-f\""
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1759845070.278864,
        "hostOnly": False,
        "httpOnly": True,
        "name": "dfpfpt",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "aeea675cabea40c5aa86509e7bd945a9"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1760450027.395488,
        "hostOnly": False,
        "httpOnly": False,
        "name": "JSESSIONID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "\"ajax:5761033954218264024\""
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1737211442.784849,
        "hostOnly": False,
        "httpOnly": False,
        "name": "li_sugr",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "a7bbf2e4-744c-41f5-b5d2-b052388c2153"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1744986859,
        "hostOnly": False,
        "httpOnly": False,
        "name": "li_theme",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "light"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1744986859,
        "hostOnly": False,
        "httpOnly": False,
        "name": "li_theme_set",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "app"
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1760450027.395453,
        "hostOnly": False,
        "httpOnly": False,
        "name": "liap",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "True"
    },
    {
        "domain": "www.linkedin.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "PLAY_SESSION",
        "path": "/",
        "sameSite": "lax",
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7ImZsb3dUcmFja2luZ0lkIjoiQ2NSbzBuQjBTdWlnaXIyK3hMM1ZWUT09In0sIm5iZiI6MTcyODMwODkzNywiaWF0IjoxNzI4MzA4OTM3fQ.3qdfFU8wtMGGf0s8Q0E6OJB_oVU6FYq-pgVAvs2AZjk"
    },
    {
        "domain": ".linkedin.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "sdsc",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "22%3A1%2C1729147361775%7EJBSK%2C0DfpJnKMQHgB3iNSUvLQmET%2BMV6g%3D"
    },
    {
        "domain": ".www.linkedin.com",
        "expirationDate": 1730644459,
        "hostOnly": False,
        "httpOnly": False,
        "name": "timezone",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "Asia/Calcutta"
    },
    {
        "domain": ".linkedin.com",
        "expirationDate": 1732020331.796049,
        "hostOnly": False,
        "httpOnly": False,
        "name": "UserMatchHistory",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AQJm4CNJcAgYhQAAAZKp9i6dmBqFFRExKBrocFFFeR_CijpR0gi0-HXaU8Phru8IwA_tzCMFyUzriw"
    }
]
    # Initialize the scraper with your API token
    scraper = LinkedInPostScraper(api_token=os.getenv("APIFY_API_KEY"), cookies = cookies)

    # Provide the LinkedIn profile URL
    profile_url = 'prajwal-waykos'

    # Scrape the profile posts
    try:
        posts = scraper.scrape_profile_posts(profile_url, max_n=2)
        if posts:
            for post in posts:
                print(post)
        else:
            print("No data retrieved.")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
