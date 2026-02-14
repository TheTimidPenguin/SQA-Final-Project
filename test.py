from decimal import Decimal

class BankAccount:
    def __init__(self, account_number : str, holder_name : str, balance: Decimal, status: str = 'A', plan: str = 'SP'):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance
        self.status = status
        self.plan = plan

    def is_active(self) -> bool:
        return self.status == 'A'

    def is_student(self) -> bool:
        return self.plan == 'S'

    def balance_deduction(self, amount: Decimal):
        self.balance -= amount

    def balance_addition(self, amount: Decimal):
        self.balance += amount

    def disable(self):
        self.status = 'D'

class UserInterface:

    @staticmethod
    def display_menu(is_admin: bool):
        print("\n========Your Available Transactions========\n")
        print("withdrawal\n")
        print("transfer\n")
        print("paybill\n")
        print("deposit\n")
        if is_admin:
            print("create\n")
            print("delete\n")
            print("disable\n")
            print("changeplan\n")
        print("logout\n")
        print("============================================\n")

    @staticmethod
    def read_input(prompt: str, validator, error_message: str) -> str:
        while True:
            value = input(prompt).strip().lower()
            try:
                if validator(value):
                    print(value)
                    return value
            except Exception:
                print(error_message)

    @staticmethod
    def prompt_mode():
        return UserInterface.read_input(
            "Enter session mode (admin/standard): ",
            lambda x: x in ("admin", "standard"),
            "Error mode must be 'admin' or 'standard'"
        )

    @staticmethod
    def prompt_account_name():
        return UserInterface.read_input(
            "Enter account name: ",
            lambda x: 0 < len(x) <= 20,
            "Error Account name must be between 1-20 characters long"
        )

    @staticmethod
    def prompt_login() -> tuple[str, str]:
        mode = UserInterface.prompt_mode()
        if mode == "standard":
            account_name = UserInterface.prompt_account_name()
        else:
            account_name = None

        return mode, account_name

    @staticmethod
    def prompt_account_number():
        value =  UserInterface.read_input(
            "Enter account number: ",
            lambda x: x.isdigit() and len(x) <= 5,
            "Error Account number must be a maximum of 5 digits"
        )
        return value.zfill(5)

    @staticmethod
    def prompt_transaction_type():
            return UserInterface.read_input(
                "Enter transaction type: ",
                lambda x: x.isalnum(),
                "Error transaction type must be alphanumeric"
            )


    @staticmethod
    def prompt_amount():
        value = UserInterface.read_input(
            "Enter amount value: ",
            lambda x: Decimal(x) >= 0,
            "Error amount must be entered and cannot be negative"
        )
        return Decimal(value)

    @staticmethod
    def prompt_company_code() -> str:
        valid = {'ec', 'cq', 'fi'}
        return UserInterface.read_input(
            "Enter company code (EC/CQ/FI): ",
            lambda x: x in valid,
            "Error company code must be one of 'EC', 'CQ', 'FI'"
        )

    @staticmethod
    def display_error(msg: str):
        print(f"Error: {msg}")

    @staticmethod
    def display_success(msg: str):
        print({msg})

class FileHandler:

    @staticmethod
    def pad_left(line: str, width: int, pad_char: str = '0') -> str:
        return str(line).rjust(width, pad_char)

    @staticmethod
    def pad_right(line: str, width: int, pad_char: str = ' ') -> str:
        return str(line).ljust(width, pad_char)

    @staticmethod
    def format_amount(amount: Decimal) -> str:
        dollars = int(amount)
        cents = int((amount - dollars) * 100)
        return f"{dollars:05d}.{cents:02d}"

    @staticmethod
    def parse_account_line(line: str):
        if len(line) < 37:
            raise ValueError("line too short")
            # add something so that users can also be notified
        acc_num = line[0:5]
        name = ' '.join(line[6:26].rstrip(' ').split(" ")).lower()
        status = line[27]
        balance = Decimal(line[30:37].lstrip('0'))
        print(acc_num, name, balance, status)
        return BankAccount(acc_num, name, balance, status)

    @staticmethod
    def format_transaction(trn: Transaction) -> str:

        code = FileHandler.pad_left(trn.transaction_code, 2)
        name = FileHandler.pad_right(trn.holders_name[:20], 20)
        account_number = FileHandler.pad_left(trn.account_num, 5)
        amount = FileHandler.format_amount(trn.balance)
        misc = FileHandler.pad_right(trn.misc[:2], 2)

        return f"{code} {name} {account_number} {amount} {misc}"

    @staticmethod
    def write_file(filename: str, trns: TransactionLog):
        try:
            with open(filename, 'w') as f:
                for file in trns.get_transactions():
                    f.write(file.format() + '\n')
                end_txn = Transaction('00', '', '00000', Decimal('0.00'), '')
                f.write(end_txn.format() + '\n')
        except IOError as e:
            print(f"Error writing transaction file '{filename}': {e}")

    @staticmethod
    def read_file(filename: str) -> list[BankAccount]:
        accounts = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.rstrip('\n')
                if line == "END_OF_FILE":
                    break
                accounts.append(FileHandler.parse_account_line(line))
        return accounts

class AccountsManager:
    def __init__(self):
        self.accounts = {}

    def load_accounts(self, filename: str) -> bool:
        try:
            accounts = FileHandler.read_file(filename)
            for account in accounts:
                self.accounts[account.account_number] = account
            return True
        except (IOError, ValueError) as e:
            print(f"error: cannot read account file '{filename}' - {e}")
            return False

    def find_account(self, account_number: str):
        return self.accounts.get(account_number)

    def find_account_by_name(self, name: str):
        return [account for account in self.accounts.values() if account.holder_name == name]

    @staticmethod
    def debit(account: BankAccount, amount: Decimal):
        if account:
            account.balance_deduction(amount)

    @staticmethod
    def credit(account: BankAccount, amount: Decimal):
        account.balance_addition(amount)

    def disable_account(self, account_number: str):
        account = self.find_account(account_number)
        if account:
            account.disable()

    def delete(self, account_number: str):
        if account_number in self.accounts:
            del self.accounts[account_number]

    def change_plan(self, account_number: str):
        account = self.find_account(account_number)
        if account and account.is_student():
            account.plan = 'NP'

    def generate_new_account_number(self) -> str:
        if not self.accounts:
            return "00001"
        max_num = max(int(num) for num in self.accounts.keys())
        return f"{max_num + 1:05d}"

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

class Transaction:
    def __init__(self, transaction_code: str, holders_name: str, account_num: str, balance: Decimal, misc: str = ''):
        self.transaction_code = transaction_code
        self.holders_name = holders_name
        self.account_num = account_num
        self.balance = balance
        self.misc = misc

    def format(self):
        return FileHandler.format_transaction(self)

    def get_transaction_code(self):
        return self.transaction_code

    def get_holders_name(self):
        return self.holders_name

    def get_balance(self):
        return self.balance

    def get_misc(self):
        return self.misc

