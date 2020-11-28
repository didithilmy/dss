import os
from dotenv import load_dotenv
load_dotenv()

MODEL_META_FILENAME = "model.yml"
MODELS_PATH = os.getenv('MODELS_PATH')
DATA_TMP_PATH = os.getenv('DATA_TMP_PATH')