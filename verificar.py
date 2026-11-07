import sqlite3

con = sqlite3.connect("data/banco.db")

resultado1 = con.execute(
    "SELECT COUNT(*), MIN(monto), MAX(monto) FROM transacciones"
).fetchone()
print("Filas, monto mínimo, monto máximo:", resultado1)

resultado2 = con.execute(
    "SELECT tipo, COUNT(*) FROM transacciones GROUP BY tipo"
).fetchall()
print("Transacciones por tipo:")
for fila in resultado2:
    print(fila)

con.close()