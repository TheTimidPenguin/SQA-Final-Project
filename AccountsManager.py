from decimal import Decimal

from BankAccount import BankAccount
from FileHandler import FileHandler

class AccountsManager:
    """
    Manages the data of bank accounts. Provides methods to load accounts from file, find accounts by number or name, and
    perform operations on them as well as generate new account numbers.
    """
    def __init__(self):
        """Initialize an empty account dictionary"""
        self.accounts = {}

    def load_accounts(self, filename: str) -> bool:
        """
        Load accounts from the current bank accounts file into memory.

        :param filename: Path to the account file.
        :return: True if loading succeeded, False otherwise.
        """
        try:
            accounts = FileHandler.read_file(filename)
            for account in accounts:
                self.accounts[account.account_number] = account
            return True
        except (IOError, ValueError) as e:
            print(f"error: cannot read account file '{filename}' - {e}")
            return False

    def find_account(self, account_number: str):
        """
        Retrieve an account by its account number.

        :param account_number: 5‑digit account number (zero‑padded).
        :return: BankAccount (if found) or None (otherwise).
        """
        return self.accounts.get(account_number)

    def find_account_by_name(self, name: str):
        """
        Find the first account belonging to a given holder name. (Assumes at most one account per holder)
        :param name: Account holder's name.
        :return: BankAccount (if found) or None (otherwise).
        """
        for account in self.accounts.values():
            if account.name == name:
                return account
        return None

    @staticmethod
    def debit(account: BankAccount, amount: Decimal):
        """
        Subtract the specified amount from the account balance.

        :param account: The account to debit.
        :param amount: Positive amount to deduct.
        """
        if account:
            account.balance_deduction(amount)

    @staticmethod
    def credit(account: BankAccount, amount: Decimal):
        """
        Add the specified amount from the account balance.

        :param account: The account to credit.
        :param amount: Positive amount to add.
        """
        account.balance_addition(amount)

    def disable_account(self, account_number: str):
        """
        Set the status of the account to disabled ('D').
        :param account_number: The account number to disable.
        """
        account = self.find_account(account_number)
        if account:
            account.disable()

    def delete(self, account_number: str):
        """
        Permanently remove an account from the in‑memory collection.
        :param account_number: The account number to delete.
        :return:
        """
        if account_number in self.accounts:
            del self.accounts[account_number]

    def change_plan(self, account_number: str):
        """
        Change the account plan from student ('SP') to non‑student ('NP').Does nothing if the account already
        non‑student.

        :param account_number: The account number to modify.
        """
        account = self.find_account(account_number)
        if account and account.is_student():
            account.plan = 'NP'

    def generate_new_account_number(self) -> str:
        """
        Generate a new unique 5‑digit account number (zero‑padded).
        :return: A new account number greater than any existing number. (str)
        """
        if not self.accounts:
            return "00001"
        max_num = max(int(num) for num in self.accounts.keys())
        return f"{max_num + 1:05d}"


