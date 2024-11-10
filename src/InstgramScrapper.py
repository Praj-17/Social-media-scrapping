import re
from apify_client import ApifyClient
import os
import json
from dotenv import load_dotenv
load_dotenv()

class InstagramPostScraper:
    def __init__(self, api_token):
        """
        Initializes the InstagramPostScraper with the provided Apify API token.

        :param api_token: Your Apify API token.
        """
        if not api_token:
            raise ValueError("API token must be provided.")
        self.client = ApifyClient(api_token)

    def scrape_profile(self, username,newer_than = None,  max_n=5):
        """
        Scrapes posts from the given Instagram profile URL.

        :param profile_url: The URL of the Instagram profile to scrape.
        :param max_n: The maximum number of posts to retrieve.
        :return: A list of dictionaries containing post type and content URLs.
        """

        profile_url =f"https://www.instagram.com/{username}/"
        # Validate the profile URL
        if not re.match(r'^https?://(www\.)?instagram\.com/[^/]+/?$', profile_url):
            raise ValueError("Invalid Instagram profile URL.")

        # Prepare the Actor input
        run_input = {
            "directUrls": [profile_url],
            "resultsType": "posts",
            "resultsLimit": max_n, # Quantity
            "proxyConfiguration": {
                "useApifyProxy": True,
                # Uncomment and specify proxy groups if needed
                # "apifyProxyGroups": ["RESIDENTIAL"]
                "searchType": "hashtag",
                "searchLimit": 1,
            },
            "onlyPostsNewerThan": newer_than # Date 
        }

        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
        except Exception as e:
            print(f"An error occurred while running the actor: {e}")
            return None

        items = self.get_items(run)
        outputs = self.process_items(items)
        return outputs

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

    def process_items(self, items):
        """
        Processes the items retrieved from the dataset to extract required data.

        :param items: A list of items from the dataset.
        :return: A list of processed data containing post type and content URLs.
        """
        outputs = []
        for item in items:
            timestamp = item.get("timestamp", None)
            output = self.get_required_data_for_user(item)
            if output:
                timestamp = item.get("timestamp", None)
                output['timestamp'] = timestamp
                output['social_media'] = "instagram"
                location = item.get("location", None)
                output['location'] = location
                outputs.append(output)
        return outputs

    def get_required_data_for_user(self, item):
        """
        Extracts required data from a single item.

        :param item: A single item from the dataset.
        :return: A dictionary with the post type and content URLs.
        """
        content_type = item.get("type")
        types = ["Video", "Image", "Sidecar"]

        if content_type in types:
            output_format = {
                "type": content_type,
                "content_urls": [],
            }
            if content_type == "Video":
                video_url = item.get("videoUrl")
                if video_url:
                    output_format["content_urls"] = [video_url]
            elif content_type == "Image":
                display_url = item.get("displayUrl")
                if display_url:
                    output_format["content_urls"] = [display_url]
            elif content_type == "Sidecar":
                images = item.get("images")
                if images:
                    output_format["content_urls"] = images
            else:
                return None
            return output_format
        else:
            return None


if __name__ == "__main__":
    # Import the class
    # from instagram_post_scraper import InstagramPostScraper

    # Initialize the scraper with your API token
    
    scraper = InstagramPostScraper(api_token=os.getenv("APIFY_API_KEY"))

    # Provide the Instagram profile URL
    profile_url = "steveyeun"

    # Scrape the profile
    try:
        outputs = scraper.scrape_profile(profile_url, max_n=20)
        if outputs:
            for output in outputs:
                print(output)
            with open("insta_output_2.json", "w+") as f:
                json.dump(outputs, f)
        else:
            print("No data retrieved.")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

