from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import date



@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


#from monyy import app
from monyy import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monyy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    pass_hash = db.Column(db.String(150), nullable=False)
    accounts = db.relationship('Account', backref=db.backref('User', uselist=False))

    def get_id(self):
        return int(self.user_id)

    def get_username(self):
        return str(self.user_name)

    def __repr__(self):
        return '<User %r>' % self.user_name

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False)
    account_name = db.Column(db.String(80), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)
    transactions = db.relationship('Transaction', backref=db.backref('Account', uselist=True))
    account_tags = db.relationship('Account_tag', backref=db.backref('Account', uselist=True))
    debts = db.relationship('Debt', backref=db.backref('Account', uselist=True))
    def __repr__(self):
        return '<Account %r>' % self.account_name
    
class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.account_id))
    transaction_type = db.Column(db.String(30), nullable=False)
    transaction_value = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today())
    # transaction_time = db.Column(db.Time, nullable=False)
    transaction_note = db.Column(db.String(80))
    transactions_ba = db.relationship('Transaction_bank_account', backref=db.backref('Transaction', uselist=True))
    transactions_re = db.relationship('Transaction_real_estate', backref=db.backref('Transaction', uselist=True))
    transactions_bond = db.relationship('Transaction_bond', backref=db.backref('Transaction', uselist=True))
    transactions_stock = db.relationship('Transaction_stock', backref=db.backref('Transaction', uselist=True))
    transactions_debt = db.relationship('Transaction_debt', backref=db.backref('Transaction', uselist=True))
    transaction_tags = db.relationship('Transaction_tag', backref=db.backref('Transaction', uselist=True))
    def __repr__(self):
        return '<Transaction %r>' % self.transaction_type
    

class Bank_account(db.Model):
    bank_account_id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(80), nullable=False)
    account_digits = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    interest_period = db.Column(db.String(30), nullable = False)
    transactions_ba = db.relationship('Transaction_bank_account', backref=db.backref('Bank_account', uselist=False))
    def __repr__(self):
        return '<Bank Account %r>' % self.bank_name + " " + self.account_digits

class Transaction_bank_account(db.Model):
    transaction_ba_id =  db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id))
    bank_account_id = db.Column(db.Integer, db.ForeignKey(Bank_account.bank_account_id))


class Debt(db.Model):
    debt_id = db.Column(db.Integer, primary_key=True)
    lender = db.Column(db.String(80), nullable=False)
    principal = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    interest_period = db.Column(db.String(30), nullable = False)
    payment_account = db.Column(db.Integer, db.ForeignKey(Account.account_id))
    payment_date = db.Column(db.String(30), nullable=True)
    transactions_debt = db.relationship('Transaction_debt', backref=db.backref('Debt', uselist=False))
    def __repr__(self):
        return '<Debt %r>' % self.lender

class Transaction_debt(db.Model):
    transaction_debt_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    debt_id = db.Column(db.Integer, db.ForeignKey('debt.debt_id'))
    

class Real_estate(db.Model):
    real_estate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    original_value = db.Column(db.Integer, nullable=False)
    estimated_value = db.Column(db.Integer, nullable=False)
    transactions_re = db.relationship('Transaction_real_estate', backref=db.backref('Real_estate', uselist=False))
    def __repr__(self):
        return '<Real Estate %r>' % self.name

class Transaction_real_estate(db.Model):
    transaction_re_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id))
    real_estate_id = db.Column(db.Integer, db.ForeignKey(Real_estate.real_estate_id))


class Bond(db.Model):
    bond_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    maturation_date = db.Column(db.Date, nullable=False)
    transactions_bond = db.relationship('Transaction_bond', backref=db.backref('Bond', uselist=False))
    def __repr__(self):
        return '<Bond %r>' % self.name

class Transaction_bond(db.Model):
    transaction_bond_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id))
    bond_id = db.Column(db.Integer, db.ForeignKey(Bond.bond_id))
    

class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(6), nullable=False)
    exchange = db.Column(db.String(80), nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False)
    transactions_stock = db.relationship('Transaction_stock', backref=db.backref('Stock', uselist=False))
    stock_ids = db.relationship('Stock_value', backref=db.backref('Stock', uselist=True))
    def __repr__(self):
        return '<Stock %r>' % self.symbol

