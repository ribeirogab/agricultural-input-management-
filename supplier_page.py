import tkinter as tk
from tkinter import ttk, messagebox
from common import (
    get_current_timestamp,
    import_data_from_json,
    export_data_to_json,
    generate_unique_id,
    is_valid_email,
    load_from_csv,
    refresh_table,
    save_to_csv,
)

# Initial data for suppliers
suppliers = {}

# CSV file for suppliers
SUPPLIER_CSV_FILE = "suppliers.csv"


# Function to load suppliers from CSV
def load_suppliers_from_csv(tree_suppliers):
    rows = load_from_csv(SUPPLIER_CSV_FILE)
    for row in rows:
        supplier_id = row["ID"]  # Load UUID as ID
        suppliers[supplier_id] = {
            "name": row["Name"],
            "email": row["Email"],
            "created_at": row["Created At"],
        }
    refresh_table(tree_suppliers, suppliers)


# Function to register a new supplier
def add_supplier(supplier_name, email):
    suppliers[generate_unique_id()] = {
        "name": supplier_name,
        "email": email,
        "created_at": get_current_timestamp(),
    }
    save_suppliers_to_csv()


# Function to save suppliers to CSV
def save_suppliers_to_csv():
    headers = ["ID", "Name", "Email", "Created At"]
    data = [
        [
            supplier_id,
            details["name"],
            details["email"],
            details["created_at"],
        ]
        for supplier_id, details in suppliers.items()
    ]
    save_to_csv(SUPPLIER_CSV_FILE, headers, data)


# Function to export data when the button is clicked
def export_data():
    export_data_to_json(suppliers, "suppliers")
    messagebox.showinfo("Success", "Data exported successfully!")


# Function to handle the import action
def import_data(tree_suppliers):
    try:
        data = import_data_from_json()

        if data:
            for supplier_id, details in data.items():
                suppliers[supplier_id] = {
                    "name": details["name"],
                    "email": details["email"],
                    "created_at": details.get("created_at", get_current_timestamp()),
                }

            # Update the CSV file with the new data
            save_suppliers_to_csv()
            refresh_table(tree_suppliers, suppliers)

            messagebox.showinfo("Success", "Data imported successfully!")
    except FileNotFoundError:
        messagebox.showwarning("No File Selected", "Please select a JSON file.")
    except ValueError as ve:
        messagebox.showerror("Invalid JSON", str(ve))
    except RuntimeError as re:
        messagebox.showerror("Error", str(re))
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")


# Function to add a new supplier via GUI
def add_supplier_gui(entry_supplier_name, entry_supplier_email, tree_suppliers):
    supplier_name = entry_supplier_name.get()
    supplier_email = entry_supplier_email.get()

    # Validate if email is valid
    if not is_valid_email(supplier_email):
        messagebox.showerror("Error", "Invalid email address!")
        return

    if not supplier_name or not supplier_email:
        messagebox.showerror("Error", "All fields must be filled!")
        return

    add_supplier(supplier_name, supplier_email)
    refresh_table(tree_suppliers, suppliers)
    clear_supplier_fields(entry_supplier_name, entry_supplier_email)


# Function to clear input fields for suppliers
def clear_supplier_fields(entry_supplier_name, entry_supplier_email):
    entry_supplier_name.delete(0, tk.END)
    entry_supplier_email.delete(0, tk.END)


# Function to remove the selected supplier
def remove_supplier(tree_suppliers):
    selected_item = tree_suppliers.selection()

    if not selected_item:
        messagebox.showerror("Error", "No supplier selected to remove!")
        return

    selected_supplier_id = tree_suppliers.item(selected_item)["values"][0]

    # Confirm before deletion
    confirm = messagebox.askyesno(
        "Confirm", "Are you sure you want to delete this supplier?"
    )
    if confirm:
        del suppliers[selected_supplier_id]  # Remove supplier from dictionary
        save_suppliers_to_csv()  # Update CSV file
        refresh_table(tree_suppliers, suppliers)


# Function to create the supplier page
def create_supplier_page(root):
    frame_suppliers = tk.Frame(root)

    # Title and Description
    tk.Label(frame_suppliers, text="Supplier Management", font=("Arial", 18)).pack(
        pady=10
    )
    tk.Label(
        frame_suppliers,
        text="Add and manage your suppliers below.",
    ).pack(pady=5)

    # Frame for adding new suppliers
    frame_add_suppliers = tk.Frame(frame_suppliers)
    frame_add_suppliers.pack(pady=10)

    tk.Label(frame_add_suppliers, text="Supplier Name:").grid(row=0, column=0)
    entry_supplier_name = tk.Entry(frame_add_suppliers)
    entry_supplier_name.grid(row=0, column=1)

    tk.Label(frame_add_suppliers, text="Email:").grid(row=1, column=0)
    entry_supplier_email = tk.Entry(frame_add_suppliers)
    entry_supplier_email.grid(row=1, column=1)

    # Button to add supplier
    btn_add_supplier = tk.Button(
        frame_add_suppliers,
        text="Add Supplier",
        command=lambda: add_supplier_gui(
            entry_supplier_name, entry_supplier_email, tree_suppliers
        ),
    )
    btn_add_supplier.grid(row=2, columnspan=2, pady=10)

    # Button to remove supplier
    btn_remove_supplier = tk.Button(
        frame_add_suppliers,
        text="Remove Supplier",
        command=lambda: remove_supplier(tree_suppliers),
    )
    btn_remove_supplier.grid(row=3, columnspan=2, pady=10)

    # Table for suppliers (after the form)
    frame_table_suppliers = tk.Frame(frame_suppliers)
    frame_table_suppliers.pack(pady=10)

    columns_suppliers = ("ID", "Name", "Email", "Created At")
    tree_suppliers = ttk.Treeview(
        frame_table_suppliers, columns=columns_suppliers, show="headings"
    )
    tree_suppliers.pack()

    for col in columns_suppliers:
        tree_suppliers.heading(col, text=col)

    # Frame for adding new supplies
    frame_footer_buttons = tk.Frame(frame_table_suppliers)
    frame_footer_buttons.pack(pady=10)

    # Button to export data
    btn_export_data = tk.Button(
        frame_footer_buttons,
        text="Export Data (JSON)",
        command=export_data,
    )
    btn_export_data.grid(row=1, column=1, sticky="ew")

    # Button to import data
    btn_import_data = tk.Button(
        frame_footer_buttons,
        text="Import Data (JSON)",
        command=lambda: import_data(tree_suppliers),
    )
    btn_import_data.grid(row=1, column=2, sticky="ew")

    # Load existing suppliers from CSV
    load_suppliers_from_csv(tree_suppliers)

    return frame_suppliers
