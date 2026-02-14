from decimal import Decimal

class UserInterface:
    """
    This function handles all user interaction via stdin/stdout. It will provide static methods for displaying menus,
    reading input with validation and showing error/success messages
    """
    @staticmethod
    def display_menu(is_admin: bool):
        """
        Prints the list of available transaction based on session mode

        :param is_admin: True if current user is admin, False otherwise
        """
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
        """
        Repeatedly prompt the user for input until input is validated

        :param prompt: The prompt for the user
        :param validator: A function that validates the user input
        :param error_message: Message to display validation failure reason

        :return: The validated user input (lowercased and stripped)
        """
        while True:
            value = input(prompt).strip().lower()
            try:
                if validator(value):
                    print(value)
                    return value
                else:
                    print(error_message)
            except ValueError as e:
                print(e)

    @staticmethod
    def prompt_mode() -> str:
        """
        Prompts the user to enter session mode (admin/standard) by calling read_input()
        passing prompt, function for validation and error message if validation does not pass

        :return: Validated User input
        """
        return UserInterface.read_input(
            "Enter session mode (admin/standard): ",
            lambda x: x in ("admin", "standard"),
            "Error mode must be 'admin' or 'standard'"
        )

    @staticmethod
    def prompt_account_name() -> str:
        """
        Prompts the user to enter account name (1-20 characters)

        :return: Validated User input
        """
        return UserInterface.read_input(
            "Enter account name: ",
            lambda x: 0 < len(x) <= 20,
            "Error Account name must be between 1-20 characters long"
        )

    @staticmethod
    def prompt_login() -> tuple[str, str]:
        """
        Prompts the user to enter login details (mode and account name)

        :return: tuple (mode, account_name) where account_name is None for admin mode
        """
        mode = UserInterface.prompt_mode()
        if mode == "standard":
            account_name = UserInterface.prompt_account_name()
        else:
            account_name = None

        return mode, account_name

    @staticmethod
    def prompt_account_number() -> str:
        """
        Prompt for an account number (1-5 digits)

        :return: account number (zero-padded)
        """
        value =  UserInterface.read_input(
            "Enter account number: ",
            lambda x: x.isdigit() and len(x) <= 5,
            "Error Account number must be a maximum of 5 digits"
        )
        return value.zfill(5)

    @staticmethod
    def prompt_transaction_type() -> str:
        """
        Prompt the user to enter transaction type (alphanumeric only)

        :return: Transaction type
        """
        return UserInterface.read_input(
            "Enter transaction type: ",
            lambda x: x.isalnum(),
            "Error transaction type must be alphanumeric"
        )


    @staticmethod
    def prompt_amount() -> Decimal:
        """
        Prompt for a monetary amount (positive values only)

        :return: amount for transaction
        """
        value = UserInterface.read_input(
            "Enter amount value: ",
            lambda x: x.isdigit() and x >= 0,
            "Error amount must be entered and cannot be negative"
        )
        return Decimal(value)

    @staticmethod
    def prompt_company_code() -> str:
        """
        Prompt the user to enter company code (EC, CQ, FI)

        :return: User selected company code
        """
        valid = {'ec', 'cq', 'fi'}
        return UserInterface.read_input(
            "Enter company code (EC/CQ/FI): ",
            lambda x: x in valid,
            "Error company code must be one of 'EC', 'CQ', 'FI'"
        )

    @staticmethod
    def display_error(msg: str):
        """Print an error message to screen"""
        print(f"Error: {msg}")

    @staticmethod
    def display_success(msg: str):
        """print a success message to screen"""
        print({msg})