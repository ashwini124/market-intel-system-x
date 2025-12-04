import pandas as pd
import time
from scraper.twitter_scraper import TweetScraper, HASHTAGS

# Remove this import since we're extracting in the scraper now
# from scraper.utils import extract_text_entities

from processing.cleaner import clean
from processing.storage import save_parquet
from analysis.vectorizer import compute_tfidf
from analysis.signal_generator import generate_signals
from analysis.visualization import plot_sampled_signal

def run_pipeline():
    scraper = None
    
    try:
        scraper = TweetScraper()

        print("\n🟦 Login to Twitter")
        scraper.login()

        all_tweets = []
        failed_hashtags = []
        
        # Configuration
        DAYS_BACK = 3  # Look back 3 days for tweets
        TARGET_TWEETS = 2000  # Stop if we reach this many

        for idx, tag in enumerate(HASHTAGS):
            print(f"\n{'='*50}")
            print(f"📍 Processing {idx + 1}/{len(HASHTAGS)}: {tag}")
            print('='*50)
            
            try:
                tweets = scraper.search_and_scrape(tag)
                
                if tweets:
                    all_tweets.extend(tweets)
                    print(f"✅ Collected {len(tweets)} tweets for {tag}")
                    print(f"📊 Total so far: {len(all_tweets)} tweets")
                    
                    # Show sample with all new fields
                    sample = tweets[0]
                    print(f"\n📝 Sample tweet:")
                    print(f"   Content: {sample['content'][:80]}...")
                    print(f"   Username: @{sample['username']}")
                    print(f"   Likes: {sample['likes']}, Retweets: {sample['retweets']}")
                    print(f"   Hashtags: {sample['hashtags'][:3]}")
                    print(f"   Mentions: {sample['mentions'][:3]}")
                else:
                    print(f"⚠️ No tweets found for {tag}")
                    failed_hashtags.append(tag)
                
                # Add delay between hashtags to prevent rate limiting
                if idx < len(HASHTAGS) - 1:
                    wait_time = 10
                    print(f"\n⏳ Waiting {wait_time} seconds before next hashtag to avoid rate limiting...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"❌ Error with {tag}: {str(e)}")
                failed_hashtags.append(tag)
                if idx < len(HASHTAGS) - 1:
                    print(f"⏳ Waiting 15 seconds before next hashtag...")
                    time.sleep(15)
                continue

        # Summary of collection phase
        print("\n" + "="*50)
        print("📊 COLLECTION SUMMARY")
        print("="*50)
        print(f"✅ Successful hashtags: {len(HASHTAGS) - len(failed_hashtags)}/{len(HASHTAGS)}")
        if failed_hashtags:
            print(f"⚠️ Failed hashtags: {', '.join(failed_hashtags)}")
        print(f"📦 Total tweets collected: {len(all_tweets)}")

        if not all_tweets:
            print("\n" + "="*50)
            print("❌ No tweets collected. Debugging tips:")
            print("="*50)
            print("1. Check if you're logged into Twitter/X")
            print("2. Manually search for hashtags in the browser")
            print("3. Check if tweets are visible in the browser window")
            print("4. Look at logs/scraper.log for details")
            print("5. Check debug_screenshots folder for screenshots")
            print("\n💡 Common issues:")
            print("   - Rate limiting (wait 15 min and retry)")
            print("   - Not logged in properly")
            print("   - Twitter structure changed")
            print("   - Hashtags have no recent activity")
            return

        print("\n" + "="*50)
        print(f"🎉 Successfully collected {len(all_tweets)} tweets!")
        print("="*50)

        print("\n🟩 Building DataFrame...")
        df = pd.DataFrame(all_tweets)
        print(f"📋 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show distribution across hashtags
        print("\n📊 Tweets per hashtag:")
        print(df['searched_tag'].value_counts().to_string())
        
        # Show engagement statistics
        print("\n📊 Engagement Statistics:")
        print(f"   Average likes: {df['likes'].mean():.0f}")
        print(f"   Average retweets: {df['retweets'].mean():.0f}")
        print(f"   Average replies: {df['replies'].mean():.0f}")
        print(f"   Total views: {df['views'].sum():,.0f}")
        
        # Show hashtag and mention statistics
        print("\n🏷️ Hashtag & Mention Statistics:")
        print(f"   Tweets with hashtags: {(df['num_hashtags'] > 0).sum()} ({(df['num_hashtags'] > 0).sum()/len(df)*100:.1f}%)")
        print(f"   Tweets with mentions: {(df['num_mentions'] > 0).sum()} ({(df['num_mentions'] > 0).sum()/len(df)*100:.1f}%)")
        print(f"   Average hashtags per tweet: {df['num_hashtags'].mean():.1f}")
        print(f"   Average mentions per tweet: {df['num_mentions'].mean():.1f}")

        # Note: We don't need to extract hashtags/mentions again since scraper does it
        # df["hashtags"], df["mentions"] = zip(*df["content"].apply(extract_text_entities))

        print("\n🧹 Cleaning data...")
        df = clean(df)
        print(f"✅ After cleaning: {len(df)} tweets remain")
        
        print("\n💾 Saving cleaned data...")
        save_parquet(df, "data/processed/tweets_cleaned.parquet")
        print("✅ Saved: data/processed/tweets_cleaned.parquet")

        print("\n🔢 Computing TF-IDF...")
        X, vec = compute_tfidf(df["content"])
        print(f"✅ TF-IDF matrix shape: {X.shape}")
        
        print("\n📊 Generating signals...")
        signals = generate_signals(X)

        print("\n📈 Creating visualization...")
        plot_sampled_signal(signals["confidence"])

        df["buy_signal"] = signals["buy"]
        df["sell_signal"] = signals["sell"]
        df["confidence"] = signals["confidence"]

        print("\n💾 Saving final data...")
        save_parquet(df, "data/processed/tweet_signals.parquet")
        print("✅ Saved: data/processed/tweet_signals.parquet")

        # Detailed Summary
        print("\n" + "="*50)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"📊 Total tweets processed: {len(df)}")
        print(f"📈 Buy signals generated: {df['buy_signal'].sum()} ({df['buy_signal'].sum()/len(df)*100:.1f}%)")
        print(f"📉 Sell signals generated: {df['sell_signal'].sum()} ({df['sell_signal'].sum()/len(df)*100:.1f}%)")
        print(f"💯 Average confidence: {df['confidence'].mean():.3f}")
        print(f"📈 Max confidence: {df['confidence'].max():.3f}")
        print(f"📉 Min confidence: {df['confidence'].min():.3f}")
        
        # Show top confident tweets with engagement
        print("\n🔝 Top 3 most confident signals:")
        top_signals = df.nlargest(3, 'confidence')[['content', 'confidence', 'buy_signal', 'sell_signal', 'likes', 'retweets']]
        for idx, row in top_signals.iterrows():
            signal_type = "BUY" if row['buy_signal'] else "SELL" if row['sell_signal'] else "NEUTRAL"
            print(f"\n  {signal_type} (confidence: {row['confidence']:.3f})")
            print(f"  Engagement: {row['likes']} likes, {row['retweets']} retweets")
            print(f"  {row['content'][:100]}...")
        
        # Show most engaged tweets
        print("\n❤️ Top 3 most liked tweets:")
        top_liked = df.nlargest(3, 'likes')[['content', 'likes', 'retweets', 'username']]
        for idx, row in top_liked.iterrows():
            print(f"\n  @{row['username']} - {row['likes']} likes, {row['retweets']} retweets")
            print(f"  {row['content'][:100]}...")
        
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close browser
        if scraper:
            print("\n🔴 Closing browser...")
            scraper.close()

if __name__ == "__main__":
    run_pipeline()