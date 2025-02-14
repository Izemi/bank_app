import os
import pickle
import logging
from accounts import SavingsAccount, CheckingAccount

SAVINGS = "savings"
CHECKING = "checking"

class Bank:
    """Represents a bank that manages multiple accounts."""
    def __init__(self) -> None:
        self._accounts = []

    def add_account(self, acct_type) -> None:
        """Creates a new account (Savings or Checking) and adds it to the bank.
        
        Args:
            acct_type (str): "savings" or "checking".
        """
        acct_num = self._generate_account_number()
        if acct_type.lower() == SAVINGS:
            a = SavingsAccount(acct_num)
        elif acct_type.lower() == CHECKING:
            a = CheckingAccount(acct_num)
        else:
            return None
        self._accounts.append(a)
        logging.debug(f"Created account: {acct_num}")

    def _generate_account_number(self) -> int:
        return len(self._accounts) + 1

    def show_accounts(self) -> list:
        "Returns a list of accounts."
        return self._accounts

    def get_account(self, account_num) -> "Account" or None:
        """Fetches an account by its number.
        
        Args:
            account_num (int): Account number to search for.
        
        Returns:
            Account: Matching account, or None if not found.
        """
        for x in self._accounts:
            if x.account_number == account_num:
                return x
        return None
