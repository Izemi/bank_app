from datetime import date, timedelta
from decimal import Decimal
from exceptions import OverdrawError

class Transaction:
    def __init__(self, amt, date, exempt=False):
        """
        Args:
            amt (Decimal): Dollar amount of the transaction.
            date (date): Date the transaction was created.
            exempt (bool, optional): Whether the transaction is exempt from limits. Defaults to False.
        """       
        self._amt = amt
        self._date = date
        self._exempt = exempt

    def __str__(self) -> str:
        """Formats the date and amount of this transaction.
        For example: '2022-09-15, $50.00'
        """
        return f"{self._date}, ${self._amt:,.2f}"

    def is_exempt(self) -> bool:
        "Check if the transaction is exempt from account limits."
        return self._exempt

    def in_same_day(self, other) -> bool:
        "Checks whether this transaction shares the same date as another."
        return self._date == other._date

    def in_same_month(self, other) -> bool:
        "Checks whether this transaction shares the same month and year as another."
        return self._date.month == other._date.month and self._date.year == other._date.year

    def __radd__(self, other) -> Decimal:
        "Allows summing transactions by adding their amounts."
        return other + self._amt

    def check_balance(self, balance) -> bool:
        """Checks whether this transaction would overdraw the account.
        
        Raises:
            OverdrawError: If the withdrawal exceeds the balance.
        
        Returns:
            bool: True if the transaction is acceptable.
        """
        if self._amt < 0 and balance < abs(self._amt):
            raise OverdrawError("This transaction could not be completed due to an insufficient account balance.")
        return True

    def __lt__(self, other) -> bool:
        "Compares transactions by date."
        return self._date < other._date

    def last_day_of_month(self) -> date:
        "Returns the last day of the month for this transaction's date."
        first_of_next_month = date(self._date.year + self._date.month // 12,
                                   self._date.month % 12 + 1, 1)
        return first_of_next_month - timedelta(days=1)
