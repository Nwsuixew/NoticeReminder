# Python Standard Library
import sqlite3


def create_db(db: str):
    conn = sqlite3.connect(db)
    conn.close()


def is_table_exist(db: str, table: str) -> bool:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sqlite_master WHERE type = 'table' AND tbl_name = '%s'" % table)
    res = cursor.fetchall()

    conn.commit()
    conn.close()

    if res:
        return True
    else:
        return False


def create_table(db: str, table: str, column: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE %s(sn INTEGER PRIMARY KEY AUTOINCREMENT, %s)' % (table, column))

    conn.commit()
    conn.close()


def is_column_exist(db: str, table: str, column: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sqlite_master "
                   "WHERE type = 'table' AND tbl_name = '%s' AND sql LIKE '%s'" % (table, '%' + column + '%'))
    res = cursor.fetchall()

    conn.commit()
    conn.close()

    if res:
        return True
    else:
        return False


def insert_column(db: str, table: str, column: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('ALTER TABLE %s ADD %s' % (table, column))

    conn.commit()
    conn.close()


def insert_row(db: str, table: str, column: str, data: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO %s (%s) VALUES (%s)' % (table, column, data))

    conn.commit()
    conn.close()


def delete_row(db: str, table: str, condition: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM %s WHERE %s' % (table, condition))

    conn.commit()
    conn.close()


def update_row(db: str, table: str, column_and_data: str, condition: str):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('UPDATE %s SET %s WHERE %s' % (table, column_and_data, condition))

    conn.commit()
    conn.close()


def fetch_row_ascending(db: str, table: str, column='*', key='sn', length=1, offset=0) -> tuple:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('SELECT %s FROM %s ORDER BY %s LIMIT %d OFFSET %d' % (column, table, key, length, offset))
    res = cursor.fetchall()

    conn.close()

    return tuple(res)


def fetch_row_descending(db: str, table: str, column='*', key='sn', length=1, offset=0) -> tuple:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('SELECT %s FROM %s ORDER BY %s DESC LIMIT %d OFFSET %d' % (column, table, key, length, offset))
    res = cursor.fetchall()

    conn.close()

    return tuple(res)


def fetch_row_all(db: str, table: str, column: str) -> tuple:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('SELECT %s FROM %s' % (column, table))
    res = cursor.fetchall()

    conn.close()

    return tuple(res)


def fetch_row_by_condition(db: str, table: str, column: str, condition: str) -> tuple:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute('SELECT %s FROM %s WHERE %s' % (column, table, condition))
    res = cursor.fetchall()

    conn.close()

    return tuple(res)
