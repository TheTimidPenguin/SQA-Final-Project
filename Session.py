from decimal import Decimal

# Allowed commands for each session mode
COMMANDS_BY_MODE = {
    'admin': {'withdrawal', 'deposit', 'paybill', 'transfer', 'login', 'logout', 'create', 'delete', 'changeplan'},
    'standard': {'withdrawal', 'deposit', 'paybill', 'transfer', 'login', 'logout', }
}

class Session:
    """
    Manages the state of a user session, including login status, mode (standard or admin), the currently logged‑in
    account holder (if any), and cumulative transaction amounts for enforcing per‑session limits.
    """
    def __init__(self):
        self.logged_in = False
        self.mode = None            # standard or admin
        self.current_user = None    # account holder name (None for admin)

        # For session limits
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def login(self, mode: str, user: str = None):
        """
        Log a user into the system.

        :param mode: The session mode – 'standard' or 'admin'.
        :param user: The account holder's name (required for standard mode).
        """
        self.logged_in = True
        self.mode = mode
        self. current_user = user

        # Reset cumulative amounts for a new session
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def logout(self):
        """Log out the user into the system and clear session data"""
        self.logged_in = False
        self.mode = None
        self.current_user = None
        self.withdrawn = Decimal('0.00')
        self.transferred = Decimal('0.00')
        self.paid = Decimal('0.00')

    def is_logged_in(self):
        """ Return True if the user is currently is logged in. False otherwise. """
        return self.logged_in

    def get_current_user(self):
        """ Return the name of the currently logged‑in account holder. None if admin mode or no user is logged in. """
        return self.current_user

    def get_mode(self):
        """Return the current session mode ('standard' or 'admin'), or None if not logged in"""
        return self.mode

    def is_admin(self):
        """ Return True if the current session mode is 'admin'. False otherwise. """
        return self.mode == "admin"

    def can_execute(self, command: str):
        """
        Check whether the given transaction command is allowed in the current session mode.

        :param command: The transaction command (e.g., 'withdrawal').
        :return: True if the command is allowed, False otherwise.
        """
        return command in COMMANDS_BY_MODE[self.mode]

    def session_limit(self, trans_type: str, amount: Decimal):
        """
        Update the cumulative counter for the given transaction type.This is called after a successful transaction
        to track per‑session limits.

        :param trans_type: The type of transaction ('withdrawal', 'transfer', or 'paybill').
        :param amount: The amount involved in the transaction.
        :return:
        """
        if trans_type == 'withdrawal':
            self.withdrawn += amount
        elif trans_type == 'transfer':
            self.transferred += amount
        elif trans_type == 'paybill':
            self.paid += amount
