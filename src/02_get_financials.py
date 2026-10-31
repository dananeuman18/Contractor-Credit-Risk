import requests
import pandas as pd
from config.py import SEC_USER_AGENT, DB_URL
from sqlalchemy import create_engine

HEADERS = {"User-Agent": SEC_USER_AGENT}
engine = create_engine(DB_URL)

companies = pd.read_sql("SELECT *, FROM companie", engine)
print(companies.shape)

