from monyy import app
from .database import db, User
from .login import *
from flask import Flask, render_template, redirect
from flask_login import current_user, login_user, login_required, logout_user
import json

@app.route("/")
def hello():
    if current_user.is_authenticated:
        return "Hello "+current_user.get_username()+"!"
    else:
        cash = {}
        stocks = {}
        bonds = {}
        realestate = {}
        debts = {}

        '''
        for acct in cash_data:
            transactions = {}
            for transaction in acct:
                # get 10 most recent OR
                # get all transactions in last week or 2 weeks in DESCENDING ORDER BY DATE
                # pull balance from most recent transaction
                temp = { 
                            'name' : transaction.name
                            'date' : transaction.date
                            'amount' : transaction.amount
                            # balance is the balance after the transaction has taken place
                            'balance' : transaction.balance
                }
                transactions.update(transaction.ID = temp)
            cash.update(acct.name (or acct.number) = transactions)

        for stock in stock_data:
            # get last two weeks of closing stock values
            closing_vals = {}
            for closing_val in stock:
                closing_vals.update(closing_val.date = closing_val.value)
            stocks.update(stock.name = closing_vals)

        for bond in bond_data:
            temp = {
                        'maturity-date' : bond.date
                        'amount' : bond.amount
            }
            bonds.update(bond.name = temp)

        for estate in estate_data:
            temp = {
                        'original value' : estate_data.orig_value,
                        'estimated value' : estate_data.est_value
            }
            realestate.update(estate.address = temp)

        for debt in debt_data:
            temp = {
                        'principal' : debt.principal,
                        'interest' : debt.interest,
                        'period' : debt.period,
                        'payment date' : debt.payment-date,
                        'account associated' : debt.account
            }
            debts.update(debt.name = temp)
        '''

        
        name = 'TestUser'
        rampcount = 15
        networth = 532789236
        cash = {
                    'acct1' : { 'ID0' : {
                                            'name' : 'Walmart',
                                            'date' : '2/14/2019',
                                            'amount' : 54.21,
                                            'balance' : 3000.77
                                        },
                                'ID1' : {
                                            'name' : 'The nice men in NJ',
                                            'date' : '2/12/2019',
                                            'amount' : 2278.98,
                                            'balance' : 34307.98
                                        },
                                'ID2' : {
                                            'name' : 'Deposit',
                                            'date' : '2/06/2019',
                                            'amount' : 4000.00,
                                            'balance': 36586.96
                                }
                    },
                                    
                    'acct2' : { 'ID0' : {
                                            'name' : 'Walmart',
                                            'date' : '2/14/2019',
                                            'amount' : 54.21,
                                            'balance' : 5000.77
                                        },
                                'ID1' : {
                                            'name' : 'The nice men in NJ',
                                            'date' : '2/12/2019',
                                            'amount' : 2278.98,
                                            'balance' : 34307.98
                                        },
                                'ID2' : {
                                            'name' : 'Deposit',
                                            'date' : '2/06/2019',
                                            'amount' : 4000.00,
                                            'balance': 36586.96
                                },
                    },
                    'acct3' : { 'ID0' : {
                                            'name' : 'Walmart',
                                            'date' : '2/14/2019',
                                            'amount' : 54.21,
                                            'balance' : 34253.77
                                        },
                                'ID1' : {
                                            'name' : 'The nice men in NJ',
                                            'date' : '2/12/2019',
                                            'amount' : 2278.98,
                                            'balance' : 34307.98
                                        },
                                'ID2' : {
                                            'name' : 'Deposit',
                                            'date' : '2/06/2019',
                                            'amount' : 4000.00,
                                            'balance': 36586.96
                                }
                    },
                    'acct4' : { 'ID0' : {
                                            'name' : 'Walmart',
                                            'date' : '2/14/2019',
                                            'amount' : 54.21,
                                            'balance' : 34253.77
                                        },
                                'ID1' : {
                                            'name' : 'The nice men in NJ',
                                            'date' : '2/12/2019',
                                            'amount' : 2278.98,
                                            'balance' : 34307.98
                                        },
                                'ID2' : {
                                            'name' : 'Deposit',
                                            'date' : '2/06/2019',
                                            'amount' : 4000.00,
                                            'balance': 36586.96
                                }
                    }
        }

                    # ... retrieve all
        stocks = {
                    'stock1' : {
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
                                },
                    'stock2' : {
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
                                },
                    'stock3' : {
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
                    # ... retrieve all
        }

        bonds = {
                    'Bond1' : {
                                'maturity-date' : '2/14/2030',
                                'amount' : 1000.00
                    },
                    'Bond2' : {
                                'maturity-date' : '3/12/2021',
                                'amount' : 500.00
                    },
                    'Bond3' : {
                                'maturity-date' : '7/10/2025',
                                'amount' : 5000.00
                    }
                    # ... retrieve all
        }
        realestate = {
                        'add1' : {
                                    "estimated value" : 4382905,
                                    "current value" : 5438256
                                 },
                        'add2' : {
                                    "estimated value" : 4637586,
                                    "current value" : 8658556
                                 },
                        'add3' : {
                                    "estimated value" : 4876876,
                                    "current value" : 8769780
                                 },
        }

        debts = {
                    'debt1' : {
                                    'principal' : 240000,
                                    'interest' : 12.5,
                                    'period' : 'Monthly',
                                    'payment date' : 'Some payment date',
                                    'account associated' : 'Acct'

                              },
                    'debt2' : {
                                    'principal' : 240000,
                                    'interest' : 12.5,
                                    'period' : 'Monthly',
                                    'payment date' : 'Some payment date',
                                    'account associated' : 'Acct'

                              },
                    'debt3' : {
                                    'principal' : 240000,
                                    'interest' : 12.5,
                                    'period' : 'Monthly',
                                    'payment date' : 'Some payment date',
                                    'account associated' : 'Acct'

                              }
        }

        cash = json.dumps(cash)
        stocks = json.dumps(cash)
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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = GetUser(form.username.data, form.password.data)
        except Exception as error:
            print(error)
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect("/")
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
        return redirect("/")
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/index")
@login_required
def index():
	return render_template("index.html")

