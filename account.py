from decimal import Decimal
import datetime
import calendar
from transaction import Transaction

class Account:
    """
    Base class for a bank account.
    
    Attributes:
        account_number (int): The account’s unique number.
        transactions (list[Transaction]): A list of transactions.
    """
    def __init__(self, account_number: int):
        self.account_number = account_number
        self.transactions = []

    def get_balance(self) -> Decimal:
        """Return the sum of all transaction amounts."""
        total = Decimal("0.00")
        for t in self.transactions:
            total += t.amount
        return total

    def add_transaction(self, amount: Decimal, date: datetime.date, is_user: bool = True):
        """
        Adds a transaction to the account.
        """
        if is_user:
            # A user transaction may not result in a negative balance.
            if self.get_balance() + amount < 0:
                return  # transaction rejected
        self.transactions.append(Transaction(date, amount, is_user))

    def list_transactions(self):
        """
        Returns the account’s transactions sorted by date.
        """
        return sorted(self.transactions, key=lambda t: t.date)

    def summary_str(self) -> str:
        """
        Returns a summary string for the account.
        """
        balance_str = format(self.get_balance(), ",.2f")
        return f"{self.get_account_type()}#{self.account_number:09d},\tbalance: ${balance_str}"

    def __str__(self) -> str:
        """
        Returns the string used to display the currently selected account.
        """
        balance_str = format(self.get_balance(), ",.2f")
        return f"{self.get_account_type()}#{self.account_number:09d},\tbalance: ${balance_str}"

    def get_account_type(self) -> str:
        """Return the account type (to be overridden in subclasses)."""
        return "Account"

    def get_interest_rate(self) -> Decimal:
        """Return the monthly interest rate (to be overridden in subclasses)."""
        return Decimal("0.00")

    def apply_interest_and_fees(self):
        """
        Applies interest (and fees for checking accounts).
        """
        # Find the latest user-created transaction date (if any)
        latest_date = None
        for t in self.transactions:
            if t.is_user:
                if latest_date is None or t.date > latest_date:
                    latest_date = t.date
        if latest_date is None:
            latest_date = datetime.date.today()
        # Compute last day of that month.
        last_day = calendar.monthrange(latest_date.year, latest_date.month)[1]
        interest_date = datetime.date(latest_date.year, latest_date.month, last_day)

        # Calculate interest (balance * monthly rate)
        interest_rate = self.get_interest_rate()
        interest_amount = self.get_balance() * interest_rate

        # Add the interest transaction (bypasses user checks)
        self.add_transaction(interest_amount, interest_date, is_user=False)

        # For Checking accounts, if balance is less than $100 after interest, add fee.
        if self.get_account_type() == "Checking":
            if self.get_balance() < Decimal("100"):
                fee_amount = Decimal("-5.75")
                self.add_transaction(fee_amount, interest_date, is_user=False)

class SavingsAccount(Account):
    """
    Savings account with transaction limits:
      - No more than 2 user transactions per day.
      - No more than 5 user transactions per month.
    """
    def get_account_type(self) -> str:
        return "Savings"

    def get_interest_rate(self) -> Decimal:
        return Decimal("0.0033")

    def add_transaction(self, amount: Decimal, date: datetime.date, is_user: bool = True):
        if is_user:
            # Enforce daily limit: at most 2 user transactions on the same day.
            day_count = sum(1 for t in self.transactions if t.is_user and t.date == date)
            if day_count >= 2:
                return
            # Enforce monthly limit: at most 5 user transactions in the same month.
            month_count = sum(
                1 for t in self.transactions
                if t.is_user and t.date.year == date.year and t.date.month == date.month
            )
            if month_count >= 5:
                return
            # Also check that the transaction would not overdraw the account.
            if self.get_balance() + amount < 0:
                return
        # (Auto transactions bypass these limits.)
        self.transactions.append(Transaction(date, amount, is_user))

class CheckingAccount(Account):
    """
    Checking account without per-day/month limits.
    Overdraft is prevented for user transactions.
    Low-balance fees (if balance is below $100) are applied after interest.
    """
    def get_account_type(self) -> str:
        return "Checking"

    def get_interest_rate(self) -> Decimal:
        return Decimal("0.0008")
    # Inherits add_transaction from Account (which prevents overdrafts on user transactions)
