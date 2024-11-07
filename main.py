from FacebookScrapper import FacebookPostScraper
from InstgramScrapper import InstagramPostScraper
from LinkedinScrapper import LinkedInPostScraper
from XScrapper import XScraper
import os
from dotenv import load_dotenv
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
    
    def scrape_all_social_media(self, x_username, instgram_username, facebook_username, linkedin_username, max_n = 10):
        
        tweets = self.x.scrape_tweets(x_username,max_n )

        insta_posts = self.ins.scrape_profile(instgram_username, max_n)

        fb_posts = self.fb.scrape_page_posts(facebook_username, max_results=max_n)

        if self.li:
            linkedin_posts = self.li.scrape_profile_posts(linkedin_username, max_results=max_n)
        else:
            linkedin_posts = None
        
        if linkedin_posts:
            ans = tweets + insta_posts + fb_posts  + linkedin_posts 
        else:
            ans = tweets + insta_posts + fb_posts
        return ans

if __name__ == "__main__":
    api_key = os.getenv("APIFY_API_KEY")
    cookies = ""

    sm = SocialMediaScrapper(api_key)
    handles = {
        "instgram_username": "elonmusk__official__",
        "facebook_username": "elon.musk.436479",
        "linkedin_username": "prajwal-waykos",
        "x_username": "elonmusk"
    }
    output = sm.scrape_all_social_media(**handles)
    import json

    with open("output.json", "w+") as f:
        json.dump(output, f)