import logging
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import requests

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CyberGeoAlertSystem:
    def __init__(self):
        # Configurazione Telegram
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Soglie alert
        self.high_severity_threshold = 70
        self.medium_severity_threshold = 40
        
        logger.info("🚨 Alert System inizializzato")

    def analyze_correlations(self, correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analizza le correlazioni e genera alert"""
        alerts = []
        
        for corr in correlations:
            # Fix: usa correlation_score invece di connection_score
            score = corr.get('correlation_score', 0)
            severity = corr.get('severity', 'LOW')
            correlation_type = corr.get('correlation_type', [])
            common_entities = corr.get('common_entities', [])
            
            # Determina il livello di alert
            if score >= self.high_severity_threshold:
                alert_level = 'CRITICAL'
                priority = 1
            elif score >= self.medium_severity_threshold:
                alert_level = 'HIGH'
                priority = 2
            elif score >= 25:
                alert_level = 'MEDIUM'
                priority = 3
            else:
                alert_level = 'LOW'
                priority = 4
            
            # Genera descrizione alert
            cyber_title = corr.get('cyber_article', {}).get('title', 'N/A')
            geo_title = corr.get('geo_article', {}).get('title', 'N/A')
            
            description = self._generate_alert_description(
                cyber_title, geo_title, correlation_type, common_entities, score
            )
            
            alert = {
                'id': f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(alerts)}",
                'timestamp': datetime.now().isoformat(),
                'level': alert_level,
                'priority': priority,
                'score': score,
                'severity': severity,
                'description': description,
                'correlation_type': correlation_type,
                'common_entities': common_entities,
                'cyber_article': corr.get('cyber_article', {}),
                'geo_article': corr.get('geo_article', {}),
                'correlation_data': corr
            }
            
            alerts.append(alert)
        
        # Ordina per priorità
        alerts.sort(key=lambda x: (x['priority'], -x['score']))
        
        logger.info(f"🚨 Generati {len(alerts)} alert da {len(correlations)} correlazioni")
        return alerts

    def _generate_alert_description(self, cyber_title: str, geo_title: str, 
                                   correlation_type: List[str], common_entities: List[str], 
                                   score: int) -> str:
        """Genera descrizione dell'alert"""
        
        entities_str = ", ".join(common_entities) if common_entities else "Nessuna"
        types_str = ", ".join(correlation_type) if correlation_type else "Generica"
        
        description = f"""
🔗 CORRELAZIONE CYBER-GEOPOLITICA RILEVATA (Score: {score})

🔒 CYBER: {cyber_title[:100]}...
🌍 GEO: {geo_title[:100]}...

📊 DETTAGLI:
• Tipo correlazione: {types_str}
• Entità comuni: {entities_str}
• Score di correlazione: {score}/100

⚠️ POSSIBILI IMPLICAZIONI:
• Potenziale connessione tra eventi cyber e geopolitici
• Necessità di monitoraggio approfondito
• Valutazione impatto sicurezza nazionale
"""
        return description.strip()

    def send_telegram_alert(self, alert: Dict[str, Any]) -> bool:
        """Invia alert via Telegram"""
        try:
            if not all([self.telegram_bot_token, self.telegram_chat_id]):
                logger.warning("⚠️ Configurazione Telegram incompleta")
                return False
            
            # Formatta messaggio per Telegram
            emoji_map = {
                'CRITICAL': '🔴',
                'HIGH': '🟠', 
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            emoji = emoji_map.get(alert['level'], '⚪')
            
            message = f"""
{emoji} *CYBER-GEO ALERT {alert['level']}*

🔍 *Score:* {alert['score']}/100
⏰ *Timestamp:* {alert['timestamp'][:19]}

🔒 *Cyber:* {alert['cyber_article'].get('title', 'N/A')[:80]}...
🌍 *Geo:* {alert['geo_article'].get('title', 'N/A')[:80]}...

🏷️ *Tipo:* {', '.join(alert['correlation_type'])}
🌐 *Entità:* {', '.join(alert['common_entities'])}

#CyberGeoAlert #{alert['level']}
"""
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram alert inviato: {alert['id']}")
                return True
            else:
                logger.error(f"❌ Errore Telegram: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore invio Telegram: {e}")
            return False

    def process_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa e invia tutti gli alert"""
        results = {
            'total_alerts': len(alerts),
            'sent_telegram': 0,
            'failed': 0,
            'by_level': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        
        for alert in alerts:
            # Conta per livello
            results['by_level'][alert['level']] += 1
            
            # Invia solo alert HIGH e CRITICAL per evitare spam
            if alert['level'] in ['CRITICAL', 'HIGH']:
                telegram_sent = self.send_telegram_alert(alert)
                
                if telegram_sent:
                    results['sent_telegram'] += 1
                else:
                    results['failed'] += 1
            
            # Log alert per MEDIUM e LOW
            elif alert['level'] in ['MEDIUM', 'LOW']:
                logger.info(f"📝 Alert {alert['level']}: {alert['id']} (Score: {alert['score']})")
        
        return results

    def generate_summary_report(self, alerts: List[Dict[str, Any]], 
                               correlations: List[Dict[str, Any]]) -> str:
        """Genera report riassuntivo"""
        
        now = datetime.now()
        
        # Statistiche alert
        alert_stats = {
            'CRITICAL': len([a for a in alerts if a['level'] == 'CRITICAL']),
            'HIGH': len([a for a in alerts if a['level'] == 'HIGH']),
            'MEDIUM': len([a for a in alerts if a['level'] == 'MEDIUM']),
            'LOW': len([a for a in alerts if a['level'] == 'LOW'])
        }
        
        # Top correlation types
        all_types = []
        for corr in correlations:
            all_types.extend(corr.get('correlation_type', []))
        
        type_counts = {}
        for t in all_types:
            type_counts[t] = type_counts.get(t, 0) + 1
        
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Top entities
        all_entities = []
        for corr in correlations:
            all_entities.extend(corr.get('common_entities', []))
        
        entity_counts = {}
        for e in all_entities:
            entity_counts[e] = entity_counts.get(e, 0) + 1
        
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report = f"""
🚨 CYBER-GEO INTELLIGENCE REPORT
📅 Data: {now.strftime('%Y-%m-%d %H:%M:%S')}
========================================

📊 STATISTICHE ALERT:
• CRITICAL: {alert_stats['CRITICAL']}
• HIGH: {alert_stats['HIGH']} 
• MEDIUM: {alert_stats['MEDIUM']}
• LOW: {alert_stats['LOW']}
• TOTALE: {len(alerts)}

🔗 CORRELAZIONI TROVATE: {len(correlations)}

🏷️ TOP TIPI CORRELAZIONE:
"""
        
        for tipo, count in top_types:
            report += f"• {tipo}: {count}\n"
        
        report += f"\n🌐 TOP ENTITÀ COINVOLTE:\n"
        for entity, count in top_entities:
            report += f"• {entity.upper()}: {count}\n"
        
        if alert_stats['CRITICAL'] > 0:
            report += f"\n🔴 ATTENZIONE: {alert_stats['CRITICAL']} alert CRITICI rilevati!"
        
        if alert_stats['HIGH'] > 0:
            report += f"\n🟠 {alert_stats['HIGH']} alert HIGH priorità"
        
        report += f"\n\n⏰ Prossima scansione: {(now + timedelta(hours=1)).strftime('%H:%M')}"
        report += f"\n📋 Sistema: OPERATIVO 24/7"
        
        return report


def run_full_analysis():
    """Esegue analisi completa e genera alert"""
    logger.info("🔍 Iniziando analisi completa...")
    
    try:
        # Import qui per evitare import circolari
        from news_collector import collect_cybersecurity_news, collect_geopolitical_news, enhanced_correlation_finder
        
        logger.info("📡 Raccogliendo notizie cyber...")
        cyber_articles = collect_cybersecurity_news(limit=50)
        
        logger.info("🌍 Raccogliendo notizie geopolitiche...")
        geo_articles = collect_geopolitical_news(limit=50)
        
        logger.info(f"TOTALE: {len(cyber_articles)} cyber + {len(geo_articles)} geo articles")
        
        if not cyber_articles and not geo_articles:
            logger.warning("⚠️ Nessun articolo raccolto")
            return [], []
        
        logger.info("🔗 Cercando correlazioni...")
        correlations = enhanced_correlation_finder(cyber_articles, geo_articles)
        
        if not correlations:
            logger.info("ℹ️ Nessuna correlazione significativa trovata")
            return [], []
        
        logger.info("🚨 Generando alert...")
        alert_system = CyberGeoAlertSystem()
        alerts = alert_system.analyze_correlations(correlations)
        
        # Processa alert
        if alerts:
            results = alert_system.process_alerts(alerts)
            logger.info(f"📤 Alert processati: {results}")
            
            # Genera report
            report = alert_system.generate_summary_report(alerts, correlations)
            logger.info(f"📋 Report generato:\n{report}")
        
        return alerts, correlations
        
    except Exception as e:
        logger.error(f"❌ Errore durante analisi: {e}")
        return [], []


def test_alert_system():
    """Test del sistema alert"""
    logger.info("🧪 Testing Alert System...")
    
    # Alert di test
    test_alert = {
        'id': 'TEST_001',
        'timestamp': datetime.now().isoformat(),
        'level': 'HIGH',
        'priority': 2,
        'score': 75,
        'severity': 'HIGH',
        'description': '🧪 TEST ALERT - Sistema operativo',
        'correlation_type': ['test'],
        'common_entities': ['test_entity'],
        'cyber_article': {'title': 'Test Cyber Article'},
        'geo_article': {'title': 'Test Geo Article'}
    }
    
    alert_system = CyberGeoAlertSystem()
    
    # Test Telegram
    telegram_result = alert_system.send_telegram_alert(test_alert)
    
    logger.info(f"🧪 Test completato - Telegram: {telegram_result}")
    
    return telegram_result


if __name__ == "__main__":
    # Test del sistema
    test_alert_system()