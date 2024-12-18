import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import locale

class BudgetTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.state("zoomed")  # Start maximized
        self.budget = 0
        self.password = "1234"  # Default password
        self.categories = ["Food", "Transport", "Shopping", "Utilities", "General"]
        self.currency = "INR"  # Default currency
        self.locale_setting = "en_IN"  # Default locale
        locale.setlocale(locale.LC_ALL, self.locale_setting)

        # Database setup
        self.conn = sqlite3.connect("budget_tracker.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Build UI
        self.create_budget_interface()

        # Add the menu options directly
        self.create_menu()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                amount REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                description TEXT,
                category TEXT,
                amount REAL
            )
        """)
        self.conn.commit()

    def create_budget_interface(self):
        # Budget Frame
        budget_frame = tk.Frame(self.root, padx=10, pady=10)
        budget_frame.pack(pady=10)

        tk.Label(budget_frame, text="Set Budget:", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
        self.budget_entry = tk.Entry(budget_frame, font=("Arial", 14))
        self.budget_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(budget_frame, text="Set", font=("Arial", 14), command=self.set_budget).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(budget_frame, text="Reset Budget", font=("Arial", 14), command=self.reset_budget).grid(row=0, column=3, padx=5, pady=5)

        # Expense Frame
        expense_frame = tk.Frame(self.root, padx=10, pady=10)
        expense_frame.pack(pady=10)

        tk.Label(expense_frame, text="Description:", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(expense_frame, font=("Arial", 14))
        self.description_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(expense_frame, text="Category:", font=("Arial", 14)).grid(row=0, column=2, padx=5, pady=5)
        self.category_entry = tk.StringVar(value="General")
        self.category_menu = tk.OptionMenu(expense_frame, self.category_entry, *self.categories)
        self.category_menu.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(expense_frame, text="Amount:", font=("Arial", 14)).grid(row=0, column=4, padx=5, pady=5)
        self.amount_entry = tk.Entry(expense_frame, font=("Arial", 14))
        self.amount_entry.grid(row=0, column=5, padx=5, pady=5)
        tk.Button(expense_frame, text="Add Expense", font=("Arial", 14), command=self.add_expense).grid(row=0, column=6, padx=5, pady=5)

        # Expenses List Frame
        expenses_frame = tk.Frame(self.root, padx=10, pady=10)
        expenses_frame.pack(pady=10)
        tk.Label(expenses_frame, text="Expenses List:", font=("Arial", 14)).pack(pady=5)
        self.expenses_listbox = tk.Listbox(expenses_frame, width=80, height=15, font=("Arial", 12))
        self.expenses_listbox.pack()
        tk.Button(expenses_frame, text="Delete Selected Expense", font=("Arial", 14), command=self.delete_expense).pack(pady=10)

        # Summary Frame
        summary_frame = tk.Frame(self.root, padx=10, pady=10)
        summary_frame.pack(pady=10)
        self.summary_label = tk.Label(summary_frame, text="Total Expenses: ₹0 | Remaining Budget: ₹0", font=("Arial", 16))
        self.summary_label.pack()

        # Update Expenses and Summary
        self.update_expenses_list()
        self.update_summary()

    def create_menu(self):
        # Creating the menu bar with options
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)

        # Add the options functions directly in the menu
        options_menu.add_command(label="Change Password", command=self.change_password)
        options_menu.add_command(label="Edit Categories", command=self.edit_categories)
        options_menu.add_command(label="Reset Budget", command=self.reset_budget)
        options_menu.add_command(label="Change Currency", command=self.change_currency)

    def set_budget(self):
        try:
            self.budget = float(self.budget_entry.get())
            self.cursor.execute("DELETE FROM budget")
            self.cursor.execute("INSERT INTO budget (amount) VALUES (?)", (self.budget,))
            self.conn.commit()
            self.update_summary()
            messagebox.showinfo("Success", "Budget set successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount.")

    def reset_budget(self):
        self.budget = 0
        self.cursor.execute("DELETE FROM budget")
        self.cursor.execute("DELETE FROM expenses")
        self.conn.commit()
        self.update_expenses_list()
        self.update_summary()
        messagebox.showinfo("Success", "Budget and expenses reset successfully!")

    def change_password(self):
        current_password = simpledialog.askstring("Current Password", "Enter your current password:", show="*")
        if current_password == self.password:
            new_password = simpledialog.askstring("Change Password", "Enter new password:", show="*")
            if new_password:
                self.password = new_password
                messagebox.showinfo("Success", "Password changed successfully!")
        else:
            messagebox.showerror("Error", "Current password is incorrect.")

    def edit_categories(self):
        new_categories = simpledialog.askstring("Edit Categories", "Enter new categories (comma separated):")
        if new_categories:
            self.categories = [category.strip() for category in new_categories.split(",")]
            messagebox.showinfo("Success", "Categories updated successfully!")

    def change_currency(self):
        new_currency = simpledialog.askstring("Change Currency", "Enter new currency code:")
        if new_currency:
            self.currency = new_currency
            messagebox.showinfo("Success", "Currency updated successfully!")

    def add_expense(self):
        try:
            description = self.description_entry.get()
            category = self.category_entry.get()
            amount = float(self.amount_entry.get())
            if description and amount > 0:
                self.cursor.execute("INSERT INTO expenses (description, category, amount) VALUES (?, ?, ?)",
                                    (description, category, amount))
                self.conn.commit()
                self.update_expenses_list()
                self.update_summary()
                self.description_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "Expense added successfully!")
            else:
                messagebox.showerror("Error", "Please enter a valid description and amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid expense amount.")

    def delete_expense(self):
        selected = self.expenses_listbox.curselection()
        if selected:
            index = selected[0]
            self.cursor.execute("SELECT id FROM expenses LIMIT 1 OFFSET ?", (index,))
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute("DELETE FROM expenses WHERE id = ?", (row[0],))
                self.conn.commit()
                self.update_expenses_list()
                self.update_summary()
                messagebox.showinfo("Success", "Expense deleted successfully!")
        else:
            messagebox.showerror("Error", "Please select an expense to delete.")

    def update_expenses_list(self):
        self.expenses_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT description, category, amount FROM expenses")
        for description, category, amount in self.cursor.fetchall():
            self.expenses_listbox.insert(tk.END, f"{description} ({category}) - ₹{amount:.2f}")

    def update_summary(self):
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = self.cursor.fetchone()[0] or 0
        remaining_budget = self.budget - total_expenses
        self.summary_label.config(
            text=f"Total Expenses: ₹{total_expenses:.2f} | Remaining Budget: ₹{remaining_budget:.2f}"
        )
        if remaining_budget < 0:
            messagebox.showwarning("Warning", "You have exceeded your budget!")

    def run(self):
        self.root.mainloop()


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTrackerGUI(root)
    app.run()
