"""
CSVデータをSQLiteデータベースへ移行するスクリプト
"""
import os
import csv
import sys

# プロジェクトルートをパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.db_models import User, Customer, AnalysisResult, Billing, OperationLog

def migrate_data():
    app = create_app()
    with app.app_context():
        print("Starting data migration from CSV to DB...")

        # 1. Users
        users_csv = os.path.join(project_root, 'data', 'users.csv')
        print(f"Checking for users.csv at: {users_csv}")
        if os.path.exists(users_csv):
            print("users.csv found. Reading...")
            with open(users_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    print(f"Processing user: {row.get('user_id')}")
                    if not db.session.get(User, row['user_id']):
                        user = User(
                            user_id=row['user_id'],
                            password_hash=row['password_hash'],
                            role=row.get('role', 'user'),
                            plan=row.get('plan', 'Basic'),
                            billing_type=row.get('billing_type', 'subscription'),
                            balance_enc=row.get('balance_enc', ''),
                            status=row.get('status', 'active'),
                            cancellation_date=row.get('cancellation_date'),
                            plan_change_count=int(row.get('plan_change_count', 0)),
                            last_plan_change_date=row.get('last_plan_change_date'),
                            data_retention_until=row.get('data_retention_until'),
                            created_at=row.get('created_at')
                        )
                        db.session.add(user)
                        count += 1
                db.session.commit()
                print(f"Migrated {count} users.")

        # 2. Customers
        customers_csv = os.path.join(project_root, 'data', 'customers.csv')
        if os.path.exists(customers_csv):
            with open(customers_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if not Customer.query.get(row['customer_id']):
                        customer = Customer(
                            customer_id=row['customer_id'],
                            user_id=row['user_id'],
                            name_enc=row.get('name_enc', ''),
                            address_enc=row.get('address_enc', ''),
                            phone_enc=row.get('phone_enc', ''),
                            email_enc=row.get('email_enc', ''),
                            created_at=row.get('created_at')
                        )
                        db.session.add(customer)
                        count += 1
                db.session.commit()
                print(f"Migrated {count} customers.")

        # 3. Analysis Results
        analysis_csv = os.path.join(project_root, 'data', 'analysis_results.csv')
        if os.path.exists(analysis_csv):
            with open(analysis_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if not AnalysisResult.query.get(row['result_id']):
                        ar = AnalysisResult(
                            result_id=row['result_id'],
                            customer_id=row['customer_id'],
                            analysis_date=row.get('analysis_date'),
                            accuracy_score=float(row.get('accuracy_score', 0.0)),
                            attribute_json_enc=row.get('attribute_json_enc', ''),
                            status=row.get('status', 'completed')
                        )
                        db.session.add(ar)
                        count += 1
                db.session.commit()
                print(f"Migrated {count} analysis results.")

        # 4. Billing
        billing_csv = os.path.join(project_root, 'data', 'billing.csv')
        if os.path.exists(billing_csv):
            with open(billing_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if not Billing.query.get(row['billing_id']):
                        b = Billing(
                            billing_id=row['billing_id'],
                            user_id=row['user_id'],
                            billing_period=row.get('billing_period'),
                            plan=row.get('plan'),
                            base_fee=float(row.get('base_fee', 0.0)),
                            usage_fee=float(row.get('usage_fee', 0.0)),
                            total_fee=float(row.get('total_fee', 0.0)),
                            details=row.get('details', ''),
                            created_at=row.get('created_at')
                        )
                        db.session.add(b)
                        count += 1
                db.session.commit()
                print(f"Migrated {count} billings.")

        # 5. Logs
        logs_csv = os.path.join(project_root, 'data', 'logs.csv')
        if os.path.exists(logs_csv):
            with open(logs_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if not OperationLog.query.get(row['log_id']):
                        log = OperationLog(
                            log_id=row['log_id'],
                            user_id=row['user_id'],
                            operation=row.get('operation'),
                            target_id=row.get('target_id'),
                            details=row.get('details'),
                            created_at=row.get('created_at')
                        )
                        db.session.add(log)
                        count += 1
                db.session.commit()
                print(f"Migrated {count} operation logs.")

        print("Migration process completed.")

if __name__ == '__main__':
    migrate_data()
