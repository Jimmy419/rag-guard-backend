import sqlite3
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("db-mcp-server")

DB_PATH = "feedback.db"

@mcp.tool()
def query_feedback_db(sql_query: str) -> str:
    """
    Execute a SQL query against the feedback.db SQLite database.
    The database has a table 'feedback' with columns:
    - id (INTEGER PRIMARY KEY)
    - thread_id (TEXT)
    - question (TEXT)
    - answer (TEXT)
    - rating (INTEGER)
    - created_at (TIMESTAMP)
    - resolved (BOOLEAN)
    
    Returns the query results as a JSON string.
    Only SELECT statements are allowed for safety.
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT statements are allowed."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
            
        conn.close()
        return json.dumps(results, ensure_ascii=False, default=str)
    except Exception as e:
        return f"Error executing query: {str(e)}"

if __name__ == "__main__":
    mcp.run()
