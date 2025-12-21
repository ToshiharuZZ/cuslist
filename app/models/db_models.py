"""
Database Models definitions using SQLAlchemy.
"""
from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    plan = db.Column(db.String(20), default='Basic')
    billing_type = db.Column(db.String(20), default='subscription')
    balance_enc = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    cancellation_date = db.Column(db.String(50))
    plan_change_count = db.Column(db.Integer, default=0)
    last_plan_change_date = db.Column(db.String(50))
    data_retention_until = db.Column(db.String(50))
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    # Relationships
    customers = db.relationship('Customer', backref='owner', lazy=True)
    logs = db.relationship('OperationLog', backref='user', lazy=True)
    billings = db.relationship('Billing', backref='user', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    name_enc = db.Column(db.Text)
    address_enc = db.Column(db.Text)
    phone_enc = db.Column(db.Text)
    email_enc = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    # Relationships
    analysis_results = db.relationship('AnalysisResult', backref='customer', lazy=True)

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    result_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'), nullable=False)
    analysis_date = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    accuracy_score = db.Column(db.Float, default=0.0)
    attribute_json_enc = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')

class Billing(db.Model):
    __tablename__ = 'billings'
    billing_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    billing_period = db.Column(db.String(7))  # YYYY-MM
    plan = db.Column(db.String(20))
    base_fee = db.Column(db.Float, default=0.0)
    usage_fee = db.Column(db.Float, default=0.0)
    total_fee = db.Column(db.Float, default=0.0)
    details = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    log_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    operation = db.Column(db.String(50))
    target_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PlanChangeHistory(db.Model):
    __tablename__ = 'plan_change_histories'
    history_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    change_type = db.Column(db.String(20))
    old_plan = db.Column(db.String(20))
    new_plan = db.Column(db.String(20))
    old_billing_type = db.Column(db.String(20))
    new_billing_type = db.Column(db.String(20))
    change_reason = db.Column(db.Text)
    changed_by = db.Column(db.String(50))
    prorated_amount = db.Column(db.Float, default=0.0)
    effective_date = db.Column(db.String(50))
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class CancellationHistory(db.Model):
    __tablename__ = 'cancellation_histories'
    cancellation_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    cancellation_type = db.Column(db.String(20))
    cancellation_reason = db.Column(db.Text)
    cancellation_comment = db.Column(db.Text)
    cancelled_by = db.Column(db.String(50))
    is_forced = db.Column(db.Boolean, default=False)
    plan_at_cancellation = db.Column(db.String(20))
    requested_date = db.Column(db.String(50))
    effective_date = db.Column(db.String(50))
    data_retention_until = db.Column(db.String(50))
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 他のモデルにも同様に to_dict を追加
User.to_dict = lambda self: {c.name: getattr(self, c.name) for c in self.__table__.columns}
Customer.to_dict = lambda self: {c.name: getattr(self, c.name) for c in self.__table__.columns}
AnalysisResult.to_dict = lambda self: {c.name: getattr(self, c.name) for c in self.__table__.columns}
Billing.to_dict = lambda self: {c.name: getattr(self, c.name) for c in self.__table__.columns}
