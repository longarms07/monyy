from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import date
from monyy import app, db



class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, unique=True, nullable=False)
    pass_hash = db.Column(db.String, nullable=False)
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
    account_name = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String, nullable=False)
    transactions = db.relationship('Transaction', backref=db.backref('Account', uselist=True))
    account_tags = db.relationship('Account_tag', backref=db.backref('Account', uselist=True))
    debts = db.relationship('Debt', backref=db.backref('Account', uselist=True))
    def __repr__(self):
        return '<Account %r>' % self.account_name
    
class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.account_id), nullable=False)
    transaction_type = db.Column(db.String, nullable=False)
    transaction_value = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today())
    # transaction_time = db.Column(db.Time, nullable=False)
    transaction_note = db.Column(db.String)
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
    bank_name = db.Column(db.String, nullable=False)
    account_digits = db.Column(db.String, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=True)
    interest_period = db.Column(db.String, nullable = True)
    transactions_ba = db.relationship('Transaction_bank_account', backref=db.backref('Bank_account', uselist=False))
    def __repr__(self):
        return '<Bank Account %r %r>' % (self.bank_name, self.account_digits)

class Transaction_bank_account(db.Model):
    transaction_ba_id =  db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey(Bank_account.bank_account_id), nullable=False)


class Debt(db.Model):
    debt_id = db.Column(db.Integer, primary_key=True)
    lender = db.Column(db.String, nullable=False)
    principal = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=True)
    interest_period = db.Column(db.String, nullable = True)
    payment_account = db.Column(db.Integer, db.ForeignKey(Account.account_id), nullable=False)
    payment_date = db.Column(db.String, nullable=True)
    transactions_debt = db.relationship('Transaction_debt', backref=db.backref('Debt', uselist=False))
    def __repr__(self):
        return '<Debt %r>' % self.lender

class Transaction_debt(db.Model):
    transaction_debt_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'), nullable=False)
    debt_id = db.Column(db.Integer, db.ForeignKey('debt.debt_id'), nullable=False)
    

class Real_estate(db.Model):
    real_estate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    original_value = db.Column(db.Float, nullable=False)
    estimated_value = db.Column(db.Float, nullable=False)
    transactions_re = db.relationship('Transaction_real_estate', backref=db.backref('Real_estate', uselist=False))
    def __repr__(self):
        return '<Real Estate %r>' % self.name

class Transaction_real_estate(db.Model):
    transaction_re_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id), nullable=False)
    real_estate_id = db.Column(db.Integer, db.ForeignKey(Real_estate.real_estate_id), nullable=False)


class Bond(db.Model):
    bond_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    value = db.Column(db.Float, nullable=False)
    maturation_date = db.Column(db.Date, nullable=False, default=date.today())
    transactions_bond = db.relationship('Transaction_bond', backref=db.backref('Bond', uselist=False))
    def __repr__(self):
        return '<Bond %r>' % self.name

class Transaction_bond(db.Model):
    transaction_bond_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id), nullable=False)
    bond_id = db.Column(db.Integer, db.ForeignKey(Bond.bond_id), nullable=False)
    

class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String, nullable=False)
    exchange = db.Column(db.String, nullable=False)
    num_stocks = db.Column(db.Integer, nullable=False) #Starting number of stocks
    transactions_stock = db.relationship('Transaction_stock', backref=db.backref('Stock', uselist=False))
    stock_ids = db.relationship('Stock_value', backref=db.backref('Stock', uselist=True))
    def __repr__(self):
        return '<Stock %r>' % self.symbol

class Stock_value(db.Model):
    stock_value_id = db.Column(db.Float, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey(Stock.stock_id), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today())
    value = db.Column(db.Integer, nullable=False)

class Transaction_stock(db.Model):
    transaction_stock_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey(Stock.stock_id), nullable=False)
    

class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String, unique=True, nullable=False)
    account_tags = db.relationship('Account_tag', backref=db.backref('Tag', uselist=True))
    transaction_tags = db.relationship('Transaction_tag', backref=db.backref('Tag', uselist=True))
    def __repr__(self):
        return '<Tag %r>' % self.tag_name

class Transaction_tag(db.Model):
    transaction_tag_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey(Transaction.transaction_id), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.tag_id), nullable=False)
    
class Account_tag(db.Model):
    account_tag_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.account_id), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey(Tag.tag_id), nullable=False)
    


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
    

    bank_account_test = Bank_account(bank_name='USAA',account_digits='1234')
    # print(Bank_account.query.filter_by(bank_name='USAA').first())
    db.session.add(bank_account_test)
    db.session.commit()
    # print(Bank_account.query.get(1))
    bank_account_selected = Bank_account.query.filter_by(bank_name='USAA').first()
    # print(bank_account_selected.bank_name)
    
    bank_account_trans_test = Transaction_bank_account(transaction_id = transaction_selected_cash.transaction_id, bank_account_id= bank_account_selected.bank_account_id)
    # print(Transaction_bank_account.query.filter_by(bank_account_id=1).first())
    db.session.add(bank_account_trans_test)
    db.session.commit()
    # print(Transaction_bank_account.query.get(1))
    bank_account_trans_selected = Transaction_bank_account.query.filter_by(bank_account_id=1).first()
    # print(bank_account_trans_selected.bank_account_id)


    #bond
    bond_test = Bond(name='ex Bond',value=50,maturation_date=date(2020,6,20))
    # print(Bond.query.filter_by(name='ex Bond').first())
    db.session.add(bond_test)
    db.session.commit()
    # print(Bond.query.get(1))
    bond_selected = Bond.query.filter_by(name='ex Bond').first()
    # print(bond_selected.maturation_date)
    
    bond_trans_test = Transaction_bond(transaction_id = transaction_selected_bond.transaction_id, bond_id= bond_selected.bond_id)
    # print(Transaction_bond.query.filter_by(bond_id=1).first())
    db.session.add(bond_trans_test)
    db.session.commit()
    # print(Transaction_bond.query.get(1))
    bond_trans_selected = Transaction_bond.query.filter_by(bond_id=1).first()
    # print(bond_trans_selected.bond_id)


    #stock
    stock_test = Stock(symbol='DIS',exchange='Dow Jones',num_stocks=500)
    # print(Stock.query.filter_by(exchange='Dow Jones').first())
    db.session.add(stock_test)
    db.session.commit()
    # print(Stock.query.get(1))
    stock_selected = Stock.query.filter_by(exchange='Dow Jones').first()
    # print(stock_selected.num_stocks)

    stock_value_test = Stock_value(stock_id=stock_selected.stock_id, value=5)
    # print(Stock_value.query.filter_by(stock_id=1).first())
    db.session.add(stock_value_test)
    db.session.commit()
    # print(Stock_value.query.get(1))
    stock_value_selected = Stock_value.query.filter_by(stock_id=1).first()
    # print(stock_value_selected.date)
    
    stock_trans_test = Transaction_stock(transaction_id = transaction_selected_stock.transaction_id, stock_id= stock_selected.stock_id)
    # print(Transaction_stock.query.filter_by(stock_id=1).first())
    db.session.add(stock_trans_test)
    db.session.commit()
    # print(Transaction_stock.query.get(1))
    stock_trans_selected = Transaction_stock.query.filter_by(stock_id=1).first()
    # print(stock_trans_selected.stock_id)


    #real estate

    real_estate_test = Real_estate(name='House',original_value=0,estimated_value=2)
    # print(Real_estate.query.filter_by(name='House').first())
    db.session.add(real_estate_test )
    db.session.commit()
    # print(Real_estate.query.get(1))
    real_estate_selected = Real_estate.query.filter_by(name='House').first()
    # print(real_estate_selected.name)
    
    re_trans_test = Transaction_real_estate(transaction_id = transaction_selected_re.transaction_id, real_estate_id= real_estate_selected.real_estate_id)
    # print(Transaction_real_estate.query.filter_by(real_estate_id=1).first())
    db.session.add(re_trans_test)
    db.session.commit()
    # print(Transaction_real_estate.query.get(1))
    re_trans_selected = Transaction_real_estate.query.filter_by(real_estate_id=1).first()
    # print(re_trans_selected.real_estate_id)


    #debt
    debt_test = Debt(lender='Jersey Boys',principal=60,interest_rate=2,interest_period='Month',payment_account=account_selected.account_id, payment_date='Weekly')
    # print(Debt.query.filter_by(lender='Jersey Boys').first())
    db.session.add(debt_test)
    db.session.commit()
    # print(Debt.query.get(1))
    debt_selected = Debt.query.filter_by(lender='Jersey Boys').first()
    # print(debt_selected.principal)
    
    debt_trans_test = Transaction_debt(transaction_id = transaction_selected_debt.transaction_id, debt_id= debt_selected.debt_id)
    # print(Transaction_debt.query.filter_by(debt_id=1).first())
    db.session.add(debt_trans_test)
    db.session.commit()
    # print(Transaction_debt.query.get(1))
    debt_trans_selected = Transaction_debt.query.filter_by(debt_id=1).first()
    # print(debt_trans_selected.debt_id)

    test_tag = Tag(tag_name='internal')
    print(Tag.query.filter_by(tag_name='internal').first())
    db.session.add(test_tag)
    db.session.commit()
    test_tag = Tag(tag_name='personal')
    db.session.add(test_tag)
    db.session.commit()
    #print(Tag.query.get(1))
    tag_selected = Tag.query.filter_by(tag_name='internal').first()
    tag_selected_two = Tag.query.filter_by(tag_name='personal').first()
    #print(tag_selected.tag_name)

    test_trans_tag = Transaction_tag(transaction_id=transaction_selected_cash.transaction_id,tag_id=tag_selected.tag_id)
    #print(Transaction_tag.query.filter_by(tag_id=1).first())
    db.session.add(test_trans_tag)
    db.session.commit()
    #print(Transaction_tag.query.get(1))
    tag_trans_selected = Transaction_tag.query.filter_by(tag_id=1).first()
    #print(tag_trans_selected.transaction_id)

    account_tag_test = Account_tag(account_id = account_selected.account_id, tag_id = tag_selected_two.tag_id)
    #print(Account_tag.query.filter_by(account_id=1).first())
    db.session.add(account_tag_test)
    db.session.commit()
    #print(Account_tag.query.get(1))
    tag_account_selected = Account_tag.query.filter_by(account_id=1).first()
    #print(tag_account_selected.account_id)

    join_test = db.session.query(Account, Transaction, Transaction_bank_account).filter_by(account_id=account_selected.account_id).join(Transaction).join(Transaction_bank_account).first()
    #print(join_test)
    #print(join_test.Transaction.transaction_id)
    sum_test = db.session.query(func.sum(Transaction.transaction_value).label('balance')).filter_by(transaction_type='Cash').first()
    sum_test = db.session.query(func.sum(Transaction.transaction_value).label('balance')).filter(Transaction.transaction_id<=12).first()
    #print(sum_test.balance)



#database_test()