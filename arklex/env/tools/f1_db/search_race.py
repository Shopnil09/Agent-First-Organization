from ..tools import register_tool
from .f1_utils import *
import pandas as pd
import sqlite3

@register_tool(
    "Searches the Formula 1 database for races based on name and season",
    [
        {**SLOTS['name'], 'required': False},
        {**SLOTS['season'], 'required': False},
    ],
    [{
        "name": "query_result",
        "type": "str",
        "description": "A list of races that match the given criteria. If no race matches, returns 'No results found.'"
    }],
    lambda x: x not in (LOG_IN_FAILURE or NO_RESULT_MESSAGE)
)
def search_race(name=None, season=None) -> str | None:
    if not log_in(): return LOG_IN_FAILURE

    conn = sqlite3.connect(f1.db_path)
    cursor = conn.cursor()
    query = """
        SELECT name AS race_name, season, date, circuit_name, round
        FROM race
        WHERE 1 = 1
    """
    params = []
    if name:
        query += " AND name = ?"
        params.append(name)
    if season:
        query += " AND season = ?"
        params.append(season)
    query += " LIMIT 10"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = NO_RESULT_MESSAGE
    if rows:
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        result = "Available races are:\n" + pd.DataFrame(results).to_string(index=False)
    cursor.close()
    conn.close()
    return result
