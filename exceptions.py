class OverdrawError(Exception):
    """Raised when a withdrawal would exceed the account balance."""
    pass


class TransactionSequenceError(Exception):
    """Raised when a new transaction is not in chronological order.
    
    Attributes:
        latest_date (date): The date of the most recent transaction.
    """
    def __init__(self, latest_date, message=None):
        self.latest_date = latest_date
        if message is None:
            message = f"New transactions must be from {latest_date.strftime('%Y-%m-%d')} onward."
        super().__init__(message)


class TransactionLimitError(Exception):
    """Raised when a transaction exceeds the account’s daily or monthly limit.
    
    Attributes:
        limit_type (str): Either 'daily' or 'monthly'.
    """
    def __init__(self, limit_type, message=None):
        self.limit_type = limit_type  # 'daily' or 'monthly'
        if message is None:
            if limit_type == 'daily':
                message = "This transaction could not be completed because this account already has 2 transactions in this day."
            elif limit_type == 'monthly':
                message = "This transaction could not be completed because this account already has 5 transactions in this month."
            else:
                message = "Transaction limit exceeded."
        super().__init__(message)
