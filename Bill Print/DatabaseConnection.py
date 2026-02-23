import pyodbc
from datetime import datetime

class DatabaseConnection:
    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=ROOT\SQLEXPRESS;'
                r'DATABASE=Restaurant;'
                r'Trusted_Connection=yes;'
            )
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            print("Error connecting to database:", e)
            raise

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
        try:
            n = int(input("Enter number of items: "))
        except ValueError:
            print("Invalid input! Using 1 item by default.")
            n = 1

        for _ in range(n):
            while True:
                item = input("Enter item: ").strip()
                if item in self.menu:
                    break
                else:
                    print("Item not available. Please choose from the menu.")

            try:
                qty = int(input(f"Enter quantity for {item}: "))
                if qty <= 0:
                    print("Quantity must be positive. Using 1 by default.")
                    qty = 1
            except ValueError:
                print("Invalid input! Using quantity 1 by default.")
                qty = 1

            self.order[item] = [qty, self.menu[item]]

    def calculate_total(self):
        self.grand_total = sum(qty * price for qty, price in self.order.values())

    def print_bill(self):
        print("\n------ BILL ------")
        print(f"{'Item':<15}{'Qty':<5}{'Price':<10}{'Total':<10}")
        print("-" * 40)
        for item, (qty, price) in self.order.items():
            total = qty * price
            print(f"{item:<15}{qty:<5}{price:<10}{total:<10}")
        print("-" * 40)
        print(f"{'Grand Total':<30}₹{self.grand_total}")
        print("-" * 40)

    def save_bill(self):
        try:
            self.db.cursor.execute(
                "INSERT INTO Bills (GrandTotal) OUTPUT INSERTED.BillID VALUES (?)",
                self.grand_total
            )
            bill_id = self.db.cursor.fetchone()[0]

            for item, (qty, price) in self.order.items():
                total = qty * price
                self.db.cursor.execute(
                    """INSERT INTO BillDetails
                       (BillID, ItemName, Quantity, Price, Total)
                       VALUES (?, ?, ?, ?, ?)""",
                    bill_id, item, qty, price, total
                )

            self.db.commit()
            print("\nBill saved successfully with Bill ID:", bill_id)

        except pyodbc.Error as e:
            print("Error saving bill to database:", e)

    def close_connection(self):
        self.db.close()


if __name__ == "__main__":
    billing = RestaurantBilling()
    billing.fetch_menu()
    billing.take_order()
    billing.calculate_total()
    billing.print_bill()
    billing.save_bill()
    billing.close_connection()
