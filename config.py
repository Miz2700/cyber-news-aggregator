NEWS_API_KEY = "d8ff546e474640e59b6bf752ce381052"
REDDIT_CLIENT_ID = " JGxRXZlv9ddjbEhbgEb5DA "
REDDIT_CLIENT_SECRET = "1AcqxPEFZbfP33fDWd7epNzTVSqhmA "

# OpenAI API Key (for AI analysis - get free tier)
OPENAI_API_KEY = "your_openai_key_here"

# Keywords to watch for cybersecurity news
CYBER_KEYWORDS = [
    "ransomware", "cyberattack", "data breach", "malware", 
    "phishing", "ddos", "vulnerability", "exploit",
    "zero-day", "apt", "botnet", "trojan", "backdoor",
    "cybersecurity", "information security", "cyber warfare"
]

# Keywords for geopolitical connections
GEOPOLITICAL_KEYWORDS = [
    "sanctions", "conflict", "diplomatic", "military", 
    "intelligence", "nation-state", "government",
    "international relations", "warfare", "espionage",
    "state-sponsored", "political tension"
]

# Countries/regions to track for connections
REGIONS = [
    "Russia", "China", "Iran", "North Korea", "Ukraine", 
    "Taiwan", "Israel", "Palestine", "Europe", "NATO",
    "United States", "South Korea", "Japan", "India",
    "Germany", "France", "United Kingdom", "Turkey"
]

# Priority threat actors to monitor
THREAT_ACTORS = [
    "APT1", "APT28", "APT29", "Lazarus", "Cozy Bear",
    "Fancy Bear", "Equation Group", "Shadow Brokers",
    "Carbanak", "FIN7", "Sandworm", "Turla"
]

# News sources configuration
NEWS_SOURCES = [
    "reuters.com", "bbc.com", "cnn.com", "bloomberg.com",
    "techcrunch.com", "wired.com", "zdnet.com", "arstechnica.com",
    "krebsonsecurity.com", "darkreading.com", "securityweek.com"
]

# Reddit subreddits to monitor
REDDIT_SUBREDDITS = [
    "cybersecurity", "netsec", "security", "malware",
    "worldnews", "geopolitics", "intelligence", "privacy"
]

# Analysis settings
MIN_CORRELATION_SCORE = 0.7  # Minimum score to flag as connected
UPDATE_FREQUENCY_MINUTES = 60  # How often to check for new news
ALERT_KEYWORDS = ["critical", "zero-day", "nation-state", "emergency"]

# Email settings (you'll configure these later)
EMAIL_ALERTS_ENABLED = False
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECIPIENT_EMAIL = "your_email@gmail.com"

# Database settings (using simple JSON for now)
DATA_STORAGE_PATH = "data/"
ARTICLES_FILE = "articles.json"
CORRELATIONS_FILE = "correlations.json"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "cyber_news.log"
