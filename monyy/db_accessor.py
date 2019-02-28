from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import date
from .database import *


class BankAccountAccessor():

    #Get all accounts under one user
    def getUserAccounts(temp_user):
        #Get user id from user
        id = temp_user.user_id
        #Query account for list of all the user's accounts where the account type = bank account.
        accounts = Transaction.query.filter_by(and_(user_id=id, transaction_type='bank_account')).all()
        #Raise an exception if they have none
        if len(accounts) == 0:
            raise Exception("This user has no bank accounts!")
        #Return that list
        return accounts

    def ownershipCheck(temp_user, temp_account):
        #check that temp_user.id == temp_account.user_id
        #Raise an exception if not
        if not temp_user.user_id == temp_account.user_id:
            raise Exception("This account does not belong to the current user!")
        

    #get all transactions under one account
    def getTransactions(temp_user, temp_account):
        #Check that the account actually belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Make a query; joining account, transaction, bank account transaction, and bank account. Get the list of all
        
        #Raise an exception if they have none

        #Return the list

    #Get the current balance for an account
    def getBalance(temp_user, temp_account, temp_transaction, temp_date=date.today()):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Join transaction and account, and sum on the transaction value where the transaction id <= temp_transaction_id and date <= Date

        #Return the int for the balance



    #Make a new transaction
    def makeTransaction(temp_user, temp_account, temp_type, temp_value, temp_date=date.today(), note=""):
        #check that the account belongs to the user
        try:
            ownershipCheck(temp_user, temp_account)
        except Exception as error: 
            raise Exception(error)
        #Find a prior transaction on this account, joining on transaction_ba.

        #Get the Bank Account id from the Transaction BA

        #Make a new transaction with the input information

        #Make a new Transaction BA with the bank account id

    #Make a new account
    def makeAccount(temp_user, temp_name, temp_value, temp_bank_name, temp_digits):
        #make an account with the given values

        #make a first transaction with same values referencing the account id

        #make a transaction ba with the transaction id

        #make a bank account with the proper values




