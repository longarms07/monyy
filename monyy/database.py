from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
#from monyy import app
app = Flask("monyy")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monyy.db'
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    pass_hash = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return '<User %r>' % self.user_name

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))#, nullable=False)
    account_name = db.Column(db.String(80), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.account_name
    

class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'))
    transaction_type = db.Column(db.String(30), nullable=False)
    transaction_value = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_time = db.Column(db.Time, nullable=False)
    transaction_note = db.Column(db.String(80))

    def __repr__(self):
        return '<Transaction %r>' % self.transaction_type
    

class Bank_account(db.Model):
    bank_account_id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(80), nullable=False)
    account_digits = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    interest_period = db.Column(db.String(30), nullable = False)
    
    def __repr__(self):
        return '<Bank Account %r>' % self.bank_name + " " + self.account_digits


class Transaction_bank_account(db.Model):
    transaction_ba_id =  db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.bank_account_id'))

class Debt(db.Model):
    debt_id = db.Column(db.Integer, primary_key=True)
    lender = db.Column(db.String(80), nullable=False)
    principal = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    interest_period = db.Column(db.String(30), nullable = False)
    payment_account = db.Column(db.Integer, db.ForeignKey('account.account_id'))
    payment_date = db.Column(db.String(30), nullable=True)
    
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
    
    def __repr__(self):
        return '<Real Estate %r>' % self.name


class Transaction_real_estate(db.Model):
    transaction_re_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    real_estate_id = db.Column(db.Integer, db.ForeignKey('real_estate.real_estate_id'))


class Bond(db.Model):
    bond_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    maturation_date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return '<Bond %r>' % self.name

class Transaction_bond(db.Model):
    transaction_bond_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.bond_id'))
    

class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(6), nullable=False)
    exchange = db.Column(db.String(80), nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return '<Stock %r>' % self.symbol

class Stock_value(db.Model):
    stock_value_id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'))
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Integer, nullable=False)


class Transaction_stock(db.Model):
    transaction_stock_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'))
    


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), nullable=False)
    
    def __repr__(self):
        return '<Tag %r>' % self.tag_name


class Transaction_tag(db.Model):
    transaction_tag_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'))
    


class Account_tag(db.Model):
    account_tag_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'))
    




def database_test():
    #Test 1: Add and retrieve values from each table
    user_test = User(user_name='test', pass_hash='password')
    print(User.query.filter_by(user_name='test').first())
    db.session.add(user_test)
    db.session.commit()
    print(User.query.get(1))
    user_selected = User.query.filter_by(user_name='test').first()
    print(user_selected.user_id)

    # account_test = Account(account_name='tester', account_type='Savings')
    # print(Account.query.filter_by(account_type='Savings').first())
    # db.session.add(account_test)
    # db.session.commit() 
    # print(Account.query.get(1))
    # account_selected = Account.query.filter_by(account_type='Savings').first()
    # print(account_selected.account_name)


db.drop_all()
db.create_all()
db.session.query(User).delete()
# db.session.query(Account).delete()
db.session.commit()
database_test()