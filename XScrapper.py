from apify_client import ApifyClient
import re
from utils import get_date_7_days_before_today
import os
from dotenv import load_dotenv
load_dotenv()
class XScraper:
    def __init__(self, api_token):
        """
        Initializes the XScraper with the provided Apify API token.

        :param api_token: Your Apify API token.
        """
        if not api_token:
            raise ValueError("API token must be provided.")
        self.client = ApifyClient(api_token)

    def scrape_tweets(self, twitter_handle, max_tweets=100, newer_than = get_date_7_days_before_today()):
        """
        Scrapes tweets from the given Twitter handle.

        :param twitter_handle: The Twitter handle of the user to scrape tweets from.
        :param max_tweets: The maximum number of tweets to retrieve.
        :return: A list of dictionaries containing tweet details.
        """
        # Validate the Twitter handle
        if not self._is_valid_twitter_handle(twitter_handle):
            raise ValueError("Invalid Twitter handle.")

        # Prepare the Actor input
        run_input = {
            "handles": [twitter_handle],
            "tweetsDesired": max_tweets,
            "proxyConfig": { "useApifyProxy": True },
        }

        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor("quacker/twitter-scraper").call(run_input=run_input)
        except Exception as e:
            print(f"An error occurred while running the actor: {e}")
            return None

        items = self.get_items(run)
        
        tweets = self.extract_tweets(items)
        return tweets

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

    def extract_tweets(self, items):
        """
        Extracts tweets from the scraped dataset.

        :param items: A list of items from the dataset.
        :return: A list of dictionaries containing tweet details.
        """
        tweets = []
        for item in items:
           output_format = {
               "type": "",
               "content_urls": []
           }
           if item.get("entities"):
               if item['entities'].get("media"):
                   for med in  item['entities'].get("media"):
                       output_format['type'] = med['type']
                       print(med)

                       if med['type'] == "photo":
                           print("entered photo")
                           output_format['content_urls'] = [med['media_url_https']]
                       elif med['type'] == "video":
                           video_info_variants = med['video_info']['variants']
                           for vid in video_info_variants:
                               if vid['content_type' ] == "video/mp4":
                                    output_format['content_urls'] = [vid['url']]
                                    break
                       else:
                           print("Triggered a different Media-type")
                       tweets.append(output_format)
               else:
                   print("No media")
           if item.get('quoted_status'):
               if item['quoted_status'].get("entities"):
                   for med in  item['quoted_status']['entities']['media']:
                       output_format['type'] = med['type']
                       print(med)

                       if med['type'] == "photo":
                           print("entered photo")
                           output_format['content_urls'] = [med['media_url_https']]
                       elif med['type'] == "video":
                           video_info_variants = med['video_info']['variants']
                           for vid in video_info_variants:
                               if vid['content_type' ] == "video/mp4":
                                    output_format['content_urls'] = [vid['url']]
                                    break
                       else:
                           print("Triggered a different Media-type")
                       tweets.append(output_format)
               else:
                   print("No qouted texted entities")
           else:
               print("Neither entities nor quoted status found")
               
                   
        return tweets
                                   
                               
                               

                           
                           
               

    def _is_valid_twitter_handle(self, handle):
        """
        Validates if the provided string is a valid Twitter handle.

        :param handle: The Twitter handle to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^@?(\w){1,15}$'
        return re.match(pattern, handle) is not None


if __name__ == "__main__":
    # Example usage of the XScraper class

    # Initialize the scraper with your Apify API token
    api_token = os.getenv("APIFY_API_KEY")
    scraper = XScraper(api_token)

    # Specify the Twitter handle and the maximum number of tweets to scrape
    twitter_handle = 'elonmusk'
    max_tweets = 100

    # Scrape tweets
    tweets = scraper.scrape_tweets(twitter_handle, max_tweets)

    # Check if tweets were successfully retrieved
    if tweets:
        print(tweets)
    else:
        print("No tweets were retrieved.")
