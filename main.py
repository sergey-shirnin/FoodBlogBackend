import sqlite3


class Database:
    def __init__(self, db_name: str, tables_names: tuple, columns: dict, adds: dict):
        self.db_name = db_name
        self.db_map = {table: dict(zip(
            ('_'.join((table[:-1], col_postfix)) for col_postfix in columns),
            [' '.join((columns.get(col), adds.get(table, dict()).get(col, ''))).rstrip() for col in columns])
        ) for table in tables_names}
        self.initiate_db()

    def connect(self):
        conn = sqlite3.connect(f'{self.db_name}.db')
        return conn, conn.cursor()

    def initiate_db(self, template='CREATE TABLE {table} ({columns});'):
        conn, cur = self.connect()
        for table in self.db_map:
            columns = ", ".join(
                ' '.join((col_name, col_prop)) for col_name, col_prop in self.db_map.get(table).items()
            )
            cur.execute(template.format(table=table, columns=columns))
        conn.commit(); conn.close()

    def add_data(self, fill_obj: dict, template='INSERT INTO {table} ({columns}) VALUES ("{values}");'):
        conn, cur = self.connect()
        for req_table, table in zip(fill_obj, self.db_map):
            if req_table == table:
                columns_data = self.db_map.get(table)
                columns = ', '.join(c for c in columns_data if 'AUTOINCREMENT' not in columns_data.get(c))
                values = '"), ("'.join(fill_obj.get(table))
                cur.execute(template.format(table=table, columns=columns, values=values))
            else:
                print(f'not updated {req_table} -> table name mismatch did you mean {table}?')
        conn.commit(); conn.close()


def main():
    tables = ('meals', 'ingredients', 'measures')
    columns = {'id': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'name': 'VARCHAR(20) UNIQUE'}
    adds = {'meals': {'name': 'NOT NULL'}, 'ingredients': {'name': 'NOT NULL'}}
    init_data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
                 "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
                 "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    food_db = Database('food_blog', tables, columns, adds)
    food_db.add_data(init_data)


main()
