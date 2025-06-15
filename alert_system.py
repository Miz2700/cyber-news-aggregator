import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class CyberGeoAlertSystem:
    def __init__(self):
        """Inizializza il sistema di alert"""
        self.alert_thresholds = {
            'critical': 7,    # Score >= 7 = CRITICO
            'high': 5,        # Score >= 5 = ALTO
            'medium': 3,      # Score >= 3 = MEDIO
            'low': 1          # Score >= 1 = BASSO
        }
        
        self.critical_keywords = [
            'apt', 'nation-state', 'zero-day', 'critical infrastructure',
            'government', 'military', 'war', 'sanctions'
        ]
    
    def analyze_correlations(self, correlations):
        """Analizza le correlazioni e genera alert"""
        
        alerts = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for corr in correlations:
            score = corr['connection_score']
            
            # Determina il livello di alert
            if score >= self.alert_thresholds['critical']:
                level = 'critical'
            elif score >= self.alert_thresholds['high']:
                level = 'high'
            elif score >= self.alert_thresholds['medium']:
                level = 'medium'
            else:
                level = 'low'
            
            # Crea alert strutturato
            alert = {
                'level': level,
                'score': score,
                'timestamp': datetime.now().isoformat(),
                'cyber_title': corr['cyber_article']['title'],
                'geo_title': corr['geo_article']['title'],
                'analysis': corr['analysis'],
                'patterns': corr['matched_patterns'],
                'cyber_url': corr['cyber_article'].get('url', ''),
                'geo_url': corr['geo_article'].get('url', ''),
                'threat_level': self.assess_threat_level(corr)
            }
            
            alerts[level].append(alert)
        
        return alerts
    
    def assess_threat_level(self, correlation):
        """Valuta il livello di minaccia"""
        
        text = (correlation['cyber_article']['title'] + ' ' + 
                correlation['geo_article']['title'] + ' ' +
                ' '.join(correlation['matched_patterns'])).lower()
        
        threat_indicators = {
            'nation_state': any(word in text for word in ['apt', 'nation-state', 'state-sponsored']),
            'critical_infra': any(word in text for word in ['infrastructure', 'power', 'election', 'government']),
            'active_conflict': any(word in text for word in ['war', 'military', 'conflict', 'sanctions']),
            'zero_day': 'zero-day' in text,
            'widespread': any(word in text for word in ['widespread', 'global', 'multiple'])
        }
        
        threat_score = sum(threat_indicators.values())
        
        if threat_score >= 3:
            return "EXTREME"
        elif threat_score >= 2:
            return "HIGH"
        elif threat_score >= 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_alert_report(self, alerts):
        """Genera un report completo degli alert"""
        
        report = []
        report.append("🚨 CYBER-GEO INTELLIGENCE ALERT REPORT")
        report.append("=" * 50)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Statistiche
        total_alerts = sum(len(alerts[level]) for level in alerts)
        report.append("📊 ALERT SUMMARY:")
        report.append(f"🔴 Critical: {len(alerts['critical'])}")
        report.append(f"🟠 High: {len(alerts['high'])}")
        report.append(f"🟡 Medium: {len(alerts['medium'])}")
        report.append(f"🟢 Low: {len(alerts['low'])}")
        report.append(f"📈 Total: {total_alerts}")
        report.append("")
        
        # Alert critici
        if alerts['critical']:
            report.append("🔴 CRITICAL ALERTS:")
            report.append("-" * 30)
            for i, alert in enumerate(alerts['critical'][:5]):  # Top 5
                report.append(f"\n{i+1}. THREAT LEVEL: {alert['threat_level']} (Score: {alert['score']})")
                report.append(f"   🔒 CYBER: {alert['cyber_title']}")
                report.append(f"   🌍 GEO:   {alert['geo_title']}")
                report.append(f"   🔍 ANALYSIS: {alert['analysis']}")
                report.append(f"   ⏰ TIME: {alert['timestamp'][:19]}")
                if alert['cyber_url']:
                    report.append(f"   🔗 CYBER SOURCE: {alert['cyber_url']}")
                if alert['geo_url']:
                    report.append(f"   🔗 GEO SOURCE: {alert['geo_url']}")
        
        # Alert high
        if alerts['high']:
            report.append(f"\n🟠 HIGH PRIORITY ALERTS ({len(alerts['high'])}):")
            report.append("-" * 30)
            for i, alert in enumerate(alerts['high'][:3]):  # Top 3
                report.append(f"\n{i+1}. {alert['cyber_title'][:60]}...")
                report.append(f"   ↔️ {alert['geo_title'][:60]}...")
                report.append(f"   📊 Score: {alert['score']} | Threat: {alert['threat_level']}")
        
        report.append(f"\n📁 Full data saved in timestamped JSON files")
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def save_alerts(self, alerts):
        """Salva gli alert in file JSON"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'alerts_{timestamp}.json'
        
        alert_data = {
            'timestamp': timestamp,
            'summary': {
                'critical': len(alerts['critical']),
                'high': len(alerts['high']),
                'medium': len(alerts['medium']),
                'low': len(alerts['low'])
            },
            'alerts': alerts
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Alert salvati: {filename}")
        return filename
    
    def print_immediate_alerts(self, alerts):
        """Stampa alert immediati nella console"""
        
        print("\n" + "🚨" * 20)
        print("  IMMEDIATE THREAT ALERTS")
        print("🚨" * 20)
        
        # Alert critici - IMMEDIATI
        if alerts['critical']:
            print(f"\n🔴 {len(alerts['critical'])} CRITICAL ALERTS DETECTED!")
            for alert in alerts['critical']:
                print(f"\n⚡ THREAT LEVEL: {alert['threat_level']}")
                print(f"📊 Score: {alert['score']}")
                print(f"🔒 {alert['cyber_title']}")
                print(f"🌍 {alert['geo_title']}")
                print(f"🔍 {alert['analysis']}")
                print("-" * 40)
        
        # Alert high
        if alerts['high']:
            print(f"\n🟠 {len(alerts['high'])} HIGH PRIORITY ALERTS")
            for alert in alerts['high'][:2]:  # Solo i primi 2
                print(f"📊 Score {alert['score']}: {alert['analysis']}")
        
        if not alerts['critical'] and not alerts['high']:
            print("✅ No immediate threats detected")
        
        print("🚨" * 20 + "\n")

def run_full_analysis():
    """Esegue analisi completa con alert"""
    
    print("🚀 AVVIO SISTEMA ALERT CYBER-GEO")
    print("=" * 40)
    
    # Importa i collector
    from news_collector import collect_cyber_news, collect_geopolitical_news, find_correlations
    from news_collector import collect_cybersecurity_rss, collect_geopolitical_rss, enhanced_correlation_finder
    from config import NEWS_API_KEY
    
    alert_system = CyberGeoAlertSystem()
    
    # Raccolta dati da tutte le fonti
    print("📡 Raccogliendo da NewsAPI...")
    newsapi_cyber = collect_cyber_news(NEWS_API_KEY)
    newsapi_geo = collect_geopolitical_news(NEWS_API_KEY)
    
    print("📡 Raccogliendo da RSS...")
    rss_cyber = collect_cybersecurity_rss()
    rss_geo = collect_geopolitical_rss()
    
    # Combina tutte le fonti
    all_cyber = newsapi_cyber + rss_cyber
    all_geo = newsapi_geo + rss_geo
    
    print(f"📊 TOTALE: {len(all_cyber)} cyber + {len(all_geo)} geo articles")
    
    # Analisi correlazioni
    correlations = enhanced_correlation_finder(all_cyber, all_geo)
    
    # Genera alert
    alerts = alert_system.analyze_correlations(correlations)
    
    # Alert immediati
    alert_system.print_immediate_alerts(alerts)
    
    # Report completo
    report = alert_system.generate_alert_report(alerts)
    print(report)
    
    # Salva tutto
    alert_system.save_alerts(alerts)
    
    return alerts, correlations

if __name__ == "__main__":
    alerts, correlations = run_full_analysis()