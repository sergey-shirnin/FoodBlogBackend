from db_prereq import *
import sqlite3
import io
import re
import pprint


def singular(what, consonant='^aeyiou'):
    if re.search('([zx]|ss|[sc]h)es$', what) is not None:
        return re.sub('es$', '', what)
    if re.search(f'[{consonant}]ies$', what) is not None:
        return re.sub('ies$', 'y', what)
    if re.search('ves$', what) is not None:
        return re.sub('ves$', ('f', 'fe')[re.search(f'[{consonant}]ves$', what) is None], what)
    return re.sub('s$', '', what)


class UserManager:
    def __init__(self, db_name, db_map):
        self.db_name, self.db_map = db_name, db_map
        self.linked_table = self.linked_columns = self.linked_prompt = None
        self.link_table = self.link_columns = self.link_data = None
        self.update_table = self.columns = self.entry_row = None
        self.i = self.n_columns = None

    def connect(self):
        conn = sqlite3.connect(f'{self.db_name}.db')
        return conn, conn.cursor()

    def get_entry_row(self, table, template=templates['max_row']):
        conn, curr = self.connect()
        last_row = curr.execute(template.format(table=table)).fetchone()[0]
        if conn: conn.close()
        return 1 if last_row is None else last_row + 1

    def get_link_data(self, entry, table, columns, template=templates['select_from']):
        conn, curr = self.connect()
        query_res = curr.execute(template.format(table=table, columns=", ".join(columns))).fetchall()
        if conn: conn.close()

        if not self.i % self.n_columns and entry:
            if not query_res:
                print(f'Can not manage ER link now as linked table <{self.linked_table}> is empty'); return

            print('  '.join([f'{p[0]}) {p[1]}' for p in query_res]), self.linked_prompt, sep='\n', end=': ')
            linked_ids = set(map(int, input().split()))
            self.link_data += sum(
                zip(*[linked_ids, [self.entry_row] * len(linked_ids)]
                [::[1, -1][self.link_columns.index(columns[0])]]),
                ())
            self.entry_row += 1

    def get_entry(self):
        print(f'{singular(self.update_table).capitalize()} '
              f'{self.columns[self.i % self.n_columns].split("_")[1]}', end=': ')
        entry = input(); self.i += 1
        if self.linked_table:
            self.get_link_data(entry, self.linked_table, self.linked_columns)
        return entry

    def get_linked(self, er_objects='objects', er_options='options'):
        name = columns = prompt = link = link_columns = None
        for rel in relations:
            if self.update_table in rel.get(er_objects):
                name = [t for t in rel.get(er_objects) if t != self.update_table][0]
                columns = ['_'.join((singular(name), 'id')), '_'.join((singular(name), rel.get(er_options)))]
                prompt = rel.get('prompts')[rel.get('objects').index(name)]
                link = rel.get('link')
                link_columns = tuple(k for k, v in self.db_map.get(link).items() if
                                     not any(('AUTOINCREMENT' in v, 'FOREIGN' in k)))

        return name, columns, prompt, link, link_columns

    def set_dependencies(self, update_table):
        self.update_table = update_table
        self.entry_row = self.get_entry_row(update_table)
        self.columns = tuple(k for k, v in self.db_map.get(update_table).items() if
                             not any(('AUTOINCREMENT' in v, 'FOREIGN' in k)))
        self.i = self.n_columns = len(self.columns)
        self.linked_table, self.linked_columns, self.linked_prompt, \
            self.link_table, self.link_columns = self.get_linked()
        self.link_data = []

    def get_data(self, update_table):
        self.set_dependencies(update_table)
        print(f'Pass the empty {" ".join(self.columns[0].split("_"))} to exit.')
        data = [entry for entry in iter(self.get_entry, '')]
        if self.linked_table:
            return {self.update_table: data} | {self.link_table: self.link_data}
        return {self.update_table: data}


class Database:
    def __init__(self, name: str, all_tables: dict, pre_fill: dict = None):
        self.name = name
        self.map = {t: dict(zip(
            ['_'.join((singular(t), c)) if isinstance(c, str) else  # reg columns
             '_'.join((singular(c[0]), c[1])) for c in all_tables.get(t)],  # FK columns
            all_tables.get(t).values())
        ) for t in all_tables}

        for t in all_tables:
            for c in all_tables.get(t):
                if isinstance(c, tuple):
                    ref_table = c[0]
                    ref_col = '_'.join((singular(c[0]), c[1]))
                    self.map[t] |= {
                        f'FOREIGN KEY ({ref_col})': f'REFERENCES {ref_table}({ref_col})'
                    }
        # pprint.pprint(self.map)
        self.create_tables()
        if pre_fill: self.add_data(pre_fill)

    def connect(self):
        conn = sqlite3.connect(f'{self.name}.db')
        return conn, conn.cursor()

    def create_tables(self, template=templates['create'], init_script=io.StringIO()):
        conn, cur = self.connect()
        for table in self.map:
            init_script.write(template.format(table=table, columns=", ".join(
                ' '.join((col_name, col_prop)) for col_name, col_prop in self.map.get(table).items())))
        try:
            cur.executescript(init_script.getvalue())
        except sqlite3.Error as e:
            if conn: conn.rollback(); print(e)
        finally:
            if conn: conn.commit(); conn.close()

    def add_data(self, fill_obj: dict, template=templates['insert']):
        conn, cur = self.connect()
        try:
            for table in fill_obj:
                columns = tuple(k for k, v in self.map.get(table).items() if not any(
                    ('AUTOINCREMENT' in v, 'FOREIGN' in k)))
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
    user = UserManager(db_name=db.name, db_map=db.map)

    db.add_data(user.get_data('recipes'))
    # db.add_data(user.get_data('meals'))  # works backwards as well


main()
