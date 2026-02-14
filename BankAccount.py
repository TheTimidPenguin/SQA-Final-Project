from decimal import Decimal

class BankAccount:
    """
    This class represents a single bank account in the system

    Attributes:
        account_number (str): Unique account number (5 digits and zero-padded)
        holder_name (str): Name of the account holder (max 20 chars)
        balance (Decimal): Balance of the account
        status (str): Status of the account - 'A' (active) or 'D' (disabled)
        plan (str): Plan of the account - 'SP' (student) or 'NP' (non-student)
    """
    def __init__(self, account_number : str, holder_name : str, balance: Decimal, status: str = 'A', plan: str = 'SP'):
        """
        Initialize a new BankAccount instance.

        :param account_number:  Unique account number (5 digits and zero-padded)
        :param holder_name: Name of the account holder (max 20 chars)
        :param balance: Balance of the account
        :param status: Initial status of the account. Defaults to 'A' (Optional)
        :param plan: Account plan. Defaults to 'SP' (Optional)
        """
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance
        self.status = status
        self.plan = plan

    def is_active(self) -> bool:
        """
        :return: Returns true if the account is active, false otherwise
        """
        return self.status == 'A'

    def is_student(self) -> bool:
        """
        :return: returns true if the account is student, false otherwise
        """
        return self.plan == 'SP'

    def balance_deduction(self, amount: Decimal):
        """
        Subtract the given amount from the account balance

        :param amount: Amount to be deduced
        """
        self.balance -= amount

    def balance_addition(self, amount: Decimal):
        """
        Add the given amount to the account balance

        :param amount: Amount to be added
        """
        self.balance += amount

    def disable(self):
        """
        Set the account status to 'D' to disable the account
        """
        self.status = 'D'