import sqlite3

DB_NAME = 'techrepair.db'


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS techs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES owners(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS specialists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tech_id INTEGER,
            specialist_id INTEGER,
            datetime TEXT NOT NULL,
            FOREIGN KEY (tech_id) REFERENCES techs(id),
            FOREIGN KEY (specialist_id) REFERENCES specialists(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')


    cur.execute('SELECT COUNT(*) FROM owners')
    if cur.fetchone()[0] == 0:
        cur.executemany('INSERT INTO owners (name, phone) VALUES (?, ?)', [
            ('Иванов Ваня', '+7-900-131-53-11'),
            ('Ветроломова Александра', '+7-900-192-61-52'),
        ])
        cur.executemany('INSERT INTO techs (name, owner_id) VALUES (?, ?)', [
            ('Компьютер', 1),
            ('Телефон', 2),
            ('Планшет', 3),
        ])
        cur.executemany('INSERT INTO specialists (name) VALUES (?)', [
            ('Витя Коряга',),
            ('Влад Бадминтон',),
        ])
        cur.executemany('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', [
            ('Плашки 16 гигабайт', 7000.0, 20),
            ('Кулеры', 3000.0, 15),
            ('Мышка', 900.0, 5),
        ])

    conn.commit()
    conn.close()



def get_all_appointments():
    conn = get_connection()
    rows = con.execute('''
        SELECT a.id, t.name AS tech_name, s.name AS specialist_name, a.datetime
        FROM appointments a
        JOIN techs t ON t.id = a.tech_id
        JOIN specialists s ON s.id = a.specialist_id
        ORDER BY a.datetime
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_appointment(tech_id, specialist_id, datetime_str):
    conn = get_connection()
    conn.execute(
        'INSERT INTO appointments (tech_id, specialist_id, datetime) VALUES (?, ?, ?)',
        (tech_id, specialist_id, datetime_str)
    )
    conn.commit()
    conn.close()


def is_specialist_busy(specialist_id, datetime_str):
    conn = get_connection()
    row = conn.execute(
        'SELECT COUNT(*) FROM appointments WHERE specialist_id=? AND datetime=?',
        (specialist_id, datetime_str)
    ).fetchone()
    conn.close()
    return row[0] > 0


def get_all_techs():
    conn = get_connection()
    rows = conn.execute('SELECT id, name FROM techs').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_specialists():
    conn = get_connection()
    rows = conn.execute('SELECT id, name FROM specialists').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_products():
    conn = get_connection()
    rows = conn.execute('SELECT id, name, price, stock FROM products').fetchall()
    conn.close()
    return [dict(r) for r in rows]