from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import date
from monyy import db
from .database import *


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

    #Check that the user actually owns this account
    def ownershipCheck(self,temp_user, temp_account):
        #check that temp_user.id == temp_account.user_id
        #Raise an exception if not
        if not temp_user.user_id == temp_account.user_id:
            raise Exception("This account does not belong to the current user!")
        
    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account).filter_by(account_id=temp_account.account_id).join(Transaction).order_by(Transaction.transaction_id.desc()).join(Transaction_bank_account).join(Bank_account).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    #Get a specified number of transactions based on the limite
    def getTransactions(self,temp_user, temp_account, temp_limit):
        #Check that the account actually belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account).filter_by(account_id=temp_account.account_id).join(Transaction).order_by(Transaction.transaction_date.desc()).order_by(Transaction.transaction_id.desc()).join(Transaction_bank_account).join(Bank_account).limit(temp_limit).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no bank accounts!")
        #Return the list
        return transactions

    def getTransactionsOnDate(self,temp_user, temp_account, temp_limit, temp_date):
        #Check that the account actually belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bank_account, Bank_account).filter_by(account_id=temp_account.account_id).join(Transaction).filter(Transaction.transaction_date<=temp_date).order_by(Transaction.transaction_date.desc()).order_by(Transaction.transaction_id.desc()).join(Transaction_bank_account).join(Bank_account).limit(temp_limit).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no bank accounts!")
        #Return the list
        return transactions

    #Get the current balance for an account
    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value).label('balance')).filter_by(account_id=temp_account.account_id).filter(Transaction.transaction_id<=temp_transaction.transaction_id).filter(Transaction.transaction_date<=temp_date).first()
        #Return the int for the balance
        return int(query.balance)

    #Make a new transaction
    def makeTransaction(self,temp_user, temp_account, temp_type, temp_value, note, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.
        query = db.session.query(Account, Transaction, Transaction_bank_account).filter_by(account_id=temp_account.account_id).join(Transaction).join(Transaction_bank_account).first()
        #Get the Bank Account id from the Transaction BA
        bank_id = query.Transaction_bank_account.bank_account_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, transaction_type=temp_type, transaction_value=temp_value, transaction_date=temp_date, transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id).filter_by(transaction_type=temp_type).filter_by(transaction_value=temp_value).filter_by(transaction_date=temp_date).first()
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
            new_account = Account.query.filter_by(user_id=temp_user.user_id).filter_by(account_name=temp_name).filter_by(account_type='BANK_ACCOUNT').first()
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
            new_bank_account = Bank_account(bank_name=temp_bank_name, account_digits=temp_digits)
            db.session.add(new_bank_account)
            db.session.commit()
            new_bank_account = Bank_account.query.filter_by(bank_name=temp_bank_name).filter_by(account_digits=temp_digits).first()
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

    #Check that the user actually owns this account
    def ownershipCheck(self,temp_user, temp_account):
        #check that temp_user.id == temp_account.user_id
        #Raise an exception if not
        if not temp_user.user_id == temp_account.user_id:
            raise Exception("This account does not belong to the current user!")

    #get all transactions under one account
    def getAllTransactions(self,temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        transactions = db.session.query(Account, Transaction, Transaction_bond, Bond).filter_by(account_id=temp_account.account_id).join(Transaction).order_by(Transaction.transaction_id.desc()).join(Transaction_bond).join(Bond).all()
        #Raise an exception if they have none
        if len(transactions) == 0:
            raise Exception("This user has no transactions!")
        #Return the list
        return transactions

    def getBalance(self,temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Query on the transaction where account_id = temo_account id, sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date
        query = db.session.query(func.sum(Transaction.transaction_value).label('balance')).filter_by(account_id=temp_account.account_id).filter(Transaction.transaction_id<=temp_transaction.transaction_id).filter(Transaction.transaction_date<=temp_date).first()
        #Return the int for the balance
        return int(query.balance)

    def makeAccount(self,temp_user, temp_name, temp_value, temp_date):
        #make an account with the given values
        abs(temp_value)
        try:
            new_account = Account(user_id=temp_user.user_id, account_name=temp_name, account_type='BOND')
            db.session.add(new_account)
            db.session.commit()
            new_account = Account.query.filter_by(user_id=temp_user.user_id).filter_by(account_name=temp_name).filter_by(account_type='BOND').first()
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
            new_bank_account = Bond.query.filter_by(name=temp_name).filter_by(maturation_date=temp_date).first()
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
            self.ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_bo.
        query = db.session.query(Account, Transaction, Transaction_bond, Bond).filter_by(account_id=temp_account.account_id).join(Transaction).join(Transaction_bond).join(Bond).first()
        temp_value = query.Bond.value
        if(temp_value == 0):
            raise Exception("This bond has already been spent!")
        if temp_date < query.Bond.maturation_date:
            raise Exception("This bond has not yet matured!")
        #Get the Bank Account id from the Transaction BA
        bond_id = query.Transaction_bond.bond_id
        #Make a new transaction with the input information
        try:
            new_transaction = Transaction(account_id=temp_account.account_id, transaction_type=temp_type, transaction_value=temp_value, transaction_date=temp_date, transaction_note=note)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as error:
            raise Exception("Could not create transaction! " + str(error))
        new_transaction = Transaction.query.filter_by(account_id=temp_account.account_id).filter_by(transaction_type=temp_type).filter_by(transaction_value=temp_value).filter_by(transaction_date=temp_date).first()
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
            BankAccountAccessor.makeTransaction(temp_user, dest_account, "TRANSFER", dest_value, temp_note, temp_date=temp_date)
        except Exception as error:
            raise Exception(error)


#class StockAccessor():


#class DebtAccessor():


#class RealEstateAccessor():



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
    print(ba.getBalance(u, a1, t[0]))
