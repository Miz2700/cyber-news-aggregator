import requests
import feedparser
from datetime import datetime, timedelta
import logging
import time
from typing import List, Dict, Any
import re

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, news_api_key):
        self.news_api_key = news_api_key
        self.base_url = "https://newsapi.org/v2"
        
        # Feed RSS cyber security
        self.cyber_rss_feeds = [
            "https://feeds.feedburner.com/TheHackersNews",
            "https://krebsonsecurity.com/feed/",
            "https://www.bleepingcomputer.com/feed/",
            "https://feeds.feedburner.com/securityweek",
            "https://www.darkreading.com/rss.xml",
            "https://feeds.feedburner.com/eset/blog",
            "https://www.schneier.com/feed/atom/",
            "https://www.csoonline.com/index.rss",
            "https://www.infosecurity-magazine.com/rss/news/",
            "https://cybersecuritynews.com/feed/",
            "https://feeds.feedburner.com/SecurityIntelligence",
            "https://www.cyberscoop.com/feed",
            "https://www.securitymagazine.com/rss/topic/2236-cyber-security",
            "https://threatpost.com/feed/",
            "https://feeds.feedburner.com/tripwire-state-of-security",
            "https://www.recordedfuture.com/feed",
            "https://cyware.com/allnews/feed",
            "https://www.helpnetsecurity.com/feed/",
            "https://www.fireeye.com/blog/feed",
            "https://www.fortinet.com/blog/rss.xml"
        ]
        
        # Feed RSS geopolitica
        self.geopolitical_rss_feeds = [
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.reuters.com/rssFeed/worldNews",
            "https://feeds.reuters.com/reuters/politicsNews",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.npr.org/1004/rss.xml",
            "https://www.dw.com/en/rss/all/rss.xml",
            "https://feeds.feedburner.com/france24-en-international",
            "https://www.rt.com/rss/",
            "https://feeds.skynews.com/feeds/rss/world.xml",
            "https://feeds.reuters.com/Reuters/worldNews",
            "https://www.theguardian.com/world/rss",
            "https://feeds.washingtonpost.com/rss/world",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://www.foreignaffairs.com/rss.xml",
            "https://feeds.feedburner.com/DefenseNewsBreaking",
            "https://www.janes.com/feeds/defence-news.xml",
            "https://www.defensenews.com/arc/outboundfeeds/rss/category/global/?outputType=xml",
            "https://feeds.feedburner.com/stratfor",
            "https://www.cfr.org/feeds/net-politics"
        ]

    def collect_news_api(self, keywords: List[str], category: str = None) -> List[Dict[str, Any]]:
        """Raccoglie notizie da NewsAPI"""
        articles = []
        
        for keyword in keywords:
            try:
                params = {
                    'q': keyword,
                    'apiKey': self.news_api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 100
                }
                
                if category:
                    params['category'] = category
                
                response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        if article.get('title') and article.get('description'):
                            articles.append({
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'content': article.get('content', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', {}).get('name', 'NewsAPI'),
                                'published_at': article.get('publishedAt', ''),
                                'category': keyword,
                                'collector': 'newsapi'
                            })
                    
                    logger.info(f"✅ NewsAPI: {len(data.get('articles', []))} articoli per '{keyword}'")
                else:
                    logger.error(f"❌ NewsAPI errore {response.status_code} per '{keyword}'")
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Errore NewsAPI per '{keyword}': {e}")
        
        return articles

    def collect_rss_feeds(self, rss_feeds: List[str], category: str) -> List[Dict[str, Any]]:
        """Raccoglie notizie da feed RSS"""
        articles = []
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limita a 10 per feed
                    articles.append({
                        'title': getattr(entry, 'title', ''),
                        'description': getattr(entry, 'summary', ''),
                        'content': getattr(entry, 'content', [{}])[0].get('value', '') if hasattr(entry, 'content') else '',
                        'url': getattr(entry, 'link', ''),
                        'source': feed.feed.get('title', feed_url),
                        'published_at': getattr(entry, 'published', ''),
                        'category': category,
                        'collector': 'rss'
                    })
                
                logger.info(f"✅ RSS: {len(feed.entries[:10])} articoli da {feed.feed.get('title', feed_url)}")
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Errore RSS {feed_url}: {e}")
        
        return articles

    def collect_cybersecurity_news(self) -> List[Dict[str, Any]]:
        """Raccoglie notizie cybersecurity"""
        cyber_keywords = [
            'cybersecurity', 'cyber attack', 'malware', 'ransomware', 
            'data breach', 'hacking', 'vulnerability', 'zero-day',
            'phishing', 'APT', 'botnet', 'DDoS', 'exploit'
        ]
        
        # NewsAPI
        newsapi_articles = self.collect_news_api(cyber_keywords, 'technology')
        
        # RSS
        rss_articles = self.collect_rss_feeds(self.cyber_rss_feeds, 'cybersecurity')
        
        all_articles = newsapi_articles + rss_articles
        logger.info(f"🔒 Totale cybersecurity: {len(all_articles)} articoli")
        
        return all_articles

    def collect_geopolitical_news(self) -> List[Dict[str, Any]]:
        """Raccoglie notizie geopolitiche"""
        geopolitical_keywords = [
            'geopolitics', 'international relations', 'diplomatic crisis',
            'military conflict', 'sanctions', 'trade war', 'election',
            'terrorism', 'nuclear', 'defense', 'intelligence', 'espionage'
        ]
        
        # NewsAPI
        newsapi_articles = self.collect_news_api(geopolitical_keywords, 'general')
        
        # RSS
        rss_articles = self.collect_rss_feeds(self.geopolitical_rss_feeds, 'geopolitics')
        
        all_articles = newsapi_articles + rss_articles
        logger.info(f"🌍 Totale geopolitica: {len(all_articles)} articoli")
        
        return all_articles

    def collect_all_news(self) -> Dict[str, List[Dict[str, Any]]]:
        """Raccoglie tutte le notizie"""
        logger.info("📡 Iniziando raccolta completa notizie...")
        
        cyber_news = self.collect_cybersecurity_news()
        geo_news = self.collect_geopolitical_news()
        
        logger.info(f"📊 Raccolta completata: {len(cyber_news)} cyber + {len(geo_news)} geo = {len(cyber_news + geo_news)} totali")
        
        return {
            'cybersecurity': cyber_news,
            'geopolitics': geo_news,
            'all': cyber_news + geo_news
        }


def collect_cyber_news(limit=20):
    """Raccoglie notizie cyber"""
    import os
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.error("❌ NEWS_API_KEY non trovata")
        return []
    
    collector = NewsCollector(api_key)
    articles = collector.collect_cybersecurity_news()
    return articles[:limit]

def collect_geo_news(limit=20):
    """Raccoglie notizie geo"""
    import os
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.error("❌ NEWS_API_KEY non trovata")
        return []
    
    collector = NewsCollector(api_key)
    articles = collector.collect_geopolitical_news()
    return articles[:limit]

def collect_cybersecurity_rss(limit=20):
    """Raccoglie notizie cybersecurity da RSS"""
    import os
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.error("❌ NEWS_API_KEY non trovata")
        return []
    
    collector = NewsCollector(api_key)
    articles = collector.collect_cybersecurity_news()
    return articles[:limit]

def collect_geopolitical_rss(limit=20):
    """Raccoglie notizie geopolitiche da RSS"""
    import os
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.error("❌ NEWS_API_KEY non trovata")
        return []
    
    collector = NewsCollector(api_key)
    articles = collector.collect_geopolitical_news()
    return articles[:limit]

def enhanced_correlation_finder(cyber_articles, geo_articles):
    """Trova correlazioni avanzate tra articoli cyber e geopolitici"""
    correlations = []
    
    # Parole chiave per correlazioni
    correlation_keywords = {
        'nation_state': ['china', 'russia', 'iran', 'north korea', 'apt', 'state-sponsored'],
        'critical_infrastructure': ['power grid', 'water', 'transportation', 'healthcare', 'finance'],
        'military': ['military', 'defense', 'army', 'navy', 'air force', 'pentagon'],
        'election': ['election', 'voting', 'democracy', 'campaign', 'ballot'],
        'supply_chain': ['supply chain', 'vendor', 'third party', 'supplier'],
        'energy': ['oil', 'gas', 'energy', 'pipeline', 'nuclear', 'power plant'],
        'financial': ['bank', 'financial', 'payment', 'swift', 'cryptocurrency'],
        'diplomatic': ['embassy', 'diplomat', 'treaty', 'sanctions', 'negotiations']
    }
    
    for cyber_article in cyber_articles:
        for geo_article in geo_articles:
            correlation_score = 0
            correlation_type = []
            
            cyber_text = f"{cyber_article.get('title', '')} {cyber_article.get('description', '')}".lower()
            geo_text = f"{geo_article.get('title', '')} {geo_article.get('description', '')}".lower()
            
            # Analizza correlazioni per categoria
            for category, keywords in correlation_keywords.items():
                cyber_matches = sum(1 for keyword in keywords if keyword in cyber_text)
                geo_matches = sum(1 for keyword in keywords if keyword in geo_text)
                
                if cyber_matches > 0 and geo_matches > 0:
                    correlation_score += (cyber_matches + geo_matches) * 10
                    correlation_type.append(category)
            
            # Controlla entità comuni (paesi, organizzazioni)
            entities = ['china', 'russia', 'usa', 'iran', 'israel', 'ukraine', 'nato', 'eu', 'un']
            common_entities = []
            for entity in entities:
                if entity in cyber_text and entity in geo_text:
                    correlation_score += 15
                    common_entities.append(entity)
            
            # Controlla temporal proximity
            if correlation_score > 0:
                try:
                    cyber_date = datetime.fromisoformat(cyber_article.get('published_at', '').replace('Z', '+00:00'))
                    geo_date = datetime.fromisoformat(geo_article.get('published_at', '').replace('Z', '+00:00'))
                    time_diff = abs((cyber_date - geo_date).days)
                    
                    if time_diff <= 1:
                        correlation_score += 20
                    elif time_diff <= 3:
                        correlation_score += 10
                except:
                    pass
            
            if correlation_score >= 25:  # Soglia per correlazione significativa
                severity = 'HIGH' if correlation_score >= 50 else 'MEDIUM' if correlation_score >= 35 else 'LOW'
                
                correlations.append({
                    'cyber_article': cyber_article,
                    'geo_article': geo_article,
                    'correlation_score': correlation_score,
                    'correlation_type': correlation_type,
                    'common_entities': common_entities,
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                })
    
    # Ordina per score
    correlations.sort(key=lambda x: x['correlation_score'], reverse=True)
    
    logger.info(f"🎯 Trovate {len(correlations)} correlazioni")
    return correlations

# Alias per main.py
collect_cybersecurity_news = collect_cyber_news
collect_geopolitical_news = collect_geo_news