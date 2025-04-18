from ..tools import register_tool
from .f1_utils import *
import pandas as pd
import sqlite3

@register_tool(
    "Searches the Formula 1 database for drivers",
    [
        {"name": "first_name", "type": "string", "required": False, "description": "First name of the driver"},
        {"name": "last_name", "type": "string", "required": False, "description": "Last name of the driver"}
    ],
    [{
        "name": "query_result",
        "type": "str",
        "description": "A list of matching F1 drivers or 'No results found.'"
    }],
    lambda x: x not in (LOG_IN_FAILURE or NO_RESULT_MESSAGE)
)
def search_driver(first_name=None, last_name=None) -> str | None:
    if not log_in(): return LOG_IN_FAILURE

    conn = sqlite3.connect(f1.db_path)
    cursor = conn.cursor()
    query = "SELECT first_name, last_name, nationality, date_of_birth FROM driver WHERE 1 = 1"
    params = []
    if first_name:
        query += " AND first_name = ?"
        params.append(first_name)
    if last_name:
        query += " AND last_name = ?"
        params.append(last_name)
    query += " LIMIT 10"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = NO_RESULT_MESSAGE
    if rows:
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        result = "Matching drivers:\n" + pd.DataFrame(results).to_string(index=False)
    cursor.close()
    conn.close()
    return result
