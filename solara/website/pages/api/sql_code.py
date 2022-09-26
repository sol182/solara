"""
# SqlCode

SQL textfield input with auto complete and SQL syntax highlighting.

To get auto complete for the colum names, prefix is with the table name, i.e. "titanic.sur ctrl+space"
"""
import os
import sqlite3
import threading
from typing import Optional, cast

import pandas as pd

try:
    import vaex.datasets
except ImportError:
    vaex = None

from solara.alias import reacton, rv, sol

if vaex is not None:
    df_iris = vaex.datasets.iris().to_pandas_df()
    df_titanic = vaex.datasets.titanic().to_pandas_df()

    def create_db():
        conn = sqlite3.connect(filename)
        df_iris.to_sql("iris", conn, if_exists="replace", index=False)
        df_titanic.to_sql("titanic", conn, if_exists="replace", index=False)
        conn.close()

    filename = "solara-sql.db"
    if not os.path.exists(filename):
        create_db()

    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    table_names = [k[0] for k in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    table_hints = {table_name: conn.execute(f"SELECT * from {table_name} LIMIT 1").fetchone().keys() for table_name in table_names}


@reacton.component
def Page():
    if vaex is None:
        return sol.Error("Vaex is not installed, run pip install vaex-core vaex-hdf5")
    query, set_query = reacton.use_state("SELECT * from titanic")
    query_executed, set_query_executed = reacton.use_state(cast(Optional[str], None))

    def run_query(cancel: threading.Event) -> pd.DataFrame:
        if not query_executed:
            return
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        cursor.execute(query_executed)

        df = pd.DataFrame(cursor.fetchall(), columns=[k[0] for k in cursor.description])
        return df

    result: sol.Result[pd.DataFrame] = sol.use_thread(run_query, dependencies=[query_executed])
    with sol.VBox() as main:
        sol.SqlCode(query=query, tables=table_hints, on_query=set_query)
        enable_execute = (query != query_executed) or result.error is not None

        def execute():
            set_query_executed(query)
            if query == query_executed and result.error:
                result.retry()  # type: ignore

        sol.Button("Execute", on_click=execute, disabled=not enable_execute)
        if result.error:
            sol.Error(f"Ooops {result.error}")
        elif not query:
            sol.Info("No query")

        elif result.value is not None:
            sol.Markdown(f"Result for query: `{query_executed}`")
            df = result.value
            sol.DataTable(df)
        elif query_executed is not None:
            with sol.Div():
                sol.Text("Loading data...")
                rv.ProgressCircular(indeterminate=True, class_="solara-progress")
    return main
