from db_prereq import *
import io
import sqlite3


class UserManager:
    def __init__(self, all_tables):
        self.all_tables = all_tables
        self.update_table = self.columns = None
        self.i = self.n_columns = 0

    def entry(self):
        print(f'{self.update_table[:-1].capitalize()} {self.columns[self.i % self.n_columns]}', end=': ')
        entry = input(); self.i += 1
        return entry

    def get_data(self, update_table):
        self.update_table = update_table
        self.columns = tuple(k for k, v in self.all_tables[self.update_table].items() if 'AUTOINCREMENT' not in v)
        self.i = self.n_columns = len(self.columns)

        print(f'Pass the empty {self.update_table[:-1]} {self.columns[0]} to exit.')
        data = [entry for entry in iter(self.entry, '')]

        return {self.update_table: data}


class Database:
    def __init__(self, db_name: str, all_tables: dict, pre_fill: dict):
        self.db_name = db_name
        self.db_map = {
            table: dict(zip(
                ['_'.join((table[:-1], col_post)) for col_post in all_tables.get(table)],
                all_tables.get(table).values())) for table in all_tables}
        self.initiate_db()
        self.add_data(pre_fill)

    def connect(self):
        conn = sqlite3.connect(f'{self.db_name}.db')
        return conn, conn.cursor()

    def initiate_db(self, template='CREATE TABLE {table} ({columns});', init_script=io.StringIO()):
        conn, cur = self.connect()
        for table in self.db_map:
            init_script.write(template.format(table=table, columns=", ".join(
                ' '.join((col_name, col_prop)) for col_name, col_prop in self.db_map.get(table).items())))
        try:
            cur.executescript(init_script.getvalue())
        except sqlite3.Error as e:
            if conn: conn.rollback(); print(e)
        finally:
            if conn: conn.commit(); conn.close()

    def add_data(self, fill_obj: dict, template='INSERT INTO {table} ({columns}) VALUES ({values});'):
        conn, cur = self.connect()
        try:
            for table in fill_obj:
                columns_data = self.db_map.get(table)
                columns = [c for c in columns_data if 'AUTOINCREMENT' not in columns_data.get(c)]
                data = map(tuple, zip(*[iter(fill_obj.get(table))] * len(columns)))
                cur.executemany(template.format(table=table,
                                                columns=', '.join(columns),
                                                values=', '.join(['?'] * len(columns))
                                                ), data)
        except sqlite3.Error as e:
            if conn: conn.rollback(); print(e)
        finally:
            if conn: conn.commit(); conn.close()


def main():
    db = Database('food_blog', all_tables=tables, pre_fill=init_data)
    user = UserManager(all_tables=tables)

    db.add_data(user.get_data('recipes'))


main()
