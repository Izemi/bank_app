import pickle
from account import SavingsAccount, CheckingAccount

class Bank:
    """
    Represents the bank. It stores all accounts and tracks the next available account number.
    """
    def __init__(self):
        self.accounts = []
        self.next_account_number = 1

    def open_account(self, account_type: str):
        """
        Opens a new account of type 'checking' or 'savings'.
        """
        if account_type.lower() == "savings":
            account = SavingsAccount(self.next_account_number)
        elif account_type.lower() == "checking":
            account = CheckingAccount(self.next_account_number)
        else:
            return None  # Should not occur with proper input
        self.accounts.append(account)
        self.next_account_number += 1
        return account

    def get_account_by_number(self, account_number: int):
        """
        Returns the account with the given account number, or None if not found.
        """
        for acc in self.accounts:
            if acc.account_number == account_number:
                return acc
        return None
    
# Save/Load helper functions

def save_bank(bank: Bank, filename: str = "bank.pickle"):
    """Saves the bank object to a pickle file."""
    with open(filename, "wb") as f:
        pickle.dump(bank, f)

def load_bank(filename: str = "bank.pickle") -> Bank:
    """Loads the bank object from a pickle file."""
    with open(filename, "rb") as f:
        return pickle.load(f)
