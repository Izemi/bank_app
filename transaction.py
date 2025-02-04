import datetime
from decimal import Decimal

class Transaction:
    """
    Represents a bank transaction.
    
    Attributes:
        date: The date of the transaction.
        amount: The transaction amount.
        is_user: True if the transaction is created by the user;
                        False if automatically generated (interest/fee).
    """
    def __init__(self, date: datetime.date, amount: Decimal, is_user: bool):
        self.date = date
        self.amount = amount
        self.is_user = is_user

    def __str__(self) -> str:
        # Format as: YYYY-MM-DD, $<amount with commas and two decimals>
        amount_str = format(self.amount, ",.2f")
        return f"{self.date.isoformat()}, ${amount_str}"
