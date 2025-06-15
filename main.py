#!/usr/bin/env python3
"""
Cyber-Geo News Aggregator - Main Application for Railway Deployment
Automated 24/7 monitoring of cybersecurity and geopolitical correlations
"""

import schedule
import time
import os
import json
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cyber_geo_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CyberGeoMonitor:
    def __init__(self):
        """Inizializza il monitor principale"""
        self.last_run = None
        self.total_alerts = 0
        self.setup_directories()
        logger.info("🚀 Cyber-Geo Monitor inizializzato")
    
    def setup_directories(self):
        """Crea directory necessarie"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        os.makedirs('alerts', exist_ok=True)
        logger.info("📁 Directory configurate")
    
    def run_hourly_scan(self):
        """Esegue scansione oraria"""
        logger.info("⏰ Avvio scansione oraria...")
        
        try:
            # Import dei moduli
            from alert_system import run_full_analysis
            from email_system import EmailAlertSystem
            
            # Esegui analisi completa
            alerts, correlations = run_full_analysis()
            
            # Conta alert critici e high
            critical_count = len(alerts['critical'])
            high_count = len(alerts['high'])
            total_count = sum(len(alerts[level]) for level in alerts)
            
            self.total_alerts += total_count
            
            # Log risultati
            logger.info(f"📊 Scansione completata:")
            logger.info(f"   🔴 Critical: {critical_count}")
            logger.info(f"   🟠 High: {high_count}")
            logger.info(f"   📈 Total: {total_count}")
            logger.info(f"   🔍 Correlations: {len(correlations)}")
            
            # Salva in directory organizzate
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Sposta file nella directory alerts
            alert_file = f"alerts_{timestamp}.json"
            if os.path.exists(alert_file):
                os.rename(alert_file, f"alerts/{alert_file}")
            
            # Crea summary per Railway logs
            summary = {
                'timestamp': timestamp,
                'critical_alerts': critical_count,
                'high_alerts': high_count,
                'total_alerts': total_count,
                'correlations': len(correlations),
                'status': 'completed'
            }
            
            with open(f'data/summary_{timestamp}.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Alert immediati per threat critici
            if critical_count > 0:
                logger.warning(f"🚨 {critical_count} CRITICAL THREATS DETECTED!")
                self.send_immediate_notification(alerts['critical'])
            elif high_count > 0:
                logger.warning(f"⚠️ {high_count} HIGH PRIORITY THREATS DETECTED!")
            
            self.last_run = datetime.now()
            logger.info("✅ Scansione oraria completata con successo")
            
        except Exception as e:
            logger.error(f"❌ Errore durante scansione: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def send_immediate_notification(self, critical_alerts):
        """Invia notifica immediata per alert critici"""
        logger.info("📧 Preparando notifica immediata...")
        
        # Per ora log dettagliato - email configurabile dopo
        for alert in critical_alerts[:3]:  # Top 3
            logger.critical(f"🚨 CRITICAL: {alert['cyber_title']}")
            logger.critical(f"🌍 LINKED TO: {alert['geo_title']}")
            logger.critical(f"🎯 THREAT LEVEL: {alert['threat_level']}")
    
    def run_weekly_report(self):
        """Genera report settimanale"""
        logger.info("📊 Generando report settimanale...")
        
        try:
            from email_system import create_weekly_report
            report_html = create_weekly_report()
            
            # Sposta nella directory reports
            timestamp = datetime.now().strftime('%Y%m%d')
            report_file = f"weekly_report_{timestamp}.html"
            if os.path.exists(report_file):
                os.rename(report_file, f"reports/{report_file}")
            
            logger.info(f"📄 Report settimanale generato: reports/{report_file}")
            
        except Exception as e:
            logger.error(f"❌ Errore report settimanale: {e}")
    
    def get_system_status(self):
        """Ritorna status del sistema"""
        return {
            'status': 'running',
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'total_alerts_processed': self.total_alerts,
            'uptime_hours': self.get_uptime_hours()
        }
    
    def get_uptime_hours(self):
        """Calcola ore di uptime"""
        if self.last_run:
            return (datetime.now() - self.last_run).total_seconds() / 3600
        return 0
    
    def run_continuous_monitoring(self):
        """Avvia monitoraggio continuo"""
        logger.info("🚀 Avvio monitoraggio continuo...")
        
        # Configura schedule
        schedule.every().hour.do(self.run_hourly_scan)
        schedule.every().sunday.at("09:00").do(self.run_weekly_report)
        
        # Primo run immediato
        logger.info("⚡ Eseguendo prima scansione...")
        self.run_hourly_scan()
        
        # Loop principale
        logger.info("⏰ Sistema in monitoraggio continuo...")
        logger.info("📋 Schedule configurato:")
        logger.info("   • Scansione oraria per alert")
        logger.info("   • Report settimanale domenica 09:00")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check ogni minuto
                
                # Log status ogni 6 ore
                if datetime.now().minute == 0 and datetime.now().hour % 6 == 0:
                    status = self.get_system_status()
                    logger.info(f"📊 System Status: {status}")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Monitoraggio fermato manualmente")
        except Exception as e:
            logger.error(f"💥 Errore critico nel monitoraggio: {e}")
            # Restart automatico
            logger.info("🔄 Tentativo restart automatico in 5 minuti...")
            time.sleep(300)
            self.run_continuous_monitoring()

def health_check():
    """Health check per Railway"""
    try:
        # Test import moduli
        from config import NEWS_API_KEY
        from news_collector import collect_cybersecurity_news, collect_geopolitical_news
        
        # Test API key
        if not NEWS_API_KEY or NEWS_API_KEY == "your_newsapi_key_here":
            return False, "API Key non configurata"
        
        return True, "Sistema operativo"
        
    except Exception as e:
        return False, f"Errore: {e}"

def main():
    """Funzione principale"""
    logger.info("🚀 Avvio Cyber-Geo News Aggregator")
    logger.info("=" * 50)
    
    # Health check
    healthy, message = health_check()
    if not healthy:
        logger.error(f"❌ Health check fallito: {message}")
        return
    
    logger.info(f"✅ Health check: {message}")
    
    # Avvia monitor
    monitor = CyberGeoMonitor()
    monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()