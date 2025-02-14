from decimal import Decimal
import logging
from transactions import Transaction
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError

class Account:
    """Abstract base class for accounts. Provides default functionality for transactions,
    balance calculation, and interest/fee assessment. Should be subclassed as SavingsAccount or CheckingAccount.
    """

    def __init__(self, acct_num) -> None:
        self._transactions = []
        self._account_number = acct_num
        # Track the month (year, month) in which interest/fees have been applied.
        self._interest_applied_month = None

    def _get_acct_num(self) -> int:
        return self._account_number

    account_number = property(_get_acct_num)

    def add_transaction(self, amt, date, exempt=False) -> None:
        """Creates a new transaction, enforcing sequence order, balance, and limit rules.

        Args:
            amt (Decimal): Dollar amount.
            date (date): Date of transaction.
            exempt (bool, optional): If True, bypasses balance and limit checks.
        """
        t = Transaction(amt, date, exempt=exempt)

        # Enforce chronological order.
        if self._transactions:
            latest = max(self._transactions)
            if t._date < latest._date:
                raise TransactionSequenceError(latest._date)

        # For non-exempt transactions, check balance (this will raise OverdrawError if needed)
        if not t.is_exempt():
            t.check_balance(self.get_balance())

        # Check limits (subclasses may raise TransactionLimitError).
        self._check_limits(t)

        self._transactions.append(t)
        logging.debug(f"Created transaction: {self._account_number}, {amt}")

    def _check_balance(self, t) -> bool:
        """Checks whether a transaction would overdraw the account.
        
        Returns:
            bool: True if acceptable.
        """
        return t.check_balance(self.get_balance())

    def _check_limits(self, t) -> bool:
        """Default implementation; subclasses may override.
        
        Returns:
            bool: Always True.
        """
        return True

    def get_balance(self) -> Decimal:
        """Calculates the current balance by summing transactions.
        
        Returns:
            Decimal: Current balance.
        """
        return sum(self._transactions, Decimal("0"))

    def _assess_interest(self, latest_transaction) -> None:
        """Calculates interest and adds it as a new exempt transaction."""
        interest_amt = self.get_balance() * self._interest_rate
        self.add_transaction(interest_amt, date=latest_transaction.last_day_of_month(), exempt=True)

    def _assess_fees(self, latest_transaction) -> None:
        """Assesses fees; default is no fee."""
        pass

    def assess_interest_and_fees(self) -> None:
        """Applies interest and fees for this account, ensuring they’re applied only once per month."""
        if not self._transactions:
            return
        latest_transaction = max(self._transactions)
        trigger_date = latest_transaction.last_day_of_month()

        # Check if interest/fees have already been applied for this month.
        if self._interest_applied_month == (trigger_date.year, trigger_date.month):
            raise TransactionSequenceError(
                latest_transaction._date,
                f"Cannot apply interest and fees again in the month of {latest_transaction._date.strftime('%B')}."
            )

        logging.debug("Triggered interest and fees")
        self._assess_interest(latest_transaction)
        self._assess_fees(latest_transaction)
        self._interest_applied_month = (trigger_date.year, trigger_date.month)

    def __str__(self) -> str:
        """Formats the account number and balance.
        For example: '#000000001,	balance: $50.00'
        """
        return f"#{self._account_number:09},\tbalance: ${self.get_balance():,.2f}"

    def get_transactions(self) -> list:
        "Returns a sorted list of transactions on this account."
        return sorted(self._transactions)


class SavingsAccount(Account):
    """SavingsAccount with daily and monthly transaction limits and higher interest."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0033")
        self._daily_limit = 2
        self._monthly_limit = 5

    def _check_limits(self, t1) -> bool:
        """Checks whether the transaction exceeds daily or monthly limits.
        
        Raises:
            TransactionLimitError: If a limit is exceeded.
        """
        num_today = len(
            [t2 for t2 in self._transactions if (not t2.is_exempt()) and t2.in_same_day(t1)]
        )
        num_this_month = len(
            [t2 for t2 in self._transactions if (not t2.is_exempt()) and t2.in_same_month(t1)]
        )
        if num_today >= self._daily_limit:
            raise TransactionLimitError('daily')
        if num_this_month >= self._monthly_limit:
            raise TransactionLimitError('monthly')
        return True

    def __str__(self) -> str:
        """Formats as 'Savings#<acctnum>,	balance: $<balance>'."""
        return "Savings" + super().__str__()


class CheckingAccount(Account):
    """CheckingAccount with lower interest and low balance fees."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0008")
        self._balance_threshold = 100
        self._low_balance_fee = Decimal("-5.75")

    def _assess_fees(self, latest_transaction) -> None:
        """Assesses a fee if the balance is below a threshold."""
        if self.get_balance() < self._balance_threshold:
            self.add_transaction(self._low_balance_fee, date=latest_transaction.last_day_of_month(), exempt=True)

    def __str__(self) -> str:
        """Formats as 'Checking#<acctnum>,	balance: $<balance>'."""
        return "Checking" + super().__str__()
