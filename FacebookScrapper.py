from apify_client import ApifyClient
import re
import os
from dotenv import load_dotenv
load_dotenv()

from utils import get_date_7_days_before_today
class FacebookPostScraper:
    def __init__(self, api_token):
        """
        Initializes the FacebookPostScraper with the provided Apify API token.

        :param api_token: Your Apify API token.
        """
        if not api_token:
            raise ValueError("API token must be provided.")
        self.client = ApifyClient(api_token)

    def scrape_page_posts(self, fb_username, max_results=20,newer_than =get_date_7_days_before_today() ):
        """
        Scrapes posts from the given Facebook page URL.

        :param page_url: The URL of the Facebook page to scrape.
        :param max_results: The maximum number of posts to retrieve.
        :return: A list of dictionaries containing post details.
        """
        page_url = f'https://www.facebook.com/{fb_username}/'
        # Validate the page URL
        if not self._is_valid_facebook_page_url(page_url):
            raise ValueError("Invalid Facebook page URL.")

        # Prepare the Actor input
        run_input = {
            "startUrls": [{"url": page_url}],
            "resultsLimit": max_results,
            "maxPosts": max_results,
            "proxyConfiguration": {
                "useApifyProxy": True,
                # Uncomment and specify proxy groups if needed
                # "apifyProxyGroups": ["RESIDENTIAL"]
            },
            # "cookies": self.cookies,  # Include cookies if required
            "onlyPostsNewerThan": newer_than
        }

        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
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
        Extracts posts from the scraped page data.

        :param items: A list of items from the dataset.
        :return: A list of dictionaries containing post details.
        """
        posts = []
        for item in items:
            if item.get("media", None):
                media = item.get("media", None)
                for me in media:
                    if me.get("__typename"):
                        if me.get("__typename") == "Photo":

                            if me.get("image"):
                                output_format = {
                                    "type" : me.get("__typename"),
                                    "content_urls" : [me['image']['uri']]
                                        }
                            elif me.get("photo_image"):
                                output_format = {
                                    "type" : me.get("__typename"),
                                    "content_urls" : [me['photo_image']['uri']]
                                        }

                            posts.append(output_format)
        return posts

    def _is_valid_facebook_page_url(self, url):
        """
        Validates if the provided URL is a valid Facebook page URL.

        :param url: The URL to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^https?://(www\.)?facebook\.com/[^/]+/?$'
        return re.match(pattern, url) is not None

if __name__ == "__main__":
    # Initialize the scraper
    api_token = os.getenv("APIFY_API_KEY")
    scraper = FacebookPostScraper(api_token)

    # Scrape posts from a Facebook page
    page_url = 'humansofnewyork'
    max_results = 20  # Specify the number of posts you want to retrieve

    posts = scraper.scrape_page_posts(page_url, max_results, newer_than= "2024-01-01")

    print("Posts")


    # Output the scraped posts
    for post in posts:
        print(post)