class TransactionProcessor:

    def __init__(self, account_manager: AccountsManager, session: Session, trans_log: TransactionLog):
        self.account_manager = account_manager
        self.session = session
        self.trans_log = trans_log

    def validate_transaction(self, account: BankAccount, transaction_type: str, amount: Decimal = None) -> bool:
        if not account:
            UserInterface.display_error("Account does not exist")
            return False
        if not account.is_active():
            UserInterface.display_error(f"Account {account.holder_name} is disabled")
            return False
        if not self.session.is_admin() and self.session.current_user != account.holder_name:
            UserInterface.display_error(f"Account {account.holder_name} does not belong to you")
            return False

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
        return self.account_manager.find_account(account_number)

    def withdrawal(self, account_number: str, amount: Decimal) -> bool:
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Withdrawal', amount):
            return False

        self.account_manager.debit(account, amount)
        self.session.session_limit('withdrawal', amount)

        trans_line = Transaction('01', account.holder_name, account_number,amount, '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Withdrawal of ${amount:.2f} successful")

        return True

    def transfer(self, from_account_num: str, to_account_num: str, amount: Decimal) -> bool:
        from_account = self.find_current_user(from_account_num)
        if not self.validate_transaction(from_account, 'Transfer', amount):
            return False

        to_account = self.find_current_user(to_account_num)
        if not self.validate_transaction(to_account, 'Transfer', amount):
            return False

        self.account_manager.debit(from_account, amount)
        self.account_manager.credit(to_account, amount)
        self.session.session_limit('transfer', amount)

        trans_line = Transaction('02', from_account.holder_name, from_account_num,amount, '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Transfer of ${amount:.2f} successful")

        return True

    def paybill(self, account_number: str, company: str, amount: Decimal) -> bool:
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'PayBill', amount):
            return False

        self.account_manager.debit(account, amount)
        self.session.session_limit('paybill', amount)

        trans_line = Transaction('03', account.holder_name, account_number,amount, company)
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"PayBill of ${amount:.2f} successful")

        return True

    def deposit(self, account_number: str, amount: Decimal) -> bool:
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Deposit', amount):
            return False

        self.account_manager.credit(account, amount)

        trans_line = Transaction('04', account.holder_name, account_number,amount, '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Deposit of ${amount:.2f} successful")

        return True

    def create(self, name: str, initial_balance: Decimal):
        new_account_num = self.account_manager.generate_new_account_number()

        trans_line = Transaction('05', name, new_account_num, initial_balance, '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Creation of ${initial_balance:.2f} successful")

        return new_account_num

    def delete(self, name: str, account_number: str) -> bool:
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'Delete', None):
            return False

        self.account_manager.delete(account_number)

        trans_line = Transaction('06', name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Delete of ${name:.2f} successful")
        return True

    def disable(self, name: str, account_number: str) -> bool:
        account = self.account_manager.find_account(account_number)
        if not self.validate_transaction(account, 'Disable', None):
            return False

        self.account_manager.disable_account(account_number)

        trans_line = Transaction('07', name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Disable successful")

        return True

    def change_plan(self, account_number: str,):
        account = self.find_current_user(account_number)
        if not self.validate_transaction(account, 'ChangePlan', Decimal('0.00')):
            return False
        if not account.is_student():
            UserInterface.display_error(f"Account {account.holder_name} account is already on non-student account plan")
            return False

        self.account_manager.change_plan(account_number)
        trans_line = Transaction('08', account.holder_name, account_number, Decimal('0.00'), '')
        self.trans_log.add_transaction(trans_line)

        UserInterface.display_success(f"Change plan to non-student is successful")

        return True


    def _validate_ownership(self, account:BankAccount) -> bool:
        if self.session.current_user == account.holder_name:
            return True
        else:
            UserInterface.display_error("Account does not belong to you")
            return False

    @staticmethod
    def _sufficient_funds(account:BankAccount, amount: Decimal) -> bool:
        if account.balance >= amount:
            return True
        else:
            UserInterface.display_error("Insufficient funds")
            return False

    def _validate_limit(self, trans_type: str, amount: Decimal) -> bool:
        limits = {
            'withdrawal': (Decimal('500.00'), self.session.withdrawn),
            'transfer': (Decimal('1000.00'), self.session.transferred),
            'paybill': (Decimal('2000.00'), self.session.paid),
        }
        if not trans_type in limits:
            return True

        limit, current = limits[trans_type]
        if current + amount > limit and not self.session.is_admin():
            UserInterface.display_error(f"{trans_type} limit exceeded for this session")
            return False

        return True

COMMANDS_BY_MODE = {
    'admin': {'withdrawal', 'deposit', 'paybill', 'transfer', 'login', 'logout', 'create', 'delete', 'changeplan'},
    'standard': {'withdrawal', 'deposit', 'paybill', 'transfer', 'login', 'logout', }
}

class Session:
    def __init__(self):
        self.logged_in = False
        self.mode = None            # standard or admin
        self.current_user = None    # account holder name (None for admin)
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def login(self, mode: str, user: str = None):
        self.logged_in = True
        self.mode = mode
        self. current_user = user
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def logout(self):
        self.logged_in = False
        self.mode = None
        self.current_user = None
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def is_logged_in(self):
        return self.logged_in

    def get_current_user(self):
        return self.current_user

    def get_mode(self):
        return self.mode

    def is_admin(self):
        return self.mode == "admin"

    def can_execute(self, command: str):
        return command in COMMANDS_BY_MODE[self.mode]

    def session_limit(self, trans_type: str, amount: Decimal):
        if trans_type == 'withdrawal':
            self.withdrawn += amount
        elif trans_type == 'transfer':
            self.transferred += amount
        elif trans_type == 'paybill':
            self.paid += amount


class BankingSystem:
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
        self.session = Session()
        self.account_manager = AccountsManager()
        self.log = TransactionLog()
        self.file_handler = FileHandler()
        self.ui = UserInterface()
        self.transaction_processor = TransactionProcessor(self.account_manager, self.session, self.log)
        self.current_accounts_file = "current_bank_accounts.txt"
        self.daily_transaction_file = "daily_bank_transactions.txt"

    def run(self):
        if self._process_login():
            while True:
                self.ui.display_menu(self.session.is_admin())
                cmd = self.ui.prompt_transaction_type()
                if cmd == "logout":
                    self._process_logout()
                    break
                elif not self.session.can_execute(cmd):
                    self.ui.display_error("You are not authorized to perform this transaction.")
                else:
                    getattr(self, self.COMMAND_HANDLERS[cmd])()

    def _check_login(self) ->bool:
        if self.session.is_logged_in():
            self.ui.display_error("Already logged in. Please log out first.")
            return False
        else:
            return True

    def _process_login(self):

        if self.session.is_logged_in():
            self.ui.display_error("Already logged in. Please log out first.")
            return False

        mode, user = self.ui.prompt_login()

        if not self.account_manager.load_accounts(self.current_accounts_file):
            self.ui.display_error("Failed to load accounts. Please try again.")
            return False

        if mode == 'standard':
            account = self.account_manager.find_account_by_name(user)
            if not account:
                self.ui.display_error(f"No account found for holder '{user}'.")
                return False

        self.session.login(mode, user)
        self.ui.display_success(f"Successfully logged in. Mode: {mode}")
        if mode == 'standard':
            print(f"Logged in as: {user}")
        return True


    def _process_logout(self):
        if self.session.is_logged_in():
            self.log.write_session_file(self.daily_transaction_file)
            self.log.clear()
            self.session.logout()
            self.ui.display_success(f"Successfully logged out. Mode: {self.session.mode}")

    def _handle_withdrawal(self):
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.withdrawal(account_number, amount)

    def _handle_transfer(self):
        from_account = self.ui.prompt_account_number()
        to_account = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.transfer(from_account, to_account, amount)

    def _handle_paybill(self):
        account_number = self.ui.prompt_account_number()
        company = self.ui.prompt_company_code()
        amount = self.ui.prompt_amount()
        self.transaction_processor.paybill(account_number, company, amount)

    def _handle_deposit(self):
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.deposit(account_number, amount)

    def _handle_create(self):
        name = self.ui.prompt_account_name()
        amount = self.ui.prompt_amount()
        if amount > Decimal(99999.99):
            self.ui.display_error("Amount cannot be greater than 99999.99.")
            return
        self.transaction_processor.create(name, amount)

    def _handle_delete(self):
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.delete(name, account_number)

    def _handle_disable(self):
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.disable(name, account_number)

    def _handle_changeplan(self):
        name = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.change_plan(account_number)

def main():
    system = BankingSystem()
    system.run()

if __name__ == "__main__":
    main()

