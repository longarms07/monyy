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
    #BondTest()
    #DebtTest()
    #REATest()
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


@app.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    cash = {}
    stocks = {}
    bonds = {}
    realestate = {}
    debts = {}
    baa = BankAccountAccessor()
    ba = BondAccessor()
    da = DebtAccessor()
    rea = RealEstateAccessor()
    try:
        #Bank Accounts
        bank_accounts = baa.getUserAccounts(current_user)
        for account in bank_accounts:
            #print(account)
            transactions = {}
            trans_list = baa.getTransactionsOnDate(current_user, account,10, date.today())
            #trans_list = baa.getAllTransactions(current_user, bank_accounts[count])
            ex_trans = trans_list[0]
            bank_name = str(ex_trans.Bank_account.bank_name)+" "+account.account_name+" (..."+str(ex_trans.Bank_account.account_digits)+")"
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
        #Bonds
        bond_accounts = ba.getUserAccounts(current_user)
        for account in bond_accounts:
            bond_transactions = ba.getAllTransactions(current_user, account)
            ex_trans = bond_transactions[0]
            bond_name = ex_trans.Bond.name 
            temp = {
                'maturity-date' : str(ex_trans.Bond.maturation_date),
                'amount' : ex_trans.Bond.value,
            }
            bonds[bond_name] = temp
        #print(bonds)
        bonds = json.dumps(bonds)
        #Real Estate
        re_accounts = rea.getUserAccounts(current_user)
        for account in re_accounts:
            re_trans = rea.getTransactionsOnDate(current_user, account, 1, date.today())
            re_name = account.account_name
            trans = re_trans[0]
            temp = {
                'original value' : trans.Real_estate.original_value,
                'estimated value' : trans.Real_estate.estimated_value
            }
            realestate[re_name] = temp
        realestate = json.dumps(realestate)
        #debts
        debt_accounts = da.getUserAccounts(current_user)
        for account in debt_accounts:
            debt_trans = da.getTransactionsOnDate(current_user, account, 10, date.today())
            ex_trans = debt_trans[0]
            debt_name = ex_trans.Debt.lender
            debt_balance = da.getBalance(current_user, account, ex_trans.Transaction)
            pay_date = ex_trans.Debt.payment_date
            pay_account = ex_trans.Debt.payment_account
            pay_account = Account.query.filter_by(user_id=current_user.user_id).filter_by(account_id = pay_account).first()
            if pay_account is None:
                pay_account_name = "Autopay is off, no account"
            else:
                pay_account_name = pay_account.account_name
            if pay_date is None:
                pay_date = "Autopay is off, "
                pay_account_name = "Autopay is off, no account"
            temp = {
                'principal' : ex_trans.Debt.principal,
                'interest' : ex_trans.Debt.interest_rate,
                'period' : ex_trans.Debt.interest_period,
                'payment date' : pay_date,
                'account associated' : pay_account_name,
                'balance' : debt_balance,
            }
            debt[debt_name] = temp
        debt = json.dumps(debt)


    except Exception as error:
        print(error)



    return render_template('index.html')

    @app.route("index/post", methods=['POST'])
    @login_required
    def addValues():
        
