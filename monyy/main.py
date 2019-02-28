from monyy import app
from .database import *
from .login import *
# from .db_accessor import *
from flask import Flask, render_template, redirect, request
from flask_login import current_user, login_user, login_required, logout_user
from datetime import date
import json

# @app.route("/")
# def hello():
#     # db.drop_all()
#     # db.create_all()
#     # db.session.query(Account).delete()
#     # db.session.query(User).delete()
#     # db.session.query(Transaction).delete()
#     # db.session.query(Bank_account).delete()
#     # db.session.query(Transaction_bank_account).delete()
#     # db.session.query(Bond).delete()
#     # db.session.query(Transaction_bond).delete()
#     # db.session.query(Stock).delete()
#     # db.session.query(Stock_value).delete()
#     # db.session.query(Transaction_stock).delete()
#     # db.session.query(Debt).delete()
#     # db.session.query(Transaction_debt).delete()
#     # db.session.query(Real_estate).delete()
#     # db.session.query(Transaction_real_estate).delete()
#     # db.session.query(Transaction_tag).delete()
#     # db.session.query(Tag).delete()
#     # db.session.query(Account_tag).delete()
#     # db.session.commit()
#     #BAATest()
#     #BondTest()
#     #DebtTest()
#     #REATest()
#     if current_user.is_authenticated:
#         return redirect("/index")
#     else:
#         return redirect("/login")




# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect("/index")
#     form = LoginForm()
#     if form.validate_on_submit():
#         try:
#             user = GetUser(form.username.data, form.password.data)
#         except Exception as error:
#             print(error)
#             return redirect("/login")
#         login_user(user, remember=form.remember_me.data)
#         return redirect("/index")
#     return render_template('login.html', title='Sign In', form=form)

# @app.route("/register", methods = ['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect("/index")
#     form = LoginForm()
#     if form.validate_on_submit():
#         try:
#             RegisterUser(form.username.data, form.password.data)
#             user = GetUser(form.username.data, form.password.data)
#         except Exception as error:
#             print(error)
#             return redirect("/login")
#         login_user(user, remember=form.remember_me.data)
#         return redirect("/index")
#     return render_template('login.html', title='Register', form=form)

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect("/login")

