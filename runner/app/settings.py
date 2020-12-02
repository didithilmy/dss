import os
from dotenv import load_dotenv
load_dotenv()

MBMS_URL = os.getenv('MBMS_URL')
DB_URL = os.getenv('DB_URL')