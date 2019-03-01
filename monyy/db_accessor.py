from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import date
from datetime import datetime
from monyy import db
from .database import *
from .stocks import *

#Check that the user actually owns this account
def ownershipCheck(temp_user, temp_account):
    #check that temp_user.id == temp_account.user_id
    #Raise an exception if not
    if not temp_user.user_id == temp_account.user_id:
        raise Exception("This account does not belong to the current user!")

class BankAccountAccessor():


    #Get all accounts under one user
    def getUserAccounts(self, temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Account.query.filter_by(user_id=id).filter_by(account_type='BANK_ACCOUNT').all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no bank accounts!")
        #Return that list
        return accounts
        


    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_bank_account
            ).join(Bank_account
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    #Get a specified number of transactions based on the limite
    def getTransactions(self,temp_user, temp_account, temp_limit):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_bank_account
            ).join(Bank_account
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no bank accounts!")
        #Return the list
        return transactions

    def getTransactionsOnDate(self,temp_user, temp_account, temp_limit, temp_date):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).filter(Transaction.transaction_date<=temp_date
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_bank_account
            ).join(Bank_account
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions on this account!")
        #Return the list
        return transactions

    #Get the current balance for an account
    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value
            ).label('balance')
            ).filter_by(account_id=temp_account.account_id
            ).filter(Transaction.transaction_id<=temp_transaction.transaction_id
            ).filter(Transaction.transaction_date<=temp_date
            ).first()
        #Return the int for the balance
        return int(query.balance)

    #Make a new transaction
    def makeTransaction(self,temp_user, temp_account, temp_type, temp_value, note, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.
        try:
            query = db.session.query(Account, Transaction, Transaction_bank_account
                ).filter_by(account_id=temp_account.account_id
                ).join(Transaction
                ).join(Transaction_bank_account
                ).first()
            #Get the Bank Account id from the Transaction BA
            bank_id = query.Transaction_bank_account.bank_account_id
        except Exception:
            raise Exception("There are no prior transactions! This account should not exist!")
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, 
                transaction_type=temp_type, 
                transaction_value=temp_value, 
                transaction_date=temp_date, 
                transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id
            ).filter_by(transaction_type=temp_type
            ).filter_by(transaction_value=temp_value
            ).filter_by(transaction_date=temp_date
            ).first()
        if new_transaction is None:
            raise Exception("Error making new transaction!")
        #Make a new Transaction BA with the bank account id
        new_transaction_ba= Transaction_bank_account(transaction_id=new_transaction.transaction_id, bank_account_id=bank_id)
        db.session.add(new_transaction_ba)
        db.session.commit()

    #Make a new account
    def makeAccount(self,temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
        #make an account with the given values
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='BANK_ACCOUNT')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id
                ).filter_by(account_name=temp_name
                ).filter_by(account_type='BANK_ACCOUNT'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! " + str(error))
        #make a first transaction with same values referencing the account id
        try:
            new_transaction = Transaction(account_id=new_account.account_id, 
                transaction_type='DEPOSIT', 
                transaction_value=temp_value, 
                transaction_note="Opening account")
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction = Transaction.query.filter_by(account_id=new_account.account_id
                ).filter_by(transaction_type='DEPOSIT'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making first transaction! "+str(error))
        #make a bank account with the proper values
        try:
            new_bank_account = Bank_account(bank_name=temp_bank_name, account_digits=temp_digits)
            db.session.add(new_bank_account)
            db.session.commit()
            new_bank_account = Bank_account.query.filter_by(bank_name=temp_bank_name
                ).filter_by(account_digits=temp_digits
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making bank account! "+str(error))
        #make a transaction ba with the transaction id
        try:
            new_transaction_ba= Transaction_bank_account(transaction_id=new_transaction.transaction_id, bank_account_id=new_bank_account.bank_account_id)
            db.session.add(new_transaction_ba)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create account! Error making transaction_ba! "+str(error))

    #Make withdrawal
    def makeWithdrawal(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value is negative, since we are removing money
        if temp_value > 0:
            temp_value = (-1*temp_value)
        try:
            #Make a transaction of type withdrawal
            self.makeTransaction(temp_user, temp_account, "WITHDRAWAL", temp_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

    #Make deposit
    def makeDeposit(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value is positive
        if temp_value < 0:
            temp_value=(-1*temp_value)
        try:
            #Make a transaction of type Deposit
            self.makeTransaction(temp_user, temp_account, "DEPOSIT", temp_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

    #Do transfer
    def makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value for the source transaction is negative, since we are removing money
        #And that the value for the destination is positive, since money is being added
        if temp_value >= 0:
            source_value = (-1*temp_value)
            dest_value=temp_value
        elif temp_value < 0:
            source_value=temp_value
            dest_value = (-1*temp_value)
        try:
            #Make a transfer transaction on the source account
            self.makeTransaction(temp_user, source_account, "TRANSFER", source_value, temp_note, temp_date=temp_date)
            #Make a transfer transaction on the destination account
            self.makeTransaction(temp_user, dest_account, "TRANSFER", dest_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

     #Edit 4 digits
    
    def editDigits(self,temp_bank_account_id, temp_digits):
        #Get the account
        temp_bank_account = Bank_account.query.filter_by(bank_account_id=temp_bank_account_id).first()
        if temp_bank_account is None:
            raise Exception("There is no bank account with that id!")
        temp_bank_account.account_digits = temp_digits
        db.session.commit()

    #Edit bank name
    def editBankName(self,temp_bank_account_id, temp_bank_name):
        #Get the account
        temp_bank_account = Bank_account.query.filter_by(bank_account_id=temp_bank_account_id).first()
        if temp_bank_account is None:
            raise Exception("There is no bank account with that id!")
        temp_bank_account.bank_name = temp_bank_name
        db.session.commit()  


class BondAccessor():

    #Get all accounts under one user
    def getUserAccounts(self, temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Account.query.filter_by(user_id=id).filter_by(account_type='BOND').all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no bond accounts!")
        #Return that list
        return accounts


    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bond, Bond
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_bond
            ).join(Bond).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value
            ).label('balance')
            ).filter_by(account_id=temp_account.account_id
            ).filter(Transaction.transaction_id<=temp_transaction.transaction_id
            ).filter(Transaction.transaction_date<=temp_date
            ).first()
        #Return the int for the balance
        return int(query.balance)

    def makeAccount(self,temp_user, temp_name, temp_value, temp_date):
        #make an account with the given values
        abs(temp_value)
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='BOND')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id
                ).filter_by(account_name=temp_name
                ).filter_by(account_type='BOND'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! " + str(error))
        #make a first transaction with same values referencing the account id
        try:
            new_transaction = Transaction(account_id=new_account.account_id, transaction_type='DEPOSIT', transaction_value=temp_value, transaction_note="Opening account")
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction = Transaction.query.filter_by(account_id=new_account.account_id).filter_by(transaction_type='DEPOSIT').first()
        except Exception as error:
            raise Exception("Could not create account! Error making first transaction! "+str(error))
        #make a bank account with the proper values
        try:
            new_bond = Bond(name=temp_name, value=temp_value, maturation_date=temp_date)
            db.session.add(new_bond)
            db.session.commit()
            new_bond = Bond.query.filter_by(name=temp_name).filter_by(maturation_date=temp_date).first()
        except Exception as error:
            raise Exception("Could not create account! Error making bond account! "+str(error))
        #make a transaction ba with the transaction id
        try:
            new_transaction_bond= Transaction_bond(transaction_id=new_transaction.transaction_id, bond_id=new_bond.bond_id)
            db.session.add(new_transaction_bond)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create account! Error making transaction_bond! "+str(error))

    def editMaturationDate(self,temp_bond_id, temp_date):
        #Get the account
        temp_bond = Bond.query.filter_by(bond_id=temp_bond_id).first()
        if temp_bond is None:
            raise Exception("There is no bond with that id!")
        temp_bond.maturation_date = temp_date
        db.session.commit()

    #Edit bank name
    def editName(self,temp_bond_id, temp_name):
        #Get the account
        temp_bond = Bond.query.filter_by(bond_id=temp_bond_id).first()
        if temp_bond is None:
            raise Exception("There is no bond with that id!")
        temp_bond.name = temp_name
        db.session.commit()

    #Make a new transaction
    def makeTransaction(self,temp_user, temp_account, temp_type, note, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_bo.
        query = db.session.query(Account, Transaction, Transaction_bond, Bond
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).join(Transaction_bond
            ).join(Bond
            ).first()
        temp_value = -1*query.Bond.value
        if(temp_value == 0):
            raise Exception("This bond has already been spent!")
        if temp_date < query.Bond.maturation_date:
            raise Exception("This bond has not yet matured!")
        #Get the Bank Account id from the Transaction BA
        bond_id = query.Transaction_bond.bond_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, 
                transaction_type=temp_type, 
                transaction_value=temp_value, 
                transaction_date=temp_date, 
                transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id
            ).filter_by(transaction_type=temp_type
            ).filter_by(transaction_value=temp_value
            ).filter_by(transaction_date=temp_date
            ).first()
        if new_transaction is None:
            raise Exception("Error making new transaction!")
        query.Bond.value = 0
        db.session.commit()
        #Make a new Transaction BA with the bank account id
        new_transaction_bond= Transaction_bond(transaction_id=new_transaction.transaction_id, bond_id=bond_id)
        db.session.add(new_transaction_bond)
        db.session.commit()

    def makeWithdrawal(self,temp_user, temp_account, temp_note, temp_date=date.today()):
        #Make sure the value is negative, since we are removing money
        try:
            #Make a transaction of type withdrawal
            self.makeTransaction(temp_user, temp_account, "WITHDRAWAL", temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

    def makeTransfer(self,temp_user, source_account, dest_account, temp_note, temp_date=date.today()):
        #Make sure the value for the source transaction is negative, since we are removing money
        #And that the value for the destination is positive, since money is being added
        try:
            #Make a transfer transaction on the source account
            query = db.session.query(Account, Transaction, Transaction_bond, Bond
                ).filter_by(account_id=source_account.account_id
                ).join(Transaction
                ).join(Transaction_bond
                ).join(Bond
                ).first()
            temp_value = query.Bond.value
            self.makeTransaction(temp_user, source_account, "TRANSFER", temp_note, temp_date=temp_date)
            #Make a transfer transaction on the destination account
            BankAccountAccessor.makeTransaction(temp_user, dest_account, "TRANSFER", temp_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)


class StockAccessor():
    def getUserAccounts(self, temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Account.query.filter_by(user_id=id).filter_by(account_type='STOCK').all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no stock accounts!")
        #Return that list
        return accounts

    def getTransactions(self,temp_user, temp_account, temp_limit, temp_date=date.today()):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_stock, Stock
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).filter(Transaction.transaction_date<=temp_date
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_stock
            ).join(Stock
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions on this account!")
        #Return the list
        return transactions

    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_stock, Stock
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_stock
            ).join(Stock).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    def getValue(self, temp_stock_symbol, temp_datetime=datetime.now()):
        #Get number of Days
        try:
            if temp_datetime.date() != date.today():
                days = (datetime.today()-temp_datetime).days
                value = stockPriceOnDay(temp_stock_symbol, days)
                return value
            else:
                value = returnStock(temp_stock_symbol)
                return value
        except Exception as error:
            raise Exception("Could not get value!"+str(error))

        
        #Return the int for the balance
        return int(query.balance)

    def getNumStocks(self,temp_user, temp_account, temp_transaction, temp_datetime=datetime.now()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        temp_date = temp_datetime.date()
        query = db.session.query(func.sum(Transaction.transaction_value
            ).label('balance')
            ).filter_by(account_id=temp_account.account_id
            ).filter(Transaction.transaction_id<=temp_transaction.transaction_id
            ).filter(Transaction.transaction_date<=temp_date
            ).first()
        #Return the int for the balance
        return int(query.balance)

    #return how much we had in the stock, num of stocks * value
    def getBalance(self,temp_user, temp_account, temp_transaction, temp_stock_symbol, temp_datetime=datetime.now()):
        try:
            value = self.getValue(temp_stock_symbol, temp_datetime)
            num_stocks = self.getNumStocks(temp_user, temp_account, temp_transaction, temp_datetime)
            balance = value*num_stocks
            return balance
        except Exception as error:
            raise Exception(str(error))

    #Make a new account
    def makeAccount(self,temp_user, temp_account, temp_name, temp_num_stocks, temp_stock_symbol, temp_exchange='NASDAQ', temp_datetime=datetime.now()):
        #make sure that the stock symbol is valid
        try:
            returnStock(temp_stock_symbol)
        except:
            raise Exception("Not a valid stock symbol!")
        #make an account with the given values
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='STOCK')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id
                ).filter_by(account_name=temp_name
                ).filter_by(account_type='STOCK'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! " + str(error))
        #make a first transaction with same values referencing the account id
        try:
            new_transaction = Transaction(account_id=new_account.account_id, 
                transaction_type='TRANSFER', 
                transaction_value=temp_num_stocks, 
                transaction_note="Opening account")
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction = Transaction.query.filter_by(account_id=new_account.account_id
                ).filter_by(transaction_type='TRANSFER'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making first transaction! "+str(error))
        try:
            if temp_num_stocks < 0:
                temp_num_stocks = -temp_num_stocks
            temp_value = -(self.getValue(temp_stock_symbol, temp_datetime)*temp_num_stocks)
            BankAccountAccessor().makeTransaction(temp_user, temp_account, "TRANSFER", temp_value, 'Buying Stocks', temp_date=temp_datetime.date())
        except Exception as error:
            raise Exception("Could not create account! Error making bank transaction! "+str(error))
        #make a bank account with the proper values
        try:
            new_stock = Stock(stock_symbol=temp_stock_symbol, exchange=temp_exchange, num_stocks=temp_num_stocks)
            db.session.add(new_stock)
            db.session.commit()
            new_stock = Stock.query.filter_by(stock_symbol = temp_stock_symbol
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making Stock! "+str(error))
        #make a transaction ba with the transaction id
        try:
            new_transaction_stock= Transaction_stock(transaction_id=new_transaction.transaction_id, stock_id=new_stock.stock_id)
            db.session.add(new_transaction_stock)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create account! Error making transaction_stock! "+str(error))

    def buyStocks(self,temp_user, source_account, dest_account,temp_stock_symbol, temp_num_stocks, temp_note, temp_datetime=datetime.today()):
        if temp_num_stocks < 0:
            temp_num_stocks = -temp_num_stocks
        temp_value = -(self.getValue(temp_stock_symbol, temp_datetime)*temp_num_stocks)
        try:
            BankAccountAccessor().makeTransaction(temp_user, source_account, "TRANSFER", temp_value, temp_note, temp_date=temp_datetime.date())
            self.makeTransaction(temp_user, dest_account, "TRANSFER", temp_num_stocks, temp_note, temp_date = temp_datetime.date())
        except Exception as error:
            raise Exception(error)
            
    def sellStocks(self,temp_user, source_account, dest_account,temp_stock_symbol, temp_num_stocks, temp_note, temp_datetime=datetime.today()):
        if temp_num_stocks < 0:
            temp_num_stocks = -temp_num_stocks
        transactions = self.getTransactions(temp_user, dest_account, 1)
        if temp_num_stocks > self.getNumStocks(temp_user, dest_account, transactions[0].Transaction):
            raise Exception("You don't own that many stock of this symbol")
        temp_value = (self.getValue(temp_stock_symbol, temp_datetime)*temp_num_stocks)
        try:
            BankAccountAccessor().makeTransaction(temp_user, source_account, "TRANSFER", temp_value, temp_note, temp_date=temp_datetime.date())
            self.makeTransaction(temp_user, dest_account, "TRANSFER", -temp_num_stocks, temp_note, temp_date = temp_datetime.date())
        except Exception as error:
            raise Exception(error)

    def makeTransaction(self,temp_user, temp_account, temp_type, temp_value, note, temp_date=date.today()):
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.
        query = db.session.query(Account, Transaction, Transaction_stock).filter_by(account_id=temp_account.account_id).join(Transaction).join(Transaction_stock).first()
        #Get the Bank Account id from the Transaction BA
        stock_id = query.Transaction_stock.stock_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, 
                transaction_type=temp_type, 
                transaction_value=temp_value, 
                transaction_date=temp_date, 
                transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id
            ).filter_by(transaction_type=temp_type
            ).filter_by(transaction_value=temp_value
            ).filter_by(transaction_date=temp_date
            ).first()
        if new_transaction is None:
            raise Exception("Error making new transaction!")
        #Make a new Transaction BA with the bank account id
        new_transaction_stock= Transaction_stock(transaction_id=new_transaction.transaction_id, stock_id=stock_id)
        db.session.add(new_transaction_stock)
        db.session.commit()


class DebtAccessor():

    def getUserAccounts(self, temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Account.query.filter_by(user_id=id).filter_by(account_type='DEBT').all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no debt!")
        #Return that list
        return accounts
        
    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_debt, Debt
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_debt
            ).join(Debt
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    #Get a specified number of transactions based on the limite
    def getTransactions(self,temp_user, temp_account, temp_limit):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_debt, Debt
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_debt
            ).join(Debt
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no debt!")
        #Return the list
        return transactions

    def getTransactionsOnDate(self,temp_user, temp_account, temp_limit, temp_date):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_debt, Debt
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).filter(Transaction.transaction_date<=temp_date
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_debt
            ).join(Debt
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no debt!")
        #Return the list
        return transactions

    #Get the current balance for an account
    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value
            ).label('balance')
            ).filter_by(account_id=temp_account.account_id
            ).filter(Transaction.transaction_id<=temp_transaction.transaction_id
            ).filter(Transaction.transaction_date<=temp_date
            ).first()
        #Return the int for the balance
        return int(query.balance)

    #Make a new transaction
    def makeTransaction(self,temp_user, temp_account, temp_type, temp_value, note, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.
        query = db.session.query(Account, Transaction, Transaction_debt).filter_by(account_id=temp_account.account_id).join(Transaction).join(Transaction_debt).first()
        #Get the Bank Account id from the Transaction BA
        debt_id = query.Transaction_debt.debt_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, 
                transaction_type=temp_type, 
                transaction_value=temp_value, 
                transaction_date=temp_date, 
                transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id
            ).filter_by(transaction_type=temp_type
            ).filter_by(transaction_value=temp_value
            ).filter_by(transaction_date=temp_date
            ).first()
        if new_transaction is None:
            raise Exception("Error making new transaction!")
        #Make a new Transaction BA with the bank account id
        new_transaction_debt= Transaction_debt(transaction_id=new_transaction.transaction_id, debt_id=debt_id)
        db.session.add(new_transaction_debt)
        db.session.commit()

    #Make a new account
    def makeAccount(self,temp_user, temp_name, temp_value, temp_lender, temp_account, temp_period,temp_rate):
        #make an account with the given values
        if temp_value>0:
            temp_value = -temp_value
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='DEBT')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id
                ).filter_by(account_name=temp_name
                ).filter_by(account_type='DEBT'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! " + str(error))
        #make a first transaction with same values referencing the account id
        try:
            new_transaction = Transaction(account_id=new_account.account_id, 
                transaction_type='WITHDRAWAL', 
                transaction_value=temp_value, 
                transaction_note="Opening account")
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction = Transaction.query.filter_by(account_id=new_account.account_id
                ).filter_by(transaction_type='WITHDRAWAL'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making first transaction! "+str(error))
        #make a bank account with the proper values
        try:
            new_debt = Debt(lender=temp_lender, principal=temp_value,interest_period=temp_period,interest_rate=temp_rate, payment_account=temp_account.account_id)
            db.session.add(new_debt)
            db.session.commit()
            new_debt = Debt.query.filter_by(lender=temp_lender
                ).filter_by(interest_period=temp_period
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making debt! "+str(error))
        #make a transaction ba with the transaction id
        try:
            new_transaction_debt= Transaction_debt(transaction_id=new_transaction.transaction_id, debt_id=new_debt.debt_id)
            db.session.add(new_transaction_debt)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create account! Error making transaction_debt! "+str(error))

    #Make withdrawal
    def diggingDeeper(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value is negative, since we are removing money
        if temp_value > 0:
            temp_value = (-1*temp_value)
        try:
            #Make a transaction of type withdrawal
            self.makeTransaction(temp_user, temp_account, "WITHDRAWAL", temp_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

    #Make deposit
    def payingOff(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value is positive
        if temp_value < 0:
            temp_value=(-1*temp_value)
        try:
            #Make a transaction of type Deposit
            self.makeTransaction(temp_user, temp_account, "DEPOSIT", temp_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

    #Do transfer
    def makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):
        #Make sure the value for the source transaction is negative, since we are removing money
        #And that the value for the destination is positive, since money is being added
        if temp_value >= 0:
            source_value = (-1*temp_value)
            dest_value=temp_value
        elif temp_value < 0:
            source_value=temp_value
            dest_value = (-1*temp_value)
        try:
            #Make a transfer transaction on the source account
            BankAccountAccessor().makeTransaction(temp_user, source_account, "TRANSFER", source_value, temp_note, temp_date=temp_date)
            #Make a transfer transaction on the destination account
            self.makeTransaction(temp_user, dest_account, "TRANSFER", dest_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)

     #Edit 4 digits
    
    def editDate(self,temp_debt_id, temp_date):
        #Get the account
        temp_debt = Debt.query.filter_by(debt_id=temp_debt_id).first()
        if temp_debt is None:
            raise Exception("There is no debt with that id!")
        temp_debt.payment_date = temp_date
        db.session.commit()

    def editAccount(self,temp_debt_id, temp_account):
        #Get the account
        temp_debt = Debt.query.filter_by(debt_id=temp_debt_id).first()
        if temp_debt is None:
            raise Exception("There is no debt with that id!")
        temp_debt.payment_account = temp_account
        db.session.commit()

    def editRate(self,temp_debt_id, temp_rate):
        #Get the account
        temp_debt = Debt.query.filter_by(debt_id=temp_debt_id).first()
        if temp_debt is None:
            raise Exception("There is no debt with that id!")
        temp_debt.interest_rate = temp_rate
        db.session.commit()

    def editSchedule(self,temp_debt_id, temp_period):
        #Get the account
        temp_debt = Debt.query.filter_by(debt_id=temp_debt_id).first()
        if temp_debt is None:
            raise Exception("There is no debt with that id!")
        temp_debt.interest_period = temp_period
        db.session.commit()

    #Edit bank name
    def editLender(self,temp_debt_id, temp_name):
        #Get the account
        temp_debt = Debt.query.filter_by(debt_id=temp_debt_id).first()
        if temp_debt is None:
            raise Exception("There is no debt with that id!")
        temp_debt.lender = temp_name
        db.session.commit() 

class RealEstateAccessor():
    def getUserAccounts(self, temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Account.query.filter_by(user_id=id).filter_by(account_type='REAL_ESTATE').all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no real estate!")
        #Return that list
        return accounts
        
    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_real_estate, Real_estate
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_real_estate
            ).join(Real_estate).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    #Get a specified number of transactions based on the limite
    def getTransactions(self,temp_user, temp_account, temp_limit):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_real_estate, Real_estate
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_real_estate
            ).join(Real_estate
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no real estate!")
        #Return the list
        return transactions

    def getTransactionsOnDate(self,temp_user, temp_account, temp_limit, temp_date):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_real_estate, Real_estate
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).filter(Transaction.transaction_date<=temp_date
            ).order_by(Transaction.transaction_date.desc()
            ).order_by(Transaction.transaction_id.desc()
            ).join(Transaction_real_estate
            ).join(Real_estate
            ).limit(temp_limit
            ).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no real estate!")
        #Return the list
        return transactions

    #Get the current balance for an account
    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value
            ).label('balance')
            ).filter_by(account_id=temp_account.account_id
            ).filter(Transaction.transaction_id<=temp_transaction.transaction_id
            ).filter(Transaction.transaction_date<=temp_date
            ).first()
        #Return the int for the balance
        return int(query.balance)

    #Make a new transaction
    def makeTransaction(self,temp_user, temp_account, temp_type, temp_value, note, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.
        query = db.session.query(Account, Transaction, Transaction_real_estate
            ).filter_by(account_id=temp_account.account_id
            ).join(Transaction
            ).join(Transaction_real_estate
            ).first()
        #Get the Bank Account id from the Transaction BA
        real_estate_id = query.Transaction_real_estate.real_estate_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, 
                transaction_type=temp_type, 
                transaction_value=temp_value, 
                transaction_date=temp_date, 
                transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id
            ).filter_by(transaction_type=temp_type
            ).filter_by(transaction_value=temp_value
            ).filter_by(transaction_date=temp_date
            ).first()
        if new_transaction is None:
            raise Exception("Error making new transaction!")
        #Make a new Transaction BA with the bank account id
        new_transaction_real_estate= Transaction_real_estate(transaction_id=new_transaction.transaction_id, real_estate_id=real_estate_id)
        db.session.add(new_transaction_real_estate)
        db.session.commit()

    #Make a new account
    def makeAccount(self,temp_user, temp_name, temp_estimate, temp_original):
        #make an account with the given values
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='REAL_ESTATE')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id
                ).filter_by(account_name=temp_name
                ).filter_by(account_type='REAL_ESTATE'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! " + str(error))
        #make a first transaction with same values referencing the account id
        try:
            new_transaction = Transaction(account_id=new_account.account_id, 
                transaction_type='DEPOSIT', 
                transaction_value=temp_estimate, 
                transaction_note="Opening account")
            db.session.add(new_transaction)
            db.session.commit()
            new_transaction = Transaction.query.filter_by(account_id=new_account.account_id
                ).filter_by(transaction_type='DEPOSIT'
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making first transaction! "+str(error))
        #make a bank account with the proper values
        try:
            new_real_estate = Real_estate(name=temp_name, original_value=temp_original, estimated_value=temp_estimate)
            db.session.add(new_real_estate)
            db.session.commit()
            new_real_estate = Real_estate.query.filter_by(name=temp_name
                ).filter_by(original_value=temp_original
                ).first()
        except Exception as error:
            raise Exception("Could not create account! Error making real estate! "+str(error))
        #make a transaction ba with the transaction id
        try:
            new_transaction_real_estate= Transaction_real_estate(transaction_id=new_transaction.transaction_id, real_estate_id=new_real_estate.real_estate_id)
            db.session.add(new_transaction_real_estate)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create account! Error making transaction_real_estate! "+str(error))

    #Edit current estimated value
    def editEstimate(self,temp_user, temp_account,temp_real_estate_id, temp_note, temp_value, temp_date=date.today()):
        #Get the account
        temp_real_estate = Real_estate.query.filter_by(real_estate_id=temp_real_estate_id).first()
        if temp_real_estate is None:
            raise Exception("There is no real estate with that id!")
        old_value = temp_real_estate.estimated_value
        temp_change = temp_value - old_value
        self.makeTransaction(temp_user, temp_account, "VALUE_CHANGE", temp_change, temp_note, temp_date=temp_date)
        temp_real_estate.estimated_value = temp_value
        db.session.commit()

    #Edit bank name
    def editName(self,temp_real_estate_id, temp_name):
        #Get the account
        temp_real_estate = Real_estate.query.filter_by(real_estate_id=temp_real_estate_id).first()
        if temp_real_estate is None:
            raise Exception("There is no real estate with that id!")
        temp_real_estate.name = temp_name
        db.session.commit() 

class TagAccessor():

    def getTransactionTags(self, temp_transaction):
        query = db.session.query(Transaction, Transaction_tag, Tag
            ).filter_by(transaction_id = temp_transaction.transaction_id
            ).join(Transaction_tag
            ).join(Tag
            ).all()
        if len(query) == 0:
            raise Exception('Transaction has no tags!')
        return query

    def getTransactionTag(self, temp_transaction, tag_name):
        query = db.session.query(Transaction, Transaction_tag, Tag
            ).filter_by(transaction_id = temp_transaction.transaction_id
            ).join(Transaction_tag
            ).join(Tag
            ).all()
        if len(query) == 0:
            raise Exception('Transaction does not have this tag!')
        return query

    def makeTransactionTag(self, temp_transaction, temp_tag_name):
        #see if tag is already in tag table. If not add it
        tag_check = Tag.query().filter_by(tag_name = temp_tag_name).first()
        t_tag_exists = True
        if tag_check is None:
            tag_check = Tag(tag_name = temp_tag_name)
            db.session.add(tag_check)
            db.session.commit()
            tag_check = Tag.query().filter_by(tag_name = temp_tag_name).first()
        #check to see if this transaction already has this tag   
        else:
            try:
                t_tag = self.getTransactionTag(temp_transaction, temp_tag_name)
                t_tag_exists = True
            except:
                t_tag_exists = False
        #If this tag isn't already attatched, add the transaction tag
        if not tag_exists:
            new_t_tag = Transaction_tag(transaction_id = temp_transaction_id, tag_id = tag_check.tag_id)
            db.session.add(new_t_tag)
            db.session.commit()

    def getAccountTags(self, temp_account):
        query = db.session.query(Account, Account_tag, Tag
            ).filter_by(account_id = temp_account.account_id
            ).join(Account_tag
            ).join(Tag
            ).all()
        if len(query) == 0:
            raise Exception('Account has no tags!')
        return query

    def getAccountTag(self, temp_account, tag_name):
        query = db.session.query(Account, Account_tag, Tag
            ).filter_by(account_id = temp_account.account_id
            ).join(Account_tag
            ).join(Tag
            ).all()
        if len(query) == 0:
            raise Exception('Account does not have this tag!')
        return query

    def makeTransactionTag(self, temp_account, temp_tag_name):
        #see if tag is already in tag table. If not add it
        tag_check = Tag.query().filter_by(tag_name = temp_tag_name).first()
        a_tag_exists = True
        if tag_check is None:
            tag_check = Tag(tag_name = temp_tag_name)
            db.session.add(tag_check)
            db.session.commit()
            tag_check = Tag.query().filter_by(tag_name = temp_tag_name).first()
        #check to see if this transaction already has this tag
        else:
            try:
                a_tag = self.getTransactionTag(temp_account, temp_tag_name)
                a_tag_exists = True
            except:
                a_tag_exists = False
        #If this tag isn't already attatched, add the transaction tag
        if not tag_exists:
            new_a_tag = Transaction_tag(transaction_id = temp_account_id, tag_id = tag_check.tag_id)
            db.session.add(new_t_tag)
            db.session.commit()




def BAATest():
    baa = BankAccountAccessor()
    u = User(user_name='nfdjgbkdfjgkjbtfrkg', pass_hash = 'bfdjbvkjdbgvkjbdfkjgvbdfkjgvbkjf')
    db.session.add(u)
    db.session.commit()
    #def makeAccount(temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
    baa.makeAccount(u, 'test one', 5000, 'Chase', 5555)
    baa.makeAccount(u, 'test two', 5, 'BB&T', 3335)
    baa.makeAccount(u, 'test three', 180000000, 'Wells Fargo', 5556)
    accounts = baa.getUserAccounts(u)
    #assert(len(accounts)==3)
    a1 = accounts[0]
    a2 = accounts[1]
    a3 = accounts[2]
    
    t = baa.getAllTransactions(u, a1)
    print(t[0])
    #def makeDeposit(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
    baa.makeDeposit(u, a1, 4000, 'Test deposit')
    baa.makeDeposit(u,a1, -50, 'Test negative deposit')
    baa.makeWithdrawal(u,a1,75, 'Test withdrawal')
    baa.makeWithdrawal(u,a1,-600, 'Test negative withdrawal')
    t = baa.getAllTransactions(u, a1)
    #def getBalance(temp_user, temp_account, temp_transaction, temp_date=date.today()):
    print(baa.getBalance(u,a1,t[0].Transaction))
    for trans in t:
        print(trans.Transaction)
        print(baa.getBalance(u,a1,trans.Transaction))
    #makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):
    baa.makeTransfer(u, a1, a2, 50, 'transfer test')
    t1 = baa.getTransactions(u,a1,1)
    print(t1[0].Transaction)
    print(baa.getBalance(u,a1,t1[0].Transaction))
    t2 = baa.getTransactions(u,a2,1)
    print(t2[0].Transaction)
    print(baa.getBalance(u,a2,t2[0].Transaction))

def BondTest():
    ba = BondAccessor()
    u = User(user_name='nfdjgbkdfjgkjbtfrkeg', pass_hash = 'bfdjbvkjdbgvkjbdfkjgvbdfkjgvbkjf')
    db.session.add(u)
    db.session.commit()
    #makeAccount(self,temp_user, temp_name, temp_value,  temp_date)
    ba.makeAccount(u, 'test_one', 5000, date.today())
    ba.makeAccount(u, 'test_two', 605, date.today())
    ba.makeAccount(u, 'test_three', 89, date.today())
    accounts = ba.getUserAccounts(u)
    #assert(len(accounts)==3)
    a1 = accounts[0]
    a2 = accounts[1]
    a3 = accounts[2]
    t = ba.getAllTransactions(u, a1)
    print(t[0])
    #makeWithdrawal(self,temp_user, temp_account, temp_note, temp_date=date.today())
    ba.makeWithdrawal(u, a1, 'Spending bond')
    try:
        ba.makeWithdrawal(u, a1, 'Spending bond')
        t = ba.getAllTransactions(u, a1)
        print(t)
        print(t[0].Bond.value)
    except Exception:
        print("Couldn't take more money.")
    t = ba.getAllTransactions(u, a1)
    print(t)
    print(t[0].Bond.value)
    print(ba.getBalance(u, a1, t[0].Transaction))

def DebtTest():
    da = DebtAccessor()
    baa = BankAccountAccessor()
    u = User(user_name='nfdjgbkdfjgkjbtfrkig', pass_hash = 'bfdjbvkjdbgvkjbdfkjgvbdfkjgvbkjf')
    db.session.add(u)
    db.session.commit()
    #def makeAccount(temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
    baa.makeAccount(u, 'test four', 5, 'BB&T', 3335)
    bank_accounts = baa.getUserAccounts(u)
    a4 = bank_accounts[0]

    da.makeAccount(u, 'test one', -5000, 'Nice men in Jersey', a4, date(2019, 3, 1))
    da.makeAccount(u, 'test two', -5, 'Bugs Bunny', a4, date(2019, 2, 18))
    da.makeAccount(u, 'test three', 17, 'Thanos', a4, date(2019, 4, 26))
    accounts = da.getUserAccounts(u)
    
    #assert(len(accounts)==3)
    a1 = accounts[0]
    a2 = accounts[1]
    a3 = accounts[2]

    
    t = da.getAllTransactions(u, a1)
    print(t[0])
    #def makeDeposit(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
    da.payingOff(u, a1, 4000, 'Test deposit')
    da.payingOff(u,a1, -50, 'Test negative deposit')
    da.diggingDeeper(u,a1,75, 'Test withdrawal')
    da.diggingDeeper(u,a1,-600, 'Test negative withdrawal')
    t = da.getAllTransactions(u, a1)
    #def getBalance(temp_user, temp_account, temp_transaction, temp_date=date.today()):
    print(da.getBalance(u,a1,t[0].Transaction))
    for trans in t:
        print(trans.Transaction)
        print(da.getBalance(u,a1,trans.Transaction))
    #makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):
    da.makeTransfer(u, a4, a2, 5, 'transfer test')
    t1 = da.getTransactions(u,a2,1)
    print(t1[0].Transaction)
    print(da.getBalance(u,a2,t1[0].Transaction))
    debt = {}
    debt_accounts = da.getUserAccounts(u)
    for account in debt_accounts:
        debt_trans = da.getTransactionsOnDate(u, account, 10, date.today())
        ex_trans = debt_trans[0]
        debt_name = ex_trans.Debt.lender
        debt_balance = da.getBalance(u, account, ex_trans.Transaction)
        pay_date = ex_trans.Debt.payment_date
        pay_account = ex_trans.Debt.payment_account
        pay_account = Account.query.filter_by(user_id=u.user_id).filter_by(account_id = pay_account).first()
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
        print(debt)

def REATest():
    raa = RealEstateAccessor()
    u = User(user_name='nfdjgbkdfjgkjbtfrkog', pass_hash = 'bfdjbvkjdbgvkjbdfkjgvbdfkjgvbkjf')
    db.session.add(u)
    db.session.commit()
    #def makeAccount(temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
    raa.makeAccount(u, 'White House', 5, 5000)
    raa.makeAccount(u, 'Avenger\'s Tower', 5001, 5000)
    raa.makeAccount(u, 'PEI', 9, 5)
    accounts = raa.getUserAccounts(u)
    #assert(len(accounts)==3)
    a1 = accounts[0]
    a2 = accounts[1]
    a3 = accounts[2]
    
    t = raa.getAllTransactions(u, a2)
    print(t[0])
    temp_real_estate = Real_estate.query.filter_by(name='Avenger\'s Tower').first()
    re_id = temp_real_estate.real_estate_id
    #def makeDeposit(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
    raa.editEstimate(u, a2,re_id, 'rise in popularity', 6000)
    raa.editEstimate(u,a2,re_id, 'Infinity War', 3000)
    t = raa.getAllTransactions(u, a2)
    #def getBalance(temp_user, temp_account, temp_transaction, temp_date=date.today()):
    print(raa.getBalance(u,a2,t[0].Transaction))
    for trans in t:
        print(trans.Transaction)
        print(raa.getBalance(u,a2,trans.Transaction))
    #makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):
    realestate = {}
    re_accounts = raa.getUserAccounts(u)
    for account in re_accounts:
        re_trans = raa.getTransactionsOnDate(u, account, 1, date.today())
        re_name = account.account_name
        trans = re_trans[0]
        temp = {
            'original value' : trans.Real_estate.original_value,
            'estimated value' : trans.Real_estate.estimated_value
        }
        realestate[re_name] = temp
    print(realestate)

def StockTest():
    baa = BankAccountAccessor()
    sa = StockAccessor()
    u = User(user_name='nfdjgbkdfjgkjbtfrkug', pass_hash = 'bfdjbvkjdbgvkjbdfkjgvbdfkjgvbkjf')
    db.session.add(u)
    db.session.commit()
    #def makeAccount(temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
    baa.makeAccount(u, 'test four', 5, 'BB&T', 3335)
    bank_accounts = baa.getUserAccounts(u)
    a4 = bank_accounts[0]

    sa.makeAccount(u, 'Disney', 50, 'DIS', a4)
    sa.makeAccount(u, 'Apple', 500, 'AAPL', a4)
    sa.makeAccount(u, 'Google', 5, 'GOOG', a4)
    accounts = sa.getUserAccounts(u)
    #assert(len(accounts)==3)
    a1 = accounts[0]
    a2 = accounts[1]
    a3 = accounts[2]
    
    t = sa.getAllTransactions(u, a1)
    print(t[0])
    temp_stock = Stock.query.filter_by(stock_symbol='DIS').first()
    stock_id = temp_stock.stock_id
    #def makeDeposit(self,temp_user, temp_account, temp_value, temp_note, temp_date=date.today()):
    sa.buyStocks(u, a4, a1, 'DIS', 500, 'ready for Infinity War')
    sa.sellStocks(u, a4, a1, 'DIS', -400, 'done with Infinity War')
    sa.buyStocks(u, a4, a1, 'DIS', 300, 'ready for Captain Marvel')

    t = sa.getAllTransactions(u, a1)
    #def getBalance(temp_user, temp_account, temp_transaction, temp_date=date.today()):
    print(sa.getBalance(u,a1,t[0].Transaction, 'DIS'))
    for trans in t:
        print(trans.Transaction)
        print(sa.getBalance(u,a1,trans.Transaction, 'DIS'))
    #makeTransfer(self,temp_user, source_account, dest_account, temp_value, temp_note, temp_date=date.today()):


