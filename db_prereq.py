id_, text, unique, not_null = 'INTEGER PRIMARY KEY AUTOINCREMENT', \
                              'VARCHAR(20)', 'UNIQUE', \
                              'NOT NULL'

tables = {
    'meals': {
        'id': id_, 'name': ' '.join((text, unique, not_null))
    },
    'ingredients': {
        'id': id_, 'name': ' '.join((text, unique, not_null))
    },
    'measures': {
        'id': id_, 'name': ' '.join((text, unique))
    },
    'recipes': {
        'id': id_, 'name': ' '.join((text, not_null)), 'description': text
    }
}

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
