id_, text, integer, unique, not_null = 'INTEGER PRIMARY KEY AUTOINCREMENT', \
                                       'VARCHAR(20)', \
                                       'INTEGER', \
                                       'UNIQUE', \
                                       'NOT NULL'

templates = {'create': 'CREATE TABLE {table} ({columns});',
             'insert': 'INSERT INTO {table} ({columns}) VALUES ({values});',
             'select_from': 'SELECT {columns} FROM {table};',
             'max_row': 'SELECT max(rowid) FROM {table};'}

# specify column name as tuple ('parent table', 'parent column') to make it a FK
tables = {
    'ingredients': {
        'id': id_, 'name': ' '.join((text, unique, not_null))
    },
    'measures': {
        'id': id_, 'name': ' '.join((text, unique))
    },
    'meals': {
        'id': id_, 'name': ' '.join((text, unique, not_null))
    },
    'recipes': {
        'id': id_, 'name': ' '.join((text, not_null)), 'description': text
    },
    'serve': {
        'id': id_,
        ('meals', 'id'): ' '.join((integer, not_null)),
        ('recipes', 'id'): ' '.join((integer, not_null))
    }
}

relations = ({'objects': ('meals', 'recipes'),
              'prompts': ('When the dish can be served', 'What dishes fit this meal'),
              'link': 'serve', 'options': 'name'
              },
             )

init_data = {
    "meals": (
        "breakfast", "brunch", "lunch", "supper"
    ),
    "ingredients": (
        "milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"
    ),
    "measures": (
        "ml", "g", "l", "cup", "tbsp", "tsp", "dsp", ""
    )
}
