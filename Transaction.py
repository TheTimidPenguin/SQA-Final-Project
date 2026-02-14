from decimal import Decimal

from FileHandler import FileHandler


class Transaction:
    def __init__(self, transaction_code: str, holders_name: str, account_num: str, balance: Decimal, misc: str = ''):
        self.transaction_code = transaction_code
        self.holders_name = holders_name
        self.account_num = account_num
        self.balance = balance
        self.misc = misc

    def format(self):
        return FileHandler.format_transaction(self)

    # def get_transaction_code(self):
    #     return self.transaction_code
    #
    # def get_holders_name(self):
    #     return self.holders_name
    #
    # def get_balance(self):
    #     return self.balance
    #
    # def get_misc(self):
    #     return self.misc