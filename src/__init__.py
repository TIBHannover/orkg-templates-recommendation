import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODELS_DIR = os.path.join(CURRENT_DIR, '..', 'models')
DATA_DIR = os.path.join(CURRENT_DIR, '..', 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
TRIPLE_STORE_URL = "https://orkg.org/triplestore"