class Stock_value(db.Model):
    stock_value_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey(Stock.stock_id))
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Integer, nullable=False)

class Transaction_stock(db.Model):
    transaction_stock_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id))
    stock_id = db.Column(db.Integer, db.ForeignKey(Stock.stock_id))
    

class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), nullable=False)
    account_tags = db.relationship('Account_tag', backref=db.backref('Tag', uselist=True))
    transaction_tags = db.relationship('Transaction_tag', backref=db.backref('Tag', uselist=True))
    def __repr__(self):
        return '<Tag %r>' % self.tag_name

class Transaction_tag(db.Model):
    transaction_tag_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id))
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.tag_id))
    
class Account_tag(db.Model):
    account_tag_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.account_id))
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.tag_id))
    


def database_test():
    #Test 1: Add and retrieve values from each table
    user_test = User(user_name='test', pass_hash='password')
    # print(User.query.filter_by(user_name='test').first())
    db.session.add(user_test)
    db.session.commit()
    # print(User.query.get(1))
    user_selected = User.query.filter_by(user_name='test').first()
    # print(user_selected.user_id)
    # print(user_selected.get_id())
    # print(user_selected.get_username())


    account_test = Account(user_id=user_selected.user_id, account_name='tester', account_type='Savings')
    # print(Account.query.filter_by(account_type='Savings').first())
    db.session.add(account_test)
    db.session.commit()
    account_test = Account(user_id=user_selected.user_id, account_name='tester2', account_type='Savings')
    # print(Account.query.filter_by(account_type='Savings').first())
    db.session.add(account_test)
    db.session.commit()  
    # print(Account.query.get(1))
    account_selected = Account.query.filter_by(account_type='Savings').first()
    # print(account_selected.account_name)
    # print(account_selected.user_id)
    # print(user_selected.accounts)
    # print(User.query.filter_by(user_id=user_selected.user_id).all())
    # print(Account.query.filter_by(user_id=user_selected.user_id).all())

    transaction_test = Transaction(account_id=account_selected.account_id, transaction_type='Cash', transaction_value=50)
    # print(Transaction.query.filter_by(account_id=1).first())
    db.session.add(transaction_test)
    db.session.commit()
    transaction_test = Transaction(account_id=account_selected.account_id, transaction_type='Debt', transaction_value=50)
    # print(Transaction.query.filter_by(account_id=1).first())
    db.session.add(transaction_test)
    db.session.commit()
    transaction_test = Transaction(account_id=account_selected.account_id, transaction_type='Bond', transaction_value=50)
    # print(Transaction.query.filter_by(account_id=1).first())
    db.session.add(transaction_test)
    db.session.commit()
    transaction_test = Transaction(account_id=account_selected.account_id, transaction_type='Stock', transaction_value=50)
    # print(Transaction.query.filter_by(account_id=1).first())
    db.session.add(transaction_test)
    db.session.commit()
    transaction_test = Transaction(account_id=account_selected.account_id, transaction_type='Real Estate', transaction_value=50)
    # print(Transaction.query.filter_by(account_id=1).first())
    db.session.add(transaction_test)
    db.session.commit()
    # print(Transaction.query.filter_by(account_id=1).all())
    transaction_selected_stock = Transaction.query.filter_by(transaction_type='Stock').first()
    # print(transaction_selected_stock.account_id)
    transaction_selected_bond = Transaction.query.filter_by(transaction_type='Bond').first()
    # print(transaction_selected_bond.account_id)
    transaction_selected_cash = Transaction.query.filter_by(transaction_type='Cash').first()
    # print(transaction_selected_cash.account_id)
    transaction_selected_debt = Transaction.query.filter_by(transaction_type='Debt').first()
    # print(transaction_selected_debt.account_id)
    transaction_selected_re = Transaction.query.filter_by(transaction_type='Real Estate').first()
    # print(transaction_selected_re.account_id)
    



#db.drop_all()
db.create_all()
#db.session.query(Account).delete()
#db.session.query(User).delete()
#db.session.query(Transaction).delete()
#db.session.commit()
#database_test()