@app.route("/", methods=['GET', 'POST'])
# @login_required
def index():
    cash = {}
    stocks = {}
    bonds = {}
    realestate = {}
    debts = {}
    # baa = BankAccountAccessor()
    # ba = BondAccessor()
    # da = DebtAccessor()
    # rea = RealEstateAccessor()
    # try:
    #     #Bank Accounts
    #     bank_accounts = baa.getUserAccounts(current_user)
    #     for account in bank_accounts:
    #         #print(account)
    #         transactions = {}
    #         trans_list = baa.getTransactionsOnDate(current_user, account,10, date.today())
    #         #trans_list = baa.getAllTransactions(current_user, bank_accounts[count])
    #         ex_trans = trans_list[0]
    #         bank_name = str(ex_trans.Bank_account.bank_name)+" "+account.account_name+" (..."+str(ex_trans.Bank_account.account_digits)+")"
    #         count = 0
    #         for trans in trans_list:
    #             temp_balance = baa.getBalance(current_user, account, trans.Transaction)
    #             temp = {
    #                 'name' : trans.Transaction.transaction_note,
    #                 'date' : str(trans.Transaction.transaction_date),
    #                 'amount' : trans.Transaction.transaction_value,
    #                 'balance' : temp_balance,
    #             }
    #             id = "ID: "+str(count)
    #             count=count+1
    #             #transactions.update(id = temp)
    #             transactions[id] = temp
    #         #cash.update(bank_name= transactions)
    #         cash[bank_name] = transactions
    # except: 
    #     transactions = {}
    #     temp = {
    #                 'name' : "No account",
    #                 'date' : "No account",
    #                 'amount' : "No account",
    #                 'balance' : "No account",
    #             }
    #     transactions['None'] = temp
    #     cash['No_Account'] = transactions
    # try:
    #     #Bonds
    #     bond_accounts = ba.getUserAccounts(current_user)
    #     for account in bond_accounts:
    #         bond_transactions = ba.getAllTransactions(current_user, account)
    #         ex_trans = bond_transactions[0]
    #         bond_name = ex_trans.Bond.name 
    #         temp = {
    #             'maturity-date' : str(ex_trans.Bond.maturation_date),
    #             'amount' : ex_trans.Bond.value,
    #         }
    #         bonds[bond_name] = temp
    #     #print(bonds)
    # except:
    #     temp = {
    #             'maturity-date' : '',
    #             'amount' : '',
    #         }
    #     bonds['none'] = temp
    # try:
    #     #Real Estate
    #     re_accounts = rea.getUserAccounts(current_user)
    #     for account in re_accounts:
    #         re_trans = rea.getTransactionsOnDate(current_user, account, 1, date.today())
    #         re_name = account.account_name
    #         trans = re_trans[0]
    #         temp = {
    #             'original value' : trans.Real_estate.original_value,
    #             'estimated value' : trans.Real_estate.estimated_value
    #         }
    #         realestate[re_name] = temp
    # except:
    #     temp = {
    #             'original value' : '',
    #             'estimated value' : '',
    #     }
    #     realestate['none'] = temp
        
    # try:
    #     #debts
    #     debt_accounts = da.getUserAccounts(current_user)
    #     for account in debt_accounts:
    #         debt_trans = da.getTransactionsOnDate(current_user, account, 10, date.today())
    #         ex_trans = debt_trans[0]
    #         debt_name = ex_trans.Debt.lender
    #         debt_balance = da.getBalance(current_user, account, ex_trans.Transaction)
    #         pay_date = ex_trans.Debt.payment_date
    #         pay_account = ex_trans.Debt.payment_account
    #         pay_account = Account.query.filter_by(user_id=current_user.user_id).filter_by(account_id = pay_account).first()
    #         if pay_account is None:
    #             pay_account_name = "Autopay is off, no account"
    #         else:
    #             pay_account_name = pay_account.account_name
    #         if pay_date is None:
    #             pay_date = "Autopay is off, "
    #             pay_account_name = "Autopay is off, no account"
    #         temp = {
    #             'principal' : ex_trans.Debt.principal,
    #             'interest' : ex_trans.Debt.interest_rate,
    #             'period' : ex_trans.Debt.interest_period,
    #             'payment date' : pay_date,
    #             'account associated' : pay_account_name,
    #             'balance' : debt_balance,
    #         }
    #         debts[debt_name] = temp
    # except:
    #     temp = {
    #             'principal' : '',
    #             'interest' : '',
    #             'period' : '',
    #             'payment date' : '',
    #             'account associated' : '',
    #             'balance' : '',
    #         }
    #     debts['none'] = temp
    # try:
    #     raise Exception("Implement stocks Erik!")
    # except Exception as error:
    #     print(error)

    name = 'TestUser'
    rampcount = 15
    networth = 532789236
    cash = {}
    cash = {
                'acct1' : { 'ID0' : {
                                        'name' : 'Walmart 1',
                                        'date' : '2/14/2019',
                                        'amount' : 54.21,
                                        'balance' : 3000.77
                                    },
                            'ID1' : {
                                        'name' : 'The nice men in NJ 1',
                                        'date' : '2/12/2019',
                                        'amount' : 2278.98,
                                        'balance' : 34307.98
                                    },
                            'ID2' : {
                                        'name' : 'Deposit 1',
                                        'date' : '2/06/2019',
                                        'amount' : 4000.00,
                                        'balance': 36586.96
                            }
                },
                                
                'acct2' : { 'ID0' : {
                                        'name' : 'Walmart 2',
                                        'date' : '2/14/2019',
                                        'amount' : 54.21,
                                        'balance' : 5000.77
                                    },
                            'ID1' : {
                                        'name' : 'The nice men in NJ 2',
                                        'date' : '2/12/2019',
                                        'amount' : 2278.98,
                                        'balance' : 34307.98
                                    },
                            'ID2' : {
                                        'name' : 'Deposit 2',
                                        'date' : '2/06/2019',
                                        'amount' : 4000.00,
                                        'balance': 36586.96
                            },
                },
                'acct3' : { 'ID0' : {
                                        'name' : 'Walmart 3',
                                        'date' : '2/14/2019',
                                        'amount' : 54.21,
                                        'balance' : 34253.77
                                    },
                            'ID1' : {
                                        'name' : 'The nice men in NJ 3',
                                        'date' : '2/12/2019',
                                        'amount' : 2278.98,
                                        'balance' : 34307.98
                                    },
                            'ID2' : {
                                        'name' : 'Deposit 3',
                                        'date' : '2/06/2019',
                                        'amount' : 4000.00,
                                        'balance': 36586.96
                            }
                },
                'acct4' : { 'ID0' : {
                                        'name' : 'Walmart 4',
                                        'date' : '2/14/2019',
                                        'amount' : 54.21,
                                        'balance' : 34253.77
                                    },
                            'ID1' : {
                                        'name' : 'The nice men in NJ 4',
                                        'date' : '2/12/2019',
                                        'amount' : 2278.98,
                                        'balance' : 34307.98
                                    },
                            'ID2' : {
                                        'name' : 'Deposit 4',
                                        'date' : '2/06/2019',
                                        'amount' : 4000.00,
                                        'balance': 36586.96
                            }
                }
    }

                # ... retrieve all
    stocks = {
                'stock1' : {
                                'num_shares' : 1,
                                'cost_per_share' : 2.45,
                                'total_value' : 45768987,
                                'closing_values' : {
                                                        'date1' : 432.15,
                                                        'date2' : 543.26,
                                                        'date3' : 123.56,
                                                        'date4' : 432.67,
                                                        'date5' : 657.23,
                                                        'date6' : 7486.32,
                                                        'date7' : 4326.34,
                                                        'date8' : 4326.34,
                                                        'date9' : 4326.34,
                                                        'date10' : 4326.34,
                                                        'date11' : 4326.34,
                                                        'date12' : 4326.34,
                                                        'date13' : 4326.34,
                                                        'date14' : 4326.34
                                }
                            },
                'stock2' : {
                                'num_shares' : 2,
                                'cost_per_share' : 2.45,
                                'total_value' : 45768987,
                                'closing_values' : {
                                                        'date1' : 432.15,
                                                        'date2' : 543.26,
                                                        'date3' : 123.56,
                                                        'date4' : 432.67,
                                                        'date5' : 657.23,
                                                        'date6' : 7486.32,
                                                        'date7' : 4326.34,
                                                        'date8' : 4326.34,
                                                        'date9' : 4326.34,
                                                        'date10' : 4326.34,
                                                        'date11' : 4326.34,
                                                        'date12' : 4326.34,
                                                        'date13' : 4326.34,
                                                        'date14' : 4326.34
                                }
                            },
                'stock3' : {
                                'num_shares' : 3,
                                'cost_per_share' : 2.45,
                                'total_value' : 45768987,
                                'closing_values' : {
                                                        'date1' : 432.15,
                                                        'date2' : 543.26,
                                                        'date3' : 123.56,
                                                        'date4' : 432.67,
                                                        'date5' : 657.23,
                                                        'date6' : 7486.32,
                                                        'date7' : 4326.34,
                                                        'date8' : 4326.34,
                                                        'date9' : 4326.34,
                                                        'date10' : 4326.34,
                                                        'date11' : 4326.34,
                                                        'date12' : 4326.34,
                                                        'date13' : 4326.34,
                                                        'date14' : 4326.34
                                }
                            }
                # ... retrieve all
    }

    bonds = {
                'Bond1' : {
                            'maturity_date' : '2/14/2030',
                            'amount' : 1000.00
                },
                'Bond2' : {
                            'maturity_date' : '3/12/2021',
                            'amount' : 500.00
                },
                'Bond3' : {
                            'maturity_date' : '7/10/2025',
                            'amount' : 5000.00
                }
                # ... retrieve all
    }
    realestate = {
                    'add1' : {
                                'estimated_value' : 4382905,
                                'original_value' : 5438256
                             },
                    'add2' : {
                                'estimated_value' : 4637586,
                                'original_value' : 8658556
                             },
                    'add3' : {
                                'estimated_value' : 4876876,
                                'original_value' : 8769780
                             },
    }

    debts = {
                'debt1' : {
                                'remaining' : 145000,
                                'principal' : 240000,
                                'interest' : 12.5,
                                'period' : 'Monthly',
                                'payment date' : 'Some payment date',
                                'account associated' : 'Acct'

                          },
                'debt2' : {
                                'remaining'
                                'principal' : 240000,
                                'interest' : 12.5,
                                'period' : 'Monthly',
                                'payment_date' : 'Some payment date',
                                'account_associated' : 'Acct'

                          },
                'debt3' : {
                                'principal' : 240000,
                                'interest' : 12.5,
                                'period' : 'Monthly',
                                'payment_date' : 'Some payment date',
                                'account_associated' : 'Acct'

                          }
    }

    cash = json.dumps(cash)
    stocks = json.dumps(stocks)
    bonds = json.dumps(bonds)
    realestate = json.dumps(realestate)
    debts = json.dumps(debts)
    
    return render_template('index.html', 
                            username=name,
                            rampcount=rampcount,
                            networth=networth,
                            cash=cash,
                            stocks=stocks,
                            bonds=bonds,
                            realestate=realestate,
                            debts=debts
                            )




@app.route("/index/bank", methods=['POST'])
# @login_required
def addAcctVals():
    # baa = BankAccountAccessor()
    bank = request.add_cash['bank']
    acct_name = request.add_cash['acct-name']
    acct_num = request.add_cash['account']
    balance = request.add_cash['balance']
    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

    return redirect("/index")


@app.route("/index/banktrans", methods=['POST'])
# @login_required
def addTransVals():
    # baa = BankAccountAccessor()
    digits = request.add_trans['digits']
    name = request.add_trans['name']
    date = request.add_trans['date']
    amount = request.add_trans['amount']
    balance = request.add_trans['balance']

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
    # baa = BankAccountAccessor()
    symbol = request.add_stock['symbol']
    num_shares = request.add_stock['shares']
    init_price = request.add_stock['value']

    l = [symbol, num_shares, init_price]
    print(l)

    # try:
        #def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits)
    #     baa.makeAccount(current_user, acct_name, balance, bank, acct_num)
    # except Exception as error:
    #     print(error)

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