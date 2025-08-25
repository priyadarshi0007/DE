import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def save_df_to_sqlite(df, db_name: str, table_name: str, if_exists="replace"):
    """
    Save a Pandas DataFrame into a SQLite database table.
    """
    try:
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        logging.info("Saved %d rows into '%s' table in %s", len(df), table_name, db_name)
    except Exception as e:
        logging.error("Error saving DataFrame to SQLite: %s", e, exc_info=True)
    finally:
        conn.close()


def run_query(db_name: str, query: str):
    """
    Run a SQL query on the given SQLite DB and return all rows.
    """
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        logging.info("Query executed: %s", query)
        return rows
    except Exception as e:
        logging.error("Error running query: %s", e, exc_info=True)
        return []
    finally:
        conn.close()