import requests
import time
from datetime import datetime
import json

def collect_cyber_news(api_key):
    """Raccoglie notizie di cybersecurity da NewsAPI"""
    
    print("🔍 Raccogliendo notizie di tecnologia...")
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'category': 'technology',
        'apiKey': api_key,
        'pageSize': 100,  # Massimo disponibile
        'country': 'us'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filtra per cybersecurity keywords
            cyber_keywords = [
                'cyber', 'hack', 'breach', 'malware', 'security', 'attack', 
                'ransomware', 'phishing', 'password', 'vulnerability', 'data',
                'privacy', 'encryption', 'threat', 'virus', 'exploit'
            ]
            
            cyber_articles = []
            
            for article in data['articles']:
                # Controlla titolo e descrizione
                text_to_check = (article['title'] + ' ' + (article['description'] or '')).lower()
                
                if any(keyword in text_to_check for keyword in cyber_keywords):
                    article['cyber_score'] = sum(1 for keyword in cyber_keywords if keyword in text_to_check)
                    cyber_articles.append(article)
            
            # Ordina per rilevanza cybersecurity
            cyber_articles.sort(key=lambda x: x['cyber_score'], reverse=True)
            
            print(f"✅ Trovate {len(cyber_articles)} notizie cyber da {data['totalResults']} totali tech")
            return cyber_articles
            
        else:
            print(f"❌ Errore API: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []

def collect_geopolitical_news(api_key):
    """Raccoglie notizie geopolitiche"""
    
    print("🌍 Raccogliendo notizie generali...")
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'category': 'general',
        'apiKey': api_key,
        'pageSize': 100,
        'country': 'us'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filtra per geopolitical keywords
            geo_keywords = [
                'war', 'conflict', 'military', 'diplomatic', 'sanctions', 
                'international', 'government', 'political', 'intelligence',
                'nation', 'treaty', 'embassy', 'foreign', 'minister',
                'president', 'prime', 'defense', 'security council'
            ]
            
            geo_articles = []
            
            for article in data['articles']:
                text_to_check = (article['title'] + ' ' + (article['description'] or '')).lower()
                
                if any(keyword in text_to_check for keyword in geo_keywords):
                    article['geo_score'] = sum(1 for keyword in geo_keywords if keyword in text_to_check)
                    geo_articles.append(article)
            
            # Ordina per rilevanza geopolitica
            geo_articles.sort(key=lambda x: x['geo_score'], reverse=True)
            
            print(f"✅ Trovate {len(geo_articles)} notizie geopolitiche da {data['totalResults']} totali")
            return geo_articles
            
        else:
            print(f"❌ Errore API geo: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"❌ Errore geo: {e}")
        return []

def find_correlations(cyber_articles, geo_articles):
    """Trova correlazioni tra cyber e geo notizie"""
    
    print("🔍 Cercando correlazioni...")
    
    correlations = []
    
    # Keywords che indicano connessioni
    connection_keywords = [
        'russia', 'china', 'iran', 'north korea', 'ukraine',
        'nation-state', 'government', 'state-sponsored', 'apt',
        'military', 'intelligence', 'warfare'
    ]
    
    for cyber in cyber_articles:
        cyber_text = (cyber['title'] + ' ' + (cyber['description'] or '')).lower()
        
        for geo in geo_articles:
            geo_text = (geo['title'] + ' ' + (geo['description'] or '')).lower()
            
            # Cerca keywords comuni
            common_keywords = []
            for keyword in connection_keywords:
                if keyword in cyber_text and keyword in geo_text:
                    common_keywords.append(keyword)
            
            if common_keywords:
                correlation = {
                    'cyber_article': cyber,
                    'geo_article': geo,
                    'common_keywords': common_keywords,
                    'connection_score': len(common_keywords)
                }
                correlations.append(correlation)
    
    # Ordina per rilevanza
    correlations.sort(key=lambda x: x['connection_score'], reverse=True)
    
    print(f"🎯 Trovate {len(correlations)} possibili correlazioni")
    return correlations

def save_data(cyber_articles, geo_articles, correlations):
    """Salva tutti i dati"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Salva articoli cyber
    with open(f'cyber_news_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(cyber_articles, f, indent=2, ensure_ascii=False)
    
    # Salva articoli geo
    with open(f'geo_news_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(geo_articles, f, indent=2, ensure_ascii=False)
    
    # Salva correlazioni
    with open(f'correlations_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(correlations, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dati salvati con timestamp: {timestamp}")

def display_results(cyber_articles, geo_articles, correlations):
    """Mostra i risultati principali"""
    
    print("\n" + "="*60)
    print("📊 RISULTATI AGGREGAZIONE CYBER-GEO NEWS")
    print("="*60)
    
    # Top cyber news
    print(f"\n🔒 TOP {min(3, len(cyber_articles))} NOTIZIE CYBERSECURITY:")
    for i, article in enumerate(cyber_articles[:3]):
        print(f"\n{i+1}. {article['title']}")
        print(f"   📅 {article['publishedAt']}")
        print(f"   🔗 {article['source']['name']}")
        print(f"   🎯 Score: {article.get('cyber_score', 0)}")
    
    # Top geo news
    print(f"\n🌍 TOP {min(3, len(geo_articles))} NOTIZIE GEOPOLITICHE:")
    for i, article in enumerate(geo_articles[:3]):
        print(f"\n{i+1}. {article['title']}")
        print(f"   📅 {article['publishedAt']}")
        print(f"   🔗 {article['source']['name']}")
        print(f"   🎯 Score: {article.get('geo_score', 0)}")
    
    # Correlazioni
    if correlations:
        print(f"\n🎯 TOP {min(2, len(correlations))} CORRELAZIONI TROVATE:")
        for i, corr in enumerate(correlations[:2]):
            print(f"\n{i+1}. CONNESSIONE (Score: {corr['connection_score']}):")
            print(f"   🔒 Cyber: {corr['cyber_article']['title'][:60]}...")
            print(f"   🌍 Geo:   {corr['geo_article']['title'][:60]}...")
            print(f"   🔗 Keywords comuni: {', '.join(corr['common_keywords'])}")
    else:
        print("\n🎯 Nessuna correlazione diretta trovata oggi")

# Main execution
if __name__ == "__main__":
    print("🚀 CYBER-GEO NEWS AGGREGATOR")
    print("="*40)
    
    try:
        from config import NEWS_API_KEY
        
        # Raccolta dati
        cyber_articles = collect_cyber_news(NEWS_API_KEY)
        time.sleep(1)  # Pausa per evitare rate limiting
        geo_articles = collect_geopolitical_news(NEWS_API_KEY)
        
        # Analisi correlazioni
        correlations = find_correlations(cyber_articles, geo_articles)
        
        # Salvataggio
        save_data(cyber_articles, geo_articles, correlations)
        
        # Visualizzazione risultati
        display_results(cyber_articles, geo_articles, correlations)
        
        print(f"\n✅ COMPLETATO! Analizzate {len(cyber_articles)} cyber + {len(geo_articles)} geo notizie")
        print(f"📁 File salvati con timestamp per riferimento futuro")
        
    except Exception as e:
        print(f"❌ Errore generale: {e}")
        import traceback
        traceback.print_exc()
    
        