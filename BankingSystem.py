from decimal import Decimal

from AccountsManager import AccountsManager
from FileHandler import FileHandler
from Session import Session
from TransactionLog import TransactionLog
from TransactionProcessor import TransactionProcessor
from UserInterface import UserInterface


class BankingSystem:
    """
    Main application controller for banking system front end functionality. Will be the one to arrange the login/logout,
    display menus, user commands, and delegates transaction processing to TransactionProcessor.
    """

    # For mapping transaction command strings to the corresponding handler method names
    COMMAND_HANDLERS = {
        'logout': '_process_logout',
        'withdrawal': '_handle_withdrawal',
        'transfer': '_handle_transfer',
        'paybill': '_handle_paybill',
        'deposit': '_handle_deposit',
        'create': '_handle_create',
        'delete': '_handle_delete',
        'disable': '_handle_disable',
        'changeplan': '_handle_changeplan',
    }

    def __init__(self):
        """Initialise the banking system and file paths."""
        self.session = Session()
        self.account_manager = AccountsManager()
        self.log = TransactionLog()
        self.file_handler = FileHandler()
        self.ui = UserInterface()
        self.transaction_processor = TransactionProcessor(self.account_manager, self.session, self.log)
        self.current_accounts_file = "current_bank_accounts.txt"
        self.daily_transaction_file = "daily_bank_transactions.txt"

    def run(self):
        """
        Main execution loop. Attempts login first; if successful, repeatedly displays the menu, reads a command, and
        dispatches it to the appropriate handler.
        """
        if self._process_login():
            while True:
                self.ui.display_menu(self.session.is_admin())
                cmd = self.ui.prompt_transaction_type()
                if cmd == "logout":
                    self._process_logout()
                elif not self.session.can_execute(cmd):
                    self.ui.display_error("You are not authorized to perform this transaction.")
                else:
                    getattr(self, self.COMMAND_HANDLERS[cmd])()

    def _check_login(self) ->bool: #Lowkey redundant remove after checking
        """
        Verify that the user is already logged in. Displays an error and returns False if not logged in.

        :return: True if logged in, False otherwise.
        """
        if self.session.is_logged_in():
            self.ui.display_error("Already logged in. Please log out first.")
            return False
        else:
            return True

    def _process_login(self):
        """
        Handle Login sequence:
            - Prompt user for mode and account (if standard)
            - Load accounts file
            - Validate the account exists for standard mode
            - create session if all is good
        :return: True if login succeeded, False otherwise.
        """

        #Prevent double login
        if self._check_login():
            return False

        mode, user = self.ui.prompt_login()

        # Load accounts from file; error if file cannot be read
        if not self.account_manager.load_accounts(self.current_accounts_file):
            self.ui.display_error("Failed to load accounts. Please try again.")
            return False

        # For standard mode, check that the account holder exists
        if mode == 'standard':
            account = self.account_manager.find_account_by_name(user)
            if not account:
                self.ui.display_error(f"No account found for holder '{user}'.")
                return False

        # All checks are good - login
        self.session.login(mode, user)
        self.ui.display_success(f"Successfully logged in. Mode: {mode}")
        if mode == 'standard':
            print(f"Logged in as: {user}")

        return True


    def _process_logout(self):
        """
        Handle logout:
        - Write the daily transaction file.
        - Clear the transaction log.
        - End the session.
        """
        if self._check_login():
            self.log.write_session_file(self.daily_transaction_file)
            self.log.clear()
            self.session.logout()
            self.ui.display_success(f"Successfully logged out. Mode: {self.session.mode}")

    # =========================TRANSACTION HANDLERS=========================

    def _handle_withdrawal(self):
        """Get withdrawal input and call transaction_processor.withdrawal()."""
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.withdrawal(account_number, amount)

    def _handle_transfer(self):
        """Get transfer input and call transaction_processor.transfer()."""
        from_account = self.ui.prompt_account_number()
        to_account = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.transfer(from_account, to_account, amount)

    def _handle_paybill(self):
        """Get paybill input and call transaction_processor.paybill()."""
        account_number = self.ui.prompt_account_number()
        company = self.ui.prompt_company_code()
        amount = self.ui.prompt_amount()
        self.transaction_processor.paybill(account_number, company, amount)

    def _handle_deposit(self):
        """Get deposit input and call transaction_processor.deposit()."""
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.deposit(account_number, amount)

    def _handle_create(self):
        """Get create input and call transaction_processor.create()."""
        name = self.ui.prompt_account_name()
        amount = self.ui.prompt_amount()

        #Constraint for account creation: initial balance cannot exceed 99999.99
        if amount > Decimal(99999.99):
            self.ui.display_error("Amount cannot be greater than 99999.99.")
            return
        self.transaction_processor.create(name, amount)

    def _handle_delete(self):
        """Get delete input and call transaction_processor.delete()."""
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.delete(name, account_number)

    def _handle_disable(self):
        """Get disable input and call transaction_processor.disable()."""
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.disable(name, account_number)

    def _handle_changeplan(self):
        """Get changeplan input and call transaction_processor.changeplan()."""
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.change_plan(account_number)

def main():
    """Create BankingSystem and run."""
    system = BankingSystem()
    system.run()

if __name__ == "__main__":
    main()

