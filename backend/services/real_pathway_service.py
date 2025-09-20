import requests
import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

class RealPathwayService:
    def __init__(self):
        self.pathway_host = os.getenv("PATHWAY_HOST", "localhost")
        self.pathway_port = os.getenv("PATHWAY_PORT", "8001")
        self.pathway_api_key = os.getenv("PATHWAY_API_KEY")
        self.base_url = f"http://{self.pathway_host}:{self.pathway_port}"
        
        # News API for live data (free tier available)
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.news_base_url = "https://newsapi.org/v2"
        
        # RSS feeds for live data
        self.rss_feeds = [
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://rss.cnn.com/rss/edition_technology.rss",
            "https://feeds.feedburner.com/oreilly/radar",
        ]
    
    async def get_live_data(self, query: str) -> List[Dict[str, Any]]:
        """Get real live data from multiple sources"""
        try:
            live_data = []
            
            # Get news data
            news_data = await self._get_news_data(query)
            live_data.extend(news_data)
            
            # Get RSS feed data
            rss_data = await self._get_rss_data(query)
            live_data.extend(rss_data)
            
            # Get Pathway data if available
            pathway_data = await self._get_pathway_data(query)
            live_data.extend(pathway_data)
            
            # Get data from local live_data.json if available
            local_data = await self._get_local_live_data(query)
            live_data.extend(local_data)
            
            return live_data[:10]  # Limit to 10 most recent items
            
        except Exception as e:
            print(f"Error getting live data: {e}")
            return []
    
    async def _get_news_data(self, query: str) -> List[Dict[str, Any]]:
        """Get news data from News API"""
        if not self.news_api_key:
            return []
        
        try:
            url = f"{self.news_base_url}/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            live_data = []
            for article in articles:
                live_data.append({
                    "content": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "News API"),
                    "url": article.get("url", ""),
                    "title": article.get("title", ""),
                    "timestamp": article.get("publishedAt", ""),
                    "type": "news"
                })
            
            return live_data
            
        except Exception as e:
            print(f"Error fetching news data: {e}")
            return []
    
    async def _get_rss_data(self, query: str) -> List[Dict[str, Any]]:
        """Get data from RSS feeds"""
        try:
            import feedparser
            
            live_data = []
            for feed_url in self.rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:3]:  # Get top 3 from each feed
                        # Simple keyword matching
                        if any(keyword.lower() in entry.title.lower() or 
                               keyword.lower() in entry.get("summary", "").lower() 
                               for keyword in query.split()):
                            
                            live_data.append({
                                "content": entry.get("summary", entry.title),
                                "source": feed.feed.get("title", "RSS Feed"),
                                "url": entry.get("link", ""),
                                "title": entry.title,
                                "timestamp": entry.get("published", ""),
                                "type": "rss"
                            })
                
                except Exception as e:
                    print(f"Error parsing RSS feed {feed_url}: {e}")
                    continue
            
            return live_data
            
        except ImportError:
            print("feedparser not installed. Install with: pip install feedparser")
            return []
        except Exception as e:
            print(f"Error fetching RSS data: {e}")
            return []
    
    async def _get_pathway_data(self, query: str) -> List[Dict[str, Any]]:
        """Get data from Pathway if configured"""
        if not self.pathway_api_key:
            return []
        
        try:
            url = f"{self.base_url}/api/search"
            headers = {
                "Authorization": f"Bearer {self.pathway_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": query,
                "limit": 5
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            live_data = []
            for result in results:
                live_data.append({
                    "content": result.get("content", ""),
                    "source": result.get("source", "Pathway"),
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "timestamp": result.get("timestamp", ""),
                    "type": "pathway"
                })
            
            return live_data
            
        except Exception as e:
            print(f"Error fetching Pathway data: {e}")
            return []
    
    async def setup_pathway_connection(self):
        """Setup connection to Pathway data source"""
        try:
            if not self.pathway_api_key:
                print("Pathway API key not configured")
                return False
            
            url = f"{self.base_url}/api/health"
            headers = {
                "Authorization": f"Bearer {self.pathway_api_key}"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            print("Pathway connection established")
            return True
            
        except Exception as e:
            print(f"Error setting up Pathway connection: {e}")
            return False
    
    async def ingest_data_source(self, source_url: str, source_type: str = "rss"):
        """Ingest data from a live source using Pathway"""
        try:
            if not self.pathway_api_key:
                return None
            
            url = f"{self.base_url}/api/ingest"
            headers = {
                "Authorization": f"Bearer {self.pathway_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "source_url": source_url,
                "source_type": source_type,
                "auto_update": True
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"Started ingesting {source_type} from {source_url}")
            return result
            
        except Exception as e:
            print(f"Error ingesting data source: {e}")
            return None
    
    async def get_freshness_score(self, query: str) -> Dict[str, Any]:
        """Get freshness score for a query based on recent data"""
        try:
            live_data = await self.get_live_data(query)
            
            if not live_data:
                return {"score": 0, "message": "No recent data available"}
            
            # Calculate average age of data
            now = datetime.now()
            total_age_minutes = 0
            valid_timestamps = 0
            
            for item in live_data:
                if item.get("timestamp"):
                    try:
                        # Parse various timestamp formats
                        timestamp_str = item["timestamp"]
                        if "T" in timestamp_str:
                            item_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        else:
                            item_time = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
                        
                        age_minutes = (now - item_time).total_seconds() / 60
                        total_age_minutes += age_minutes
                        valid_timestamps += 1
                    except:
                        continue
            
            if valid_timestamps == 0:
                return {"score": 50, "message": "Data available but timestamps unclear"}
            
            avg_age_minutes = total_age_minutes / valid_timestamps
            
            # Convert to freshness score (0-100)
            if avg_age_minutes < 60:  # Less than 1 hour
                freshness_score = 100
            elif avg_age_minutes < 1440:  # Less than 1 day
                freshness_score = 80
            elif avg_age_minutes < 10080:  # Less than 1 week
                freshness_score = 60
            else:
                freshness_score = 40
            
            return {
                "score": freshness_score,
                "avg_age_minutes": avg_age_minutes,
                "data_points": len(live_data),
                "message": f"Data is {avg_age_minutes:.0f} minutes old on average"
            }
            
        except Exception as e:
            print(f"Error calculating freshness score: {e}")
            return {"score": 0, "message": "Error calculating freshness"}
    
    async def _get_local_live_data(self, query: str) -> List[Dict[str, Any]]:
        """Get live data from local JSON file"""
        try:
            if os.path.exists("live_data.json"):
                with open("live_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Filter data based on query
                filtered_data = []
                query_lower = query.lower()
                
                for item in data:
                    if (query_lower in item.get("title", "").lower() or 
                        query_lower in item.get("content", "").lower()):
                        filtered_data.append({
                            "title": item.get("title", ""),
                            "content": item.get("content", ""),
                            "source": item.get("source", ""),
                            "url": item.get("url", ""),
                            "published": item.get("published", ""),
                            "timestamp": item.get("timestamp", ""),
                            "type": "live_data"
                        })
                
                return filtered_data[:5]  # Limit to 5 items
            else:
                return []
                
        except Exception as e:
            print(f"Error getting local live data: {e}")
            return []
