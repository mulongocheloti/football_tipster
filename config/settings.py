import os, warnings
from dotenv import load_dotenv

# Only ignore the exact warning message
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable.*",
    category=UserWarning
)

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

BASE_URL = "https://api.football-data.org/v4"
DATABASE_URL = os.getenv("DATABASE_URL") 
# api token moved to github secrets

SEASONS = [
            2025,  # 2025-2026
            #2024 # data already fetched and will never change
            #2023, # data already fetched and will never change
            #<= 2022 # data not available with free tier
            # standard tier ($49) - added Europa,  FA Cup, DFB-Pokal, MLS, Fifa Club WC, No(C. Italia, CopaDelRey)
]

COMPETITIONS = [
    "PL",   # Premier League, England
    "CL",   # Champions League, Europe -- data available only for current season because competition structural change and complexity (league-knockouts)
    "BL1",  # Bundesliga, Germany
    "PD",   # La Liga, Spain
    "SA",   # Serie A, Brazil
    "FL1",  # Ligue 1, France
    "DED",  # Eredivisie, Netherlands
    "PPL",  # Primeira Liga, Portugal
    "ELC"  # Championship, England
    #"WC" World cup left out, unique group standings, knockout structure, is in the next season
]

DB = {
    "host": "localhost",
    "database": "football_tipster",
    "user": "admin",
    "password": "mulongo1999",
    "port": 5432
}

MAX_CALLS_PER_MINUTE = 9