import argparse
import threading
import time

from nsaph.db import Connection
from nsaph.model import Table

SQL12 = """
    SELECT 
      now()::TIME(0),
      p.command, 
      a.query, 
      p.phase, 
      p.blocks_total, 
      p.blocks_done, 
      p.tuples_total, 
      p.tuples_done
    FROM pg_stat_progress_create_index p 
    JOIN pg_stat_activity a ON p.pid = a.pid
"""

SQL11 = """
    SELECT 
      now()::TIME(0), 
      a.query,
      a.state
    FROM pg_stat_activity a
    WHERE a.query LIKE 'CREATE%INDEX%' 
"""

def index(table, cursor, force):
    table.build_indices(cursor, force)


def print_stat(connection):
    cursor = connection.cursor()
    version = connection.info.server_version
    if version > 120000:
        sql = SQL12
    else:
        sql = SQL11
    cursor.execute(sql)
    for row in cursor:
        if version > 120000:
            t = row[0]
            c = row[1]
            q = row[2][len(c):].strip().split(" ")
            if q:
                n = q[0]
            else:
                n = "?"
            p = row[3]
            b = row[5] * 100.0 / row[4] if row[4] else 0
            tp = row[7] * 100.0 / row[6] if row[6] else 0
            msg = "[{}] {}: {}. Blocks: {:2.0f}%, Tuples: {:2.0f}%"\
                .format(str(t), p, n, b, tp)
        else:
            t = row[0]
            q = row[2]
            s = row[2]
            msg = "[{}] {}: {}".format(t, s, q)
        print(msg)



def build_indices(table: Table, force: bool = False):
    with Connection() as connection:
        connection.autocommit = True
        cursor = connection.cursor()
        x = threading.Thread(target=index, args=(table, cursor, force))
        x.start()
        while (x.is_alive()):
            time.sleep(10)
            print_stat(connection)
        x.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser (description="Build indices")
    parser.add_argument("--config", "-c",
                        help="Path to a config file for a table",
                        required=True)
    parser.add_argument("--force", action='store_true',
                        help="Force reindexing if index already exists")

    args = parser.parse_args()

    table = Table(args.config, None, args.force)
    build_indices(table)
