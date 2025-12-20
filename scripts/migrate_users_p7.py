import os
import csv
import shutil
from datetime import datetime

def migrate():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    users_csv = os.path.join(base_dir, 'data', 'users.csv')
    backup_csv = os.path.join(base_dir, 'data', f'users_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv')

    print(f"Checking {users_csv}...")
    if not os.path.exists(users_csv):
        print("users.csv not found. Skip migration.")
        return

    # Backup
    print(f"Creating backup at {backup_csv}...")
    shutil.copy2(users_csv, backup_csv)

    # New Fieldnames
    fieldnames = [
        'user_id',
        'password_hash',
        'role',
        'plan',
        'billing_type',
        'balance_enc',
        'status',
        'cancellation_date',
        'plan_change_count',
        'last_plan_change_date',
        'data_retention_until',
        'created_at'
    ]

    updated_rows = []
    with open(users_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Add missing fields with default values
            if 'status' not in row:
                row['status'] = 'active'
            if 'cancellation_date' not in row:
                row['cancellation_date'] = ''
            if 'plan_change_count' not in row:
                row['plan_change_count'] = '0'
            if 'last_plan_change_date' not in row:
                row['last_plan_change_date'] = ''
            if 'data_retention_until' not in row:
                row['data_retention_until'] = ''
            
            # Ensure order and presence of all fields
            new_row = {field: row.get(field, '') for field in fieldnames}
            updated_rows.append(new_row)

    with open(users_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Migration completed. {len(updated_rows)} rows updated.")

if __name__ == '__main__':
    migrate()
