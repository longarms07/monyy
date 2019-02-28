from monyy import app, db
from .database import *
from .login import *
from .db_accessor import *
from flask import Flask, render_template, redirect, request
from flask_login import current_user, login_user, login_required, logout_user
from datetime import date
import json


@app.route("/")
def hello():
    # db.drop_all()
    # db.create_all()
    # db.session.query(Account).delete()
    # db.session.query(User).delete()
    # db.session.query(Transaction).delete()
    # db.session.query(Bank_account).delete()
    # db.session.query(Transaction_bank_account).delete()
    # db.session.query(Bond).delete()
    # db.session.query(Transaction_bond).delete()
    # db.session.query(Stock).delete()
    # #db.session.query(Stock_value).delete()
    # db.session.query(Transaction_stock).delete()
    # db.session.query(Debt).delete()
    # db.session.query(Transaction_debt).delete()
    # db.session.query(Real_estate).delete()
    # db.session.query(Transaction_real_estate).delete()
    # db.session.query(Transaction_tag).delete()
    # db.session.query(Tag).delete()
    # db.session.query(Account_tag).delete()
    # db.session.commit()
    # BAATest()
    # BondTest()
    # DebtTest()
    # REATest()
    # StockTest()
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
        return redirect("/index")
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
    sa = StockAccessor()
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
    except: 
        transactions = {}
        temp = {
                    'name' : "No account",
                    'date' : "No account",
                    'amount' : "No account",
                    'balance' : "No account",
                }
        transactions['None'] = temp
        cash['No_Account'] = transactions
    try:
        #Bonds
        bond_accounts = ba.getUserAccounts(current_user)
        for account in bond_accounts:
            bond_transactions = ba.getAllTransactions(current_user, account)
            ex_trans = bond_transactions[0]
            bond_name = ex_trans.Bond.name 
            temp = {
                'maturity_date' : str(ex_trans.Bond.maturation_date),
                'amount' : ex_trans.Bond.value,
            }
            bonds[bond_name] = temp
        #print(bonds)
    except:
        temp = {
                'maturity_date' : '',
                'amount' : '',
            }
        bonds['none'] = temp
    try:
        #Real Estate
        re_accounts = rea.getUserAccounts(current_user)
        for account in re_accounts:
            re_trans = rea.getTransactionsOnDate(current_user, account, 1, date.today())
            re_name = account.account_name
            trans = re_trans[0]
            temp = {
                'estimated_value' : trans.Real_estate.estimated_value,
                'original_value' : trans.Real_estate.original_value,
            }
            realestate[re_name] = temp
    except:
        temp = {
                'estimated_value' : '',
                'original_value' : '',
        }
        realestate['none'] = temp
        
    try:
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
                'remaining' : debt_balance,
                'principal' : ex_trans.Debt.principal,
                'interest' : ex_trans.Debt.interest_rate,
                'period' : ex_trans.Debt.interest_period,
                'payment_date' : str(pay_date),
                'account_associated' : pay_account_name,
            }
            debts[debt_name] = temp
    except:
        temp = {
                'remaining' : '',
                'principal' : '',
                'interest' : '',
                'period' : '',
                'payment_date' : '',
                'account_associated' : '',
            }
        debts['none'] = temp
    try:
        closing_vals={}
        stock_data = sa.getUserAccounts(current_user)
        for account in stock_data:
            trans_list = sa.getTransactions(current_user, account, 1)
            ex_trans = trans_list[0]
            on_day = 1
            closing_vals = {}
            cost_per_share = sa.getValue(ex_trans.Stock.stock_symbol)
            balance = sa.getBalance(current_user, account, ex_trans.Transaction, ex_trans.Stock.stock_symbol)
            num_shares = sa.getNumStocks(current_user, account, ex_trans.Transaction)
            start = datetime.now()
            while on_day <=14:
                #getValue(self, temp_stock, temp_datetime=datetime.today())
                #getNumStocks(self,temp_user, temp_account, temp_transaction, temp_datetime=datetime.today())
                #getBalance(self,temp_user, temp_account, temp_transaction, temp_stock, temp_datetime=datetime.today())
                day = end = start-timedelta(days=on_day)
                val = sa.getValue(ex_trans.Stock.stock_symbol, temp_datetime=end)
                closing_vals[end] = val
                on_day=on_day+1
            temp = {
                'num_shares' : num_shares,
                'cost_per_share' : cost_per_share,
                'total_value' : balance,
                'closing_values' : closing_vals
            }
            stocks[ex_trans.Stock.symbol] = temp
    except Exception as error:
        print(error)
        stocks = {

                'no_stocks' : {

                                'num_shares' : 0,

                                'cost_per_share' : 0,

                                'total_value' : 0,

                                'closing_values' : {

                                                        'date1' : 0,

                                                        'date2' : 0,

                                                        'date3' : 0,

                                                        'date4' : 0,

                                                        'date5' : 0,

                                                        'date6' : 0,

                                                        'date7' : 0,

                                                        'date8' : 0,

                                                        'date9' : 0,

                                                        'date10' : 0,

                                                        'date11' : 0,

                                                        'date12' : 0,

                                                        'date13' : 0,

                                                        'date14' : 0,

                                }

                            },
    }
    cash = json.dumps(cash)
    bonds = json.dumps(bonds)
    realestate = json.dumps(realestate)
    debts = json.dumps(debts)
    stocks = json.dumps(stocks)
    # print(cash)
    # print(bonds)
    # print(realestate)
    # print(debt)
    # print(stocks)
    return render_template('index.html', 
                            username = current_user.user_name,
                            cash=cash,
                            stocks=stocks,
                            bonds=bonds,
                            realestate=realestate,
                            debts=debts,
                            )

@app.route("/index/bank", methods=['POST'])
@login_required
def addAccValues():
    #jsdata = request.form['javascript_data']
    # jsdata = request.get_json()
    # values = json.loads(jsdata)[0]
    baa = BankAccountAccessor()
    bank = request.form['bank']
    acct_name = request.form['acct-name']
    acct_num = request.form['account']
    #balance = request.form['balance']
    #print(bank)
    #print(acct_name)
    #print(acct_num)
    #print(balance)
    try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
        baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    except Exception as error:
        print(error)

    return redirect("/index")
    
@app.route("/index/banktrans", methods=['POST'])
# @login_required
def addTransVals():
    baa = BankAccountAccessor()
    digits = request.form['digits']
    digits = str(digits)
    name = request.form['name']
    date = request.form['date']
    amount = request.form['amount']
    balance = request.form['balance']
    try:
        info = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account
                ).join(Transaction
                ).order_by(Transaction.transaction_id.desc()
                ).join(Transaction_bank_account
                ).join(Bank_account
                ).filter_by(account_digits = digits
                ).first()

        if info is None:
            raise Exception("Invalid account id!")
    except Exception as error:
        print(error)



    l = [name, date, amount, balance]
    print(l)

    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

    return redirect("/index")

@app.route("/index/stock", methods=['POST'])
# @login_required
def addStockVals():
    sa = StockAccessor()
    symbol = request.form['symbol']
    num_shares = request.form['shares']
    init_price = request.form['value']

    #l = [symbol, num_shares, init_price]
    #print(l)

    try:
        # makeAccount(self,temp_user, temp_name, temp_num_stocks, temp_stock_symbol, temp_exchange='NASDAQ', temp_datetime=datetime.now()):
        sa.makeAccount(current_user, symbol, num_shares, symbol)
    except Exception as error:
        print(error)

    return redirect("/index")

@app.route('/index/bond', methods=['POST'])
# @login_required
def addBondVals():
    # baa = BankAccountAccessor()
    name = request.add_bond['name']
    value = request.add_bond['value']
    mat_date = request.add_bond['date']

    l = [name, value, mat_date]
    print(l)

    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

    return redirect("/index")

@app.route('/index/estate', methods=['POST'])
# @login_required
def addEstateVals():
    # baa = BankAccountAccessor()
    name = request.add_estate['name']
    orig_value = request.add_estate['origvalue']
    est_value = request.add_estate['estvalue']

    l = [name, orig_value, est_value]
    print(l)

    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

    return redirect("/index")

@app.route('/index/debt', methods=['POST'])
# @login_required
def addDebtVals():
    # baa = BankAccountAccessor()
    name = request.add_debt['name']
    prin = request.add_debt['principal']
    inter = request.add_debt['interest']
    per = request.add_debt['period']

    l = [name, prin, inter, per]
    print(l)

    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

    return redirect("/index")


@app.route('/help')
def help():
    return render_template('help.html')

