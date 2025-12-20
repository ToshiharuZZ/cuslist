import os
import csv
import shutil
from datetime import datetime

def migrate():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    customers_csv = os.path.join(base_dir, 'data', 'customers.csv')
    backup_csv = os.path.join(base_dir, 'data', f'customers_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

    print(f"Checking {customers_csv}...")
    if not os.path.exists(customers_csv):
        print("customers.csv not found. Skip migration.")
        return

    # Backup
    print(f"Creating backup at {backup_csv}...")
    shutil.copy2(customers_csv, backup_csv)

    # New Fieldnames
    fieldnames = [
        'customer_id',
        'user_id',
        'name_enc',
        'address_enc',
        'phone_enc',
        'email_enc',
        'created_at'
    ]

    updated_rows = []
    with open(customers_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Add missing fields with default values
            if 'user_id' not in row:
                row['user_id'] = 'admin' # Default owner for existing customers
            
            # Ensure order and presence of all fields
            new_row = {field: row.get(field, '') for field in fieldnames}
            updated_rows.append(new_row)

    with open(customers_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Migration completed. {len(updated_rows)} rows updated.")

if __name__ == '__main__':
    migrate()
