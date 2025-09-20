#!/usr/bin/env python3
"""
Pathway Live Data Ingestion for Smart Research Assistant
"""
import requests
import pathway as pw
import feedparser
from datetime import datetime
import json
import os

# RSS feeds for live data
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://rss.cnn.com/rss/edition_technology.rss",
    "https://feeds.feedburner.com/oreilly/radar",
    "https://feeds.feedburner.com/techcrunch/",
    "https://www.wired.com/feed/rss"
]

def fetch_live_data():
    """Fetch live data from RSS feeds"""
    print("🔄 Fetching live data from RSS feeds...")
    
    live_data = []
    for feed_url in RSS_FEEDS:
        try:
            print(f"📡 Fetching from: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:3]:  # Get latest 3 articles per feed
                data = {
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", ""),
                    "source": feed.feed.get("title", feed_url),
                    "published": entry.get("published", ""),
                    "url": entry.get("link", ""),
                    "timestamp": datetime.now().isoformat(),
                    "category": "technology"
                }
                live_data.append(data)
                print(f"   ✅ {data['title'][:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error fetching {feed_url}: {e}")
    
    print(f"📊 Total articles fetched: {len(live_data)}")
    return live_data

def save_live_data(data):
    """Save live data to JSON file"""
    output_file = "live_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Live data saved to: {output_file}")

def main():
    print("🚀 Pathway Live Data Ingestion")
    print("=" * 50)
    
    # Fetch live data
    live_data = fetch_live_data()
    
    if live_data:
        # Save to file
        save_live_data(live_data)
        
        # Display summary
        print("\n📈 Live Data Summary:")
        print(f"   📰 Total articles: {len(live_data)}")
        print(f"   🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show sources
        sources = set(item['source'] for item in live_data)
        print(f"   📡 Sources: {len(sources)}")
        for source in sources:
            print(f"      • {source}")
        
        print("\n✅ Live data ingestion completed!")
        print("🔗 This data is now available for research queries")
        
    else:
        print("❌ No live data fetched")

if __name__ == "__main__":
    main()
