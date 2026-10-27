import sqlite3

con = sqlite3.connect("library.db")
cur = con.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT
);
CREATE TABLE IF NOT EXISTS copy (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(id),
    inventory_no TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS reader (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS loan (
    id INTEGER PRIMARY KEY,
    copy_id INTEGER NOT NULL REFERENCES copy(id),
    reader_id INTEGER NOT NULL REFERENCES reader(id),
    loan_date TEXT NOT NULL,
    return_date TEXT
);
""")

cur.executescript("""
INSERT OR IGNORE INTO book VALUES (1, '1984', 'Джордж Оруэлл');
INSERT OR IGNORE INTO copy VALUES (101, 1, 'INV-001');
INSERT OR IGNORE INTO reader VALUES (1, 'Иван Иванов');
-- Книга выдана 40 дней назад и еще не вернулась (для проверки просрочки)
INSERT OR IGNORE INTO loan VALUES (1, 101, 1, date('now', '-40 days'), NULL);
""")
con.commit()

reader_id = 1
cur.execute('''SELECT b.title, b.author, c.inventory_no, l.loan_date
FROM loan l
JOIN copy c ON c.id = l.copy_id
JOIN book b ON b.id = c.book_id
WHERE l.reader_id = ? AND l.return_date IS NULL;''', (reader_id,))

print("--- Книги на руках у читателя ---")
for row in cur.fetchall():
    print(row)

book_id = 1
cur.execute('''SELECT c.inventory_no,
       CASE WHEN l.id IS NULL THEN 'на полке' ELSE 'выдан' END AS status
FROM copy c
LEFT JOIN loan l ON l.copy_id = c.id AND l.return_date IS NULL
WHERE c.book_id = ?;''', (book_id,))

print("\n--- Статус экземпляров книги ---")
for row in cur.fetchall():
    print(row)

cur.execute('''SELECT r.name, b.title, l.loan_date
FROM loan l
JOIN reader r ON r.id = l.reader_id
JOIN copy c   ON c.id = l.copy_id
JOIN book b   ON b.id = c.book_id
WHERE l.return_date IS NULL
  AND julianday('now') - julianday(l.loan_date) > 30;''')

print("\n--- Должники (более 30 дней) ---")
for row in cur.fetchall():
    print(row)

cur.execute('''SELECT b.title, COUNT(*) AS times_loaned
FROM loan l
JOIN copy c ON c.id = l.copy_id
JOIN book b ON b.id = c.book_id
GROUP BY b.id
ORDER BY times_loaned DESC
LIMIT 5;''')

print("\n--- Популярные книги ---")
for row in cur.fetchall():
    print(row)

con.close()
