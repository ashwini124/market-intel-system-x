import time
import logging
import os
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from .driver_setup import get_driver


HASHTAGS = ["#nifty", "#nifty50", "#niftyanalysis", "#banknifty", "#sensex", "#indianstockmarket", 
            "#stockmarketindia", "#niftylevels", "#bankniftylevels",
            "#nse", "#bse", "#intraday", "#intradaytrading", "#optionbuying", "#optionselling"]
SCROLL_LIMIT = 50
MIN_TWEETS_REQUIRED = 2000


class TweetScraper:
    def __init__(self):
        self.driver = get_driver(headless=False)
        logging.basicConfig(filename="logs/scraper.log", level=logging.INFO)
        os.makedirs("debug_screenshots", exist_ok=True)

    # ------------------------------------------
    # LOGIN
    # ------------------------------------------
    def login(self):
        """Navigate to Twitter and wait for manual login"""
        print("\n🔐 Opening Twitter/X login page...")
        self.driver.get("https://x.com/login")
        time.sleep(5)

        print("\n➡️ Please log in manually in the browser window.")
        print("➡️ After login, reach the Home page.")
        input("\nPress ENTER once you are fully logged in... ")
        
        time.sleep(3)
        print("✅ Login confirmed!")

    # ------------------------------------------
    # BASIC UTILITIES
    # ------------------------------------------
    def take_debug_screenshot(self, name):
        try:
            path = f"debug_screenshots/{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
        except:
            pass

    def extract_hashtags(self, text):
        return list(set(re.findall(r'#\w+', text))) if text else []

    def extract_mentions(self, text):
        return list(set(re.findall(r'@\w+', text))) if text else []

    def extract_engagement_metrics(self, t):
        metrics = {"replies": 0, "retweets": 0, "likes": 0, "views": 0, "bookmarks": 0}

        try:
            buttons = t.find_elements(By.CSS_SELECTOR, "[aria-label]")
            for b in buttons:
                label = b.get_attribute("aria-label") or ""
                label_lower = label.lower()
                num = self.parse_count(label)

                if "repl" in label_lower:
                    metrics["replies"] = num
                elif "repost" in label_lower or "retweet" in label_lower:
                    metrics["retweets"] = num
                elif "like" in label_lower:
                    metrics["likes"] = num
                elif "view" in label_lower:
                    metrics["views"] = num
                elif "bookmark" in label_lower:
                    metrics["bookmarks"] = num

        except:
            pass

        return metrics

    def parse_count(self, text):
        try:
            match = re.search(r"([\d,.]+)\s*([KMB])?", text)
            if not match:
                return 0

            num = float(match.group(1).replace(",", ""))
            mult = match.group(2)

            if mult == "K":
                num *= 1_000
            elif mult == "M":
                num *= 1_000_000
            elif mult == "B":
                num *= 1_000_000_000

            return int(num)
        except:
            return 0

    # ------------------------------------------
    # PAGE LOADING & SCROLLING
    # ------------------------------------------
    def wait_for_tweets(self):
        selectors = [
            "article[data-testid='tweet']",
            "div[data-testid='tweet']",
            "article",
            "div[data-testid='cellInnerDiv']"
        ]

        for s in selectors:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, s))
                )
                return True
            except:
                continue

        return False

    def scroll_page(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(2)

    def get_tweet_elements(self):
        selectors = [
            "article[data-testid='tweet']",
            "div[data-testid='cellInnerDiv']",
            "article",
        ]

        for s in selectors:
            tweets = self.driver.find_elements(By.CSS_SELECTOR, s)
            if tweets:
                return tweets

        return []

    # ------------------------------------------
    # MAIN SCRAPER
    # ------------------------------------------
    def search_and_scrape(self, hashtag, days_back=1):
        """
        Scrape tweets for a hashtag
        
        Args:
            hashtag: Hashtag to search (e.g., '#nifty50')
            days_back: Number of days to look back (default: 3)
        """
        # ✅ FIXED: Made date range configurable and wider
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        # Remove spaces from hashtag for cleaner URL
        clean_hashtag = hashtag.replace(" ", "")
        query = f"{clean_hashtag} since:{start_date} until:{today}"
        
        encoded = (
            query.replace("#", "%23")
                 .replace(":", "%3A")
                 .replace(" ", "%20")
        )

        url = f"https://x.com/search?q={encoded}&src=typed_query&f=live"
        print(f"🔗 Searching: {url}")
        self.driver.get(url)

        time.sleep(8)

        if not self.wait_for_tweets():
            print(f"⚠️ No tweets found for {hashtag}")
            return []

        tweets_data = []
        seen = set()
        no_new_scrolls = 0

        for scroll_i in range(SCROLL_LIMIT):
            before = len(tweets_data)
            tweet_elements = self.get_tweet_elements()

            for t in tweet_elements:
                try:
                    content = ""
                    try:
                        content = t.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']").text.strip()
                    except:
                        try:
                            content = t.find_element(By.CSS_SELECTOR, "div[lang]").text.strip()
                        except:
                            continue

                    if len(content) < 5:
                        continue

                    # unique signature (user + content)
                    sig = hash(content)
                    if sig in seen:
                        continue

                    seen.add(sig)

                    # ✅ FIXED: Better username extraction
                    username = "NA"
                    try:
                        # Try method 1: Look for user link in User-Name div
                        user_link = t.find_element(By.CSS_SELECTOR, "div[data-testid='User-Name'] a[role='link']")
                        href = user_link.get_attribute('href')
                        if href:
                            username = href.rstrip('/').split('/')[-1]
                    except:
                        try:
                            # Method 2: Find any link matching Twitter profile pattern
                            user_links = t.find_elements(By.CSS_SELECTOR, "a[href]")
                            for link in user_links:
                                href = link.get_attribute("href") or ""
                                # Match pattern: https://x.com/username or https://twitter.com/username
                                if re.match(r"https://(x|twitter)\.com/[A-Za-z0-9_]+/?$", href):
                                    username = href.rstrip('/').split('/')[-1]
                                    break
                        except:
                            pass

                    # timestamp
                    timestamp = None
                    try:
                        timestamp = t.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                    except:
                        pass

                    hashtags = self.extract_hashtags(content)
                    mentions = self.extract_mentions(content)
                    engagement = self.extract_engagement_metrics(t)

                    tweet = {
                        "username": username,
                        "timestamp": timestamp,
                        "content": content,
                        "searched_tag": hashtag,
                        "hashtags": hashtags,
                        "mentions": mentions,
                        "num_hashtags": len(hashtags),
                        "num_mentions": len(mentions),
                        **engagement
                    }

                    tweets_data.append(tweet)

                except Exception as e:
                    logging.warning(f"Tweet parse error: {e}")
                    continue

            added = len(tweets_data) - before
            
            # ✅ IMPROVED: Show progress every 10 scrolls
            if scroll_i % 10 == 0 or added > 0:
                print(f"[{hashtag}] +{added} tweets (total {len(tweets_data)}), scroll {scroll_i+1}/{SCROLL_LIMIT}")

            if added == 0:
                no_new_scrolls += 1
                if no_new_scrolls >= 4:
                    print(f"⚠️ No new tweets after 4 scrolls. Stopping early.")
                    break
            else:
                no_new_scrolls = 0

            self.scroll_page()

        print(f"✅ Finished {hashtag}: {len(tweets_data)} tweets")
        return tweets_data

    # ------------------------------------------
    def close(self):
        if self.driver:
            self.driver.quit()
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.close()
        except:
            pass