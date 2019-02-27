from monyy import app, db
from .database import *
from .login import *
from .db_accessor import *
from flask import Flask, render_template, redirect
from flask_login import current_user, login_user, login_required, logout_user
from datetime import date
import json


@app.route("/")
def hello():
    db.drop_all()
    db.create_all()
    db.session.query(Account).delete()
    db.session.query(User).delete()
    db.session.query(Transaction).delete()
    db.session.query(Bank_account).delete()
    db.session.query(Transaction_bank_account).delete()
    db.session.query(Bond).delete()
    db.session.query(Transaction_bond).delete()
    db.session.query(Stock).delete()
    db.session.query(Stock_value).delete()
    db.session.query(Transaction_stock).delete()
    db.session.query(Debt).delete()
    db.session.query(Transaction_debt).delete()
    db.session.query(Real_estate).delete()
    db.session.query(Transaction_real_estate).delete()
    db.session.query(Transaction_tag).delete()
    db.session.query(Tag).delete()
    db.session.query(Account_tag).delete()
    db.session.commit()
    #BAATest()
    BondTest()
    #if current_user.is_authenticated:
    #    return "Hello "+current_user.get_username()+"!"
    #else:
    #    return "Hello mlemlem!"
    if current_user.is_authenticated:
        return redirect("/index")
    else:
        return redirect("/login")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = GetUser(form.username.data, form.password.data)
        except Exception as error:
            print(error)
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect("/index")
    return render_template('login.html', title='Sign In', form=form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        try:
            RegisterUser(form.username.data, form.password.data)
            user = GetUser(form.username.data, form.password.data)
        except Exception as error:
            print(error)
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect("/index")
    return render_template('login.html', title='Register', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/index")
@login_required
def index():
    cash = {}
    stocks = {}
    bonds = {}
    realestate = {}
    debts = {}
    baa = BankAccountAccessor()
    ba = BondAccessor()
    try:
        bank_accounts = baa.getUserAccounts(current_user)
        for account in bank_accounts:
            #print(account)
            transactions = {}
            trans_list = baa.getTransactionsOnDate(current_user, account,10, date.today())
            #trans_list = baa.getAllTransactions(current_user, bank_accounts[count])
            ex_trans = trans_list[0]
            bank_name = str(ex_trans.Bank_account.bank_name)+" (..."+str(ex_trans.Bank_account.account_digits)+")"
            count = 0
            for trans in trans_list:
                temp_balance = baa.getBalance(current_user, account, trans.Transaction)
                temp = {
                    'name' : trans.Transaction.transaction_note,
                    'date' : str(trans.Transaction.transaction_date),
                    'amount' : trans.Transaction.transaction_value,
                    'balance' : temp_balance,
                }
                id = "ID: "+str(count)
                count=count+1
                #transactions.update(id = temp)
                transactions[id] = temp
            #cash.update(bank_name= transactions)
            cash[bank_name] = transactions
        cash = json.dumps(cash)

    except Exception as error:
        print(error)












    return render_template('index.html')

