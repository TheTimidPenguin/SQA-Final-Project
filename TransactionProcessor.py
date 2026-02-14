from decimal import Decimal

from AccountsManager import AccountsManager
from BankAccount import BankAccount
from Session import Session
from Transaction import Transaction
from TransactionLog import TransactionLog
from UserInterface import UserInterface


class TransactionProcessor:
    """
    Handles the validation and execution of all banking transactions. Interacts with AccountsManager to modify account
    data, update the session sending and receiving limits, and records successful transactions in TransactionLog object.
    """
    def __init__(self, account_manager: AccountsManager, session: Session, trans_log: TransactionLog):
        """
        Initializes the processor with required dependencies

        :param account_manager: AccountsManager object (account storage and operations)
        :param session: Session object (Tracks login states like mode and cumulative limits)
        :param trans_log: TransactionLog object (For saving daily transaction records
        """
        self.account_manager = account_manager
        self.session = session
        self.trans_log = trans_log

    def validate_transaction(self, account:BankAccount, transaction_type: str, amount: Decimal = None) -> bool:
        """
        Perform common validations for a transaction:
          - Account existence and active status.
          - Ownership (if not admin).
          - For withdrawal, transfer, paybill: sufficient funds and session limit.

        :param account: The account involved in the transaction.
        :param transaction_type: Type of transaction (e.g., 'paybill' or 'withdrawal').
        :param amount: Required for balance‑affecting transactions (optional)

        :return: True if all checks pass, False otherwise.
        """

        # Checking existence, active, account is not another's and session is admin
        if not account:
            UserInterface.display_error("Account does not exist")
            return False
        if not account.is_active():
            UserInterface.display_error(f"Account {account.holder_name} is disabled")
            return False
        if not self.session.is_admin() and self.session.current_user != account.holder_name:
            UserInterface.display_error(f"Account {account.holder_name} does not belong to you")
            return False

        # For transactions that have session limits
        if transaction_type in ('withdrawal', 'transfer', 'paybill'):
            if amount is None:
                UserInterface.display_error("Amount must be provided")
                return False
            if not self._sufficient_funds(account, amount):
                return False
            if not self._validate_limit(transaction_type, amount):
                return False

        return True

    def find_current_user(self, account_number: str):
        """
        Finds the current user in the bank account

        :param account_number: The account number to look up.
        :return: BankAccount object or None if not found
        """
        return self.account_manager.find_account(account_number)

    def withdrawal(self, account_number: str, amount: Decimal) -> bool:
        """
        Process a withdrawal transaction.

        :param account_number: The account to withdraw from.
        :param amount: Positive amount to withdraw.
        :return: True if the transaction succeeded, False otherwise.
        """
        # Finding account and validating
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Withdrawal', amount):
            return False

        # Execute withdrawal
        self.account_manager.debit(account, amount)
        self.session.session_limit('withdrawal', amount)

        # Log the transaction
        trans_line = Transaction('01', account.holder_name, account_number,amount, '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Withdrawal of ${amount:.2f} successful")

        return True

    def transfer(self, from_account_num: str, to_account_num: str, amount: Decimal) -> bool:
        """
        Process a transfer between two accounts.

        :param from_account_num: Source account number.
        :param to_account_num: Destination account number.
        :param amount: Positive amount to transfer.

        :return:True if successful, False otherwise.
        """
        # Finding source account and validating
        from_account = self.find_current_user(from_account_num)
        if not self.validate_transaction(from_account, 'Transfer', amount):
            return False

        # Finding destination account and validating
        to_account = self.find_current_user(to_account_num)
        if not self.validate_transaction(to_account, 'Transfer', amount):
            return False

        # Execute Transfer
        self.account_manager.debit(from_account, amount)
        self.account_manager.credit(to_account, amount)
        self.session.session_limit('transfer', amount)

        # Log the transaction
        trans_line = Transaction('02', from_account.holder_name, from_account_num,amount, '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Transfer of ${amount:.2f} successful")

        return True

    def paybill(self, account_number: str, company: str, amount: Decimal) -> bool:
        """
        Process a bill payment to an approved company.

        :param account_number: The account to pay from.
        :param company: Company code (EC, CQ, FI).
        :param amount: Positive payment amount.

        :return: True if successful, False otherwise.
        """

        # Finding account and validating
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'PayBill', amount):
            return False

        # Execute paybill
        self.account_manager.debit(account, amount)
        self.session.session_limit('paybill', amount)

        # Log the transaction
        trans_line = Transaction('03', account.holder_name, account_number,amount, company)
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"PayBill of ${amount:.2f} successful")

        return True

    def deposit(self, account_number: str, amount: Decimal) -> bool:
        """
        Process a deposit. According to requirements, deposit does **not** update the account balance immediately; it
        only logs the transaction (Still fixing that part).

        :param account_number: The account to deposit into.
        :param amount: Positive deposit amount.
        :return:True if successful, False otherwise.
        """

        # Finding account and validating
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Deposit', amount):
            return False

        # Execute deposit
        self.account_manager.credit(account, amount)

        # Log the transaction
        trans_line = Transaction('04', account.holder_name, account_number,amount, '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Deposit of ${amount:.2f} successful")

        return True

    def create(self, name: str, initial_balance: Decimal):
        """
        Process account creation (admin only). Does **not** add the account to the in‑memory repository; only logs a
        'create' transaction.

        :param name: New account holder's name.
        :param initial_balance: Starting balance (must be >= 0 and <= 99999.99).
        :return: The new account number if successful, otherwise None.
        """

        # Generating new account number
        new_account_num = self.account_manager.generate_new_account_number()

        # Log the transaction
        trans_line = Transaction('05', name, new_account_num, initial_balance, '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Creation of ${initial_balance:.2f} successful")

        return new_account_num

    def delete(self, name: str, account_number: str) -> bool:
        """
        Process account deletion (admin only). Removes the account from the in‑memory repository and logs a
        'delete' transaction.

        :param name: Account holder's name (for verification).
        :param account_number: The account to delete.
        :return: True if successful, False otherwise.
        """

        # Finding account and validating
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Delete', None):
            return False

        # Execute
        self.account_manager.delete(account_number)

        # Log the transaction
        trans_line = Transaction('06', name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Delete of ${name:.2f} successful")

        return True

    def disable(self, name: str, account_number: str) -> bool:
        """
        Process account disable (admin only). Sets account status to 'D' and logs

        :param name: Account holder's name (for verification).
        :param account_number: The account to disable.

        :return: True if successful, False otherwise.
        """

        # Finding account and validating
        account = self.account_manager.find_account(account_number)
        if not self.validate_transaction(account, 'Disable', None):
            return False

        # Execute
        self.account_manager.disable_account(account_number)

        # Log the transaction
        trans_line = Transaction('07', name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Disable successful")

        return True

    def change_plan(self, account_number: str,):
        """
        Process changeplan transaction (admin only). Changes the account plan from student ('SP') to non‑student
        ('NP') and logs a 'changeplan' transaction.

        :param account_number: The account whose plan is to be changed.
        :return: True if successful, False otherwise.
        """

        # Finding account and validating
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'ChangePlan', Decimal('0.00')):
            return False
        if not account.is_student():
            UserInterface.display_error(f"Account {account.holder_name} account is already on non-student account plan")
            return False

        # Execute
        self.account_manager.change_plan(account_number)

        # Log the transaction
        trans_line = Transaction('08', account.holder_name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        # Display Success
        UserInterface.display_success(f"Change plan to non-student is successful")

        return True

    @staticmethod
    def _sufficient_funds(account:BankAccount, amount: Decimal) -> bool:
        """
        Check if the account has at least the requested amount.

        :param account: The account to check.
        :param amount: The amount to withdraw/transfer/pay.
        :return: True if balance ≥ amount, False otherwise.
        """

        if account.balance >= amount:
            return True
        else:
            UserInterface.display_error("Insufficient funds")
            return False

    def _validate_limit(self, trans_type: str, amount: Decimal) -> bool:
        """
        Enforce per‑session transaction limits for standard mode. Limits: withdrawal $500, transfer $1000, paybill $2000.
        (Admin mode bypasses limits.)

        :param trans_type: Type of transaction.
        :param amount: Amount to check.
        :return:
        """

        limits = {
            'withdrawal': (Decimal('500.00'), self.session.withdrawn),
            'transfer': (Decimal('1000.00'), self.session.transferred),
            'paybill': (Decimal('2000.00'), self.session.paid),
        }

        if not trans_type in limits:
            return True # No limits for other transaction types

        # Find the transaction type and its limit from the dictionary
        limit, current = limits[trans_type]

        # Check if the limit is exceeded in this session
        if current + amount > limit and not self.session.is_admin():
            UserInterface.display_error(f"{trans_type} limit exceeded for this session")
            return False

        return True








