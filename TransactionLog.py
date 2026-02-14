from Transaction import Transaction
from FileHandler import FileHandler

class TransactionLog:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_transactions(self):
        return self.transactions

    def write_session_file(self, filename: str):
        FileHandler.write_file(filename, self)

    def clear(self):
        self.transactions.clear()