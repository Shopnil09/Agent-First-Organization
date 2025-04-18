import os
import sqlite3
import logging
from langchain_openai import ChatOpenAI

from arklex.utils.model_config import MODEL

DBNAME = 'formula1_db.sqlite'

logger = logging.getLogger(__name__)

SLOTS = {
    "name": {
        "name": "name",
        "type": "string",
        "value": "",
        "description": "Name of the race, driver, or team",
        "prompt": "Please provide the name you are looking for"
    },
    "season": {
        "name": "season",
        "type": "integer",
        "value": "",
        "description": "Season year (e.g. 2024)",
        "prompt": "Please provide the season year"
    }
}

LOG_IN_FAILURE = "Failed to login. Please ensure the Formula 1 database exists in your DATA_DIR."
NO_RESULT_MESSAGE = "No results found. Please check your search criteria."

class Formula1Context:
    db_path = None
    llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)

f1 = Formula1Context()

def log_in():
    f1.db_path = os.path.join(os.environ.get("DATA_DIR"), DBNAME)
    if not os.path.exists(f1.db_path):
        logger.error("Database not found at: %s", f1.db_path)
        return False
    return True
