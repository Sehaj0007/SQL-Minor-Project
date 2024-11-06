import tkinter as tk
import sqlite3


class ExpenseTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Expense Tracker")
        self.master.geometry("500x450")
        self.master.configure(bg="#2C5F2D")

        # Connect to SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # For creating GUI elements
        self.create_widgets()

    def create_tables(self):
        # Create tables for categories and expenses if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Title label
        title_label = tk.Label(self.master, text="Expense Tracker Menu", font='Cambria 24 bold', bg="#2C5F2D", fg="white")
        title_label.pack(pady=20)

        # Frame for buttons
        button_frame = tk.Frame(self.master, bg="#2C5F2D")
        button_frame.pack(pady=10, padx=20, fill='both')

        button_style = {'padx': 10, 'pady': 10, 'bg': "#cbce91", 'fg': "black", 'font': 'Cambria 14 bold'}

        tk.Button(button_frame, text="Add Expense", command=self.add_expense_dialog, **button_style).pack(pady=5, fill='x')
        tk.Button(button_frame, text="Add Category", command=self.add_category_dialog, **button_style).pack(pady=5, fill='x')
        tk.Button(button_frame, text="View Expenses", command=self.view_expenses_dialog, **button_style).pack(pady=5, fill='x')
        tk.Button(button_frame, text="View Categories", command=self.view_categories_dialog, **button_style).pack(pady=5, fill='x')
        tk.Button(button_frame, text="Exit", command=self.master.quit, **button_style).pack(pady=10, fill='x')

        # Footer label
        footer_label = tk.Label(self.master, text="[A Minor Project in Python]", font='Cambria 10', bg="#2C5F2D", fg="white")
        footer_label.pack(side='bottom', pady=10)

    def add_expense_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Expense")
        dialog.geometry("400x250")
        dialog.configure(bg="#2C5F2D")

        tk.Label(dialog, text="Date (YYYY-MM-DD):", fg="white", bg="#2C5F2D").pack(pady=5)
        date_entry = tk.Entry(dialog, width=40)
        date_entry.pack(pady=5)

        tk.Label(dialog, text="Amount (₹):", fg="white", bg="#2C5F2D").pack(pady=5)
        amount_entry = tk.Entry(dialog, width=40)
        amount_entry.pack(pady=5)

        tk.Label(dialog, text="Category:", fg="white", bg="#2C5F2D").pack(pady=5)
        category_entry = tk.Entry(dialog, width=40)
        category_entry.pack(pady=5)

        def submit_expense():
            date = date_entry.get()
            amount = amount_entry.get()
            category = category_entry.get()
            try:
                amount = float(amount)
                if date and category:
                    self.add_expense_to_db(date, amount, category)
                    self.show_message("Success", f"Added: ₹{amount:.2f} on {date} in '{category}'")
                    dialog.destroy()
                else:
                    self.show_message("Error", "Please fill in all fields.")
            except ValueError:
                self.show_message("Error", "Amount must be a number.")

        tk.Button(dialog, text="Submit", command=submit_expense, bg="#cbce91", fg="black").pack(pady=10)

    def add_expense_to_db(self, date, amount, category):
        # Insert or ignore category if it doesn't exist
        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        self.conn.commit()

        # Get category ID
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_id = self.cursor.fetchone()[0]

        # Insert expense
        self.cursor.execute("INSERT INTO expenses (date, amount, category_id) VALUES (?, ?, ?)", (date, amount, category_id))
        self.conn.commit()

    def add_category_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Category")
        dialog.geometry("400x150")
        dialog.configure(bg="#2C5F2D")

        tk.Label(dialog, text="Category Name:", fg="white", bg="#2C5F2D").pack(pady=5)
        category_entry = tk.Entry(dialog, width=40)
        category_entry.pack(pady=5)

        def submit_category():
            category = category_entry.get()
            if category:
                self.add_category_to_db(category)
                self.show_message("Success", f"Category '{category}' added.")
                dialog.destroy()
            else:
                self.show_message("Error", "Please enter a category name.")

        tk.Button(dialog, text="Submit", command=submit_category, bg="#cbce91", fg="black").pack(pady=10)

    def add_category_to_db(self, category):
        # Insert or ignore category if it already exists
        self.cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        self.conn.commit()

    def view_expenses_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("View Expenses")
        dialog.geometry("400x250")
        dialog.configure(bg="#2C5F2D")

        # Retrieve expenses from database
        self.cursor.execute('''
            SELECT date, amount, categories.name
            FROM expenses
            JOIN categories ON expenses.category_id = categories.id
        ''')
        expenses = self.cursor.fetchall()

        expense_summary = "\n".join(f"{cat}: ₹{amt:.2f} on {date}" for date, amt, cat in expenses)
        if not expense_summary:
            expense_summary = "No expenses recorded."

        tk.Label(dialog, text=expense_summary, fg="white", bg="#2C5F2D", wraplength=380).pack(pady=20)
        tk.Button(dialog, text="OK", command=dialog.destroy, bg="#cbce91", fg="black").pack(pady=10)

    def view_categories_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("View Categories")
        dialog.geometry("400x200")
        dialog.configure(bg="#2C5F2D")

        # Retrieve categories from database
        self.cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in self.cursor.fetchall()]

        category_list = "\n".join(categories) if categories else "No categories available."

        tk.Label(dialog, text=category_list, fg="white", bg="#2C5F2D", wraplength=380).pack(pady=20)
        tk.Button(dialog, text="OK", command=dialog.destroy, bg="#cbce91", fg="black").pack(pady=10)

    def show_message(self, title, message):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.configure(bg="#2C5F2D")

        tk.Label(dialog, text=message, fg="white", bg="#2C5F2D", wraplength=380).pack(pady=20)
        tk.Button(dialog, text="OK", command=dialog.destroy, bg="#cbce91", fg="black").pack(pady=10)

    def __del__(self):
        # Close database connection when the application is closed
        self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
