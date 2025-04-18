from ..tools import register_tool
from .f1_utils import *
import pandas as pd
import sqlite3

@register_tool(
    "Searches the Formula 1 database for teams",
    [{**SLOTS['name'], 'required': False}],
    [{
        "name": "query_result",
        "type": "str",
        "description": "List of matching teams"
    }],
    lambda x: x not in (LOG_IN_FAILURE or NO_RESULT_MESSAGE)
)
def search_team(name=None) -> str | None:
    if not log_in(): return LOG_IN_FAILURE

    conn = sqlite3.connect(f1.db_path)
    cursor = conn.cursor()
    query = "SELECT name, base_country, principal_name FROM team WHERE 1 = 1"
    params = []
    if name:
        query += " AND name = ?"
        params.append(name)
    query += " LIMIT 10"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    column_names = [col[0] for col in cursor.description]  # 🔑 move this before close
    cursor.close()
    conn.close()

    if not rows:
        return NO_RESULT_MESSAGE

    results = [dict(zip(column_names, row)) for row in rows]
    return "Matching teams:\n" + pd.DataFrame(results).to_string(index=False)
