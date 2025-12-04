# market-intel-system-x
Data scraping and analysis system for real-time market  intelligence.

A Complete Twitter/X Market Sentiment Intelligence Pipeline

This project is an end-to-end market intelligence system that:

Scrapes stock-market–related tweets

Cleans + preprocesses text

Extracts hashtags/mentions/engagement metrics

Vectorizes using TF-IDF

Generates buy/sell signals

Produces final datasets & visual analysis

It is designed for analysts, data scientists, quants, and market researchers who want to track public sentiment on Indian stock markets (NIFTY, BankNifty, Sensex).

# Project Structure
market-intel-system/
│

├─ src/

│   ├─ main.py

│   │

│   ├─ scraper/

│   │   ├─ twitter_scraper.py

│   │   ├─ driver_setup.py

│   │   └─ utils.py

│   │

│   ├─ processing/

│   │   ├─ cleaner.py

│   │   └─ storage.py

│   │

│   ├─ analysis/

│   │   ├─ vectorizer.py

│   │   ├─ signal_generator.py

│   │   └─ visualization.py

│   │

│   └─ __init__.py

│

├─ logs/

│   └─ scraper.log

│

├─ data/

│   └─ processed/

│       ├─ tweets_cleaned.parquet     (sample)

│       └─ tweet_signals.parquet      (sample)

│

├─ requirements.txt

├─ environment.txt

└─ README.md


# Quick Start: Setup & Installation
1. Clone the project
2. Create virtual environment
3. Install dependencies
4. Install Chrome + ChromeDriver
5. Run the Pipeline


# 📌 Objective
The system estimates market sentiment using social media chatter from Twitter/X. Outputs serve as indicators for potential buy/sell opportunities.

# 📌 Pipeline Overview
1. Data Collection
Selenium scraper loads live Twitter search
Extracts tweets with:
content
timestamp
username
hashtags/mentions
replies/retweets/likes/views/bookmarks
All extraction is done via CSS selectors resilient to Twitter DOM changes.

2. Data Cleaning
Performed in several steps:
Removing URLs
Lowercasing
Emoji + special-character removal
Deduplication
Removing short/noisy tweets

3. Feature Extraction – TF-IDF
Unigrams + bigrams
Max vocabulary 5,000 terms
Sparse matrix used for signal model

4. Signal Generation
A lightweight numerical approach:
Total TF-IDF activation → sentiment strength
Normalized to [0, 1]
Thresholds:
> 0.7 → BUY
< 0.3 → SELL
else NEUTRAL
This is intentionally simple for interpretability.


5. Visualization
Plots sampled confidence scores.

6. Final Storage
Outputs saved as:
tweets_cleaned.parquet
tweet_signals.parquet

