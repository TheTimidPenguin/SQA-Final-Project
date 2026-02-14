from decimal import Decimal

from TransactionLog import TransactionLog
from Transaction import Transaction
from BankAccount import BankAccount


class FileHandler:
    """
    Utility class with static methods for parsing the current bank accounts file and for formatting the daily
    transaction file, enforcing fixed-length formats required by banking system
    """
    @staticmethod
    def pad_left(line: str, width: int, pad_char: str = '0') -> str:
        """
        Right‑justify a string by padding on the left.

        :param line: The string to pad.
        :param width: Desired total width.
        :param pad_char: Character used for padding (default '0').

        :return: Padded string of length `width`.
        """
        return str(line).rjust(width, pad_char)

    @staticmethod
    def pad_right(line: str, width: int, pad_char: str = ' ') -> str:
        """
        Left‑justify a string by padding on the left.

        :param line: The string to pad.
        :param width: Desired total width.
        :param pad_char: Character used for padding (default space).

        :return: Padded string of length `width`.
        """
        return str(line).ljust(width, pad_char)

    @staticmethod
    def format_amount(amount: Decimal) -> str:
        """
        Convert a Decimal amount to the 8‑character format required for file (e.g. 150.40 = 00150.40)

        :param amount: The monetary amount.
        :return: 8‑character string with leading zeros and a decimal point.
        """
        dollars = int(amount)
        cents = int((amount - dollars) * 100)
        return f"{dollars:05d}.{cents:02d}"

    @staticmethod
    def parse_account_line(line: str):
        """
        Parse a single 37‑character line from the current bank accounts file.

        :param line: A line from the account file (without newline).
        :return: A new BankAccount object populated with the parsed data.
        """
        if len(line) < 37:
            raise ValueError("line too short")
        acc_num = line[0:5]                                             # 5-digit account number
        name = ' '.join(line[6:26].rstrip(' ').split(" ")).lower()      # Account name
        status = line[29]                                               # Active status
        balance = Decimal(line[30:37].lstrip('0'))                      # Balance
        return BankAccount(acc_num, name, balance, status)

    @staticmethod
    def format_transaction(trn: Transaction) -> str:
        """
        Format a Transaction object into a 40‑character daily transaction record

        :param trn: A Transaction object to record the transaction.
        :return: A 40‑character string ready to be written to the daily file.
        """

        code = FileHandler.pad_left(trn.transaction_code, 2)
        name = FileHandler.pad_right(trn.holders_name[:20], 20)
        account_number = FileHandler.pad_left(trn.account_num, 5)
        amount = FileHandler.format_amount(trn.balance)
        misc = FileHandler.pad_right(trn.misc[:2], 2)

        return f"{code} {name} {account_number} {amount} {misc}"

    @staticmethod
    def write_file(filename: str, trns: TransactionLog):
        """
        Write all transactions from a TransactionLog to the daily transaction file, followed by an end‑of‑session marker
        (code 00).

        :param filename: Path to the output file.
        :param trns: The log containing the session's transactions.
        """
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
        """
        Read the current bank accounts file and return a list of BankAccount objects. Stops reading when an account
        with holder name "END_OF_FILE" is encountered.

        :param filename:Path to the output file.
        :return: List of accounts to read from file
        """
        accounts = []
        with open(filename, 'r') as file:
            for line in file:
                line = line.rstrip('\n')
                if line == "END_OF_FILE":
                    break
                accounts.append(FileHandler.parse_account_line(line))
        return accounts