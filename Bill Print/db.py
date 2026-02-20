import pyodbc
from datetime import datetime


class DatabaseConnection:
    def __init__(self):
        self.conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=ROOT\SQLEXPRESS;'
            r'DATABASE=Restaurant;'
            r'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class RestaurantBilling:
    def __init__(self):
        self.db = DatabaseConnection()
        self.menu = {}
        self.order = {}
        self.grand_total = 0

    def fetch_menu(self):
        self.db.cursor.execute(
            "SELECT ItemName, Price FROM Menu WHERE IsAvailable = 1"
        )

        for row in self.db.cursor.fetchall():
            self.menu[row[0]] = row[1]

        print("\n------ MENU ------")
        for item, price in self.menu.items():
            print(f"{item} - ₹{price}")

    def take_order(self):
        n = int(input("\nEnter number of items: "))

        for i in range(n):
            item = input("Enter item: ")
            if item in self.menu:
                qty = int(input("Enter quantity: "))
                self.order[item] = [qty, self.menu[item]]
            else:
                print("Item not available")

    def calculate_total(self):
        for item, value in self.order.items():
            qty, price = value
            self.grand_total += qty * price

    def save_bill(self):
        # Insert into Bills table
        self.db.cursor.execute(
            "INSERT INTO Bills (GrandTotal) OUTPUT INSERTED.BillID VALUES (?)",
            self.grand_total
        )

        bill_id = self.db.cursor.fetchone()[0]

        # Insert into BillDetails
        for item, value in self.order.items():
            qty, price = value
            total = qty * price

            self.db.cursor.execute(
                """INSERT INTO BillDetails
                   (BillID, ItemName, Quantity, Price, Total)
                   VALUES (?, ?, ?, ?, ?)""",
                bill_id, item, qty, price, total
            )

        self.db.commit()

        print("\n✅ Bill Saved Successfully!")
        print("Bill ID:", bill_id)

    def close_connection(self):
        self.db.close()



if __name__ == "__main__":
    billing = RestaurantBilling()
    billing.fetch_menu()
    billing.take_order()
    billing.calculate_total()
    billing.save_bill()
    billing.close_connection()
