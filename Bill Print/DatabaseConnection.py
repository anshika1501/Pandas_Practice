import pyodbc
from datetime import datetime

# Database Connection
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=ROOT\SQLEXPRESS;'
    r'DATABASE=Restaurant;'
    r'Trusted_Connection=yes;'
)

cursor = conn.cursor()

cursor.execute("SELECT ItemName, Price FROM Menu WHERE IsAvailable = 1")

menu = {}
for row in cursor.fetchall():
    menu[row[0]] = row[1]

print("\n------ MENU ------")
for item, price in menu.items():
    print(f"{item} - ₹{price}")


order = {}
n = int(input("\nEnter number of items: "))

for i in range(n):
    item = input("Enter item: ")
    if item in menu:
        qty = int(input("Enter quantity: "))
        order[item] = [qty, menu[item]]
    else:
        print("Item not available")

grand_total = 0
for item, value in order.items():
    qty, price = value
    grand_total += qty * price

cursor.execute(
    "INSERT INTO Bills (GrandTotal) OUTPUT INSERTED.BillID VALUES (?)",
    grand_total
)

bill_id = cursor.fetchone()[0]  # Get newly created BillID


for item, value in order.items():
    qty, price = value
    total = qty * price

    cursor.execute(
        """INSERT INTO BillDetails 
           (BillID, ItemName, Quantity, Price, Total)
           VALUES (?, ?, ?, ?, ?)""",
        bill_id, item, qty, price, total
    )

conn.commit()

print("\n✅ Bill Saved Successfully!")
print("Bill ID:", bill_id)

conn.close()
