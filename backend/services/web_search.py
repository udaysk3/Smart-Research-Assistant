import requests
import os
from typing import List, Dict, Any
from datetime import datetime

class WebSearchService:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for relevant information"""
        try:
            if not self.serpapi_key:
                # Fallback to a simple web search simulation
                return await self._fallback_search(query, num_results)
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("displayed_link", ""),
                        "timestamp": datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            print(f"Error in web search: {e}")
            # Fallback to mock data
            return await self._fallback_search(query, num_results)
    
    async def _fallback_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback search with mock data when SerpAPI is not available"""
        # This is a mock implementation for demonstration
        # In a real application, you might use other free search APIs
        
        mock_results = [
            {
                "title": f"Research about {query} - Academic Source",
                "link": f"https://example.com/research/{query.replace(' ', '-')}",
                "snippet": f"This is a comprehensive study about {query} that provides detailed insights and analysis.",
                "source": "example.com",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": f"Latest News on {query}",
                "link": f"https://news.example.com/{query.replace(' ', '-')}",
                "snippet": f"Recent developments and news coverage about {query} from reliable sources.",
                "source": "news.example.com",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": f"Expert Analysis: {query}",
                "link": f"https://analysis.example.com/{query.replace(' ', '-')}",
                "snippet": f"Expert opinions and detailed analysis on {query} from industry professionals.",
                "source": "analysis.example.com",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return mock_results[:num_results]
    
    async def search_news(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for recent news articles"""
        try:
            if not self.serpapi_key:
                return await self._fallback_news_search(query, num_results)
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "tbm": "nws",  # News search
                "num": num_results
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "news_results" in data:
                for result in data["news_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", ""),
                        "timestamp": datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            print(f"Error in news search: {e}")
            return await self._fallback_news_search(query, num_results)
    
    async def _fallback_news_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback news search with mock data"""
        mock_news = [
            {
                "title": f"Breaking: Latest Updates on {query}",
                "link": f"https://news.example.com/breaking/{query.replace(' ', '-')}",
                "snippet": f"Breaking news and latest updates about {query} from reliable news sources.",
                "source": "News Source",
                "date": "Today",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": f"Industry Report: {query} Trends",
                "link": f"https://industry.example.com/reports/{query.replace(' ', '-')}",
                "snippet": f"Industry analysis and trend reports on {query} from market experts.",
                "source": "Industry Report",
                "date": "This week",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return mock_news[:num_results]


