import os
import sys
import pickle
import logging
from decimal import Decimal, InvalidOperation, getcontext, BasicContext
from datetime import datetime
from bank import Bank
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError

# Configure Decimal context (using ROUND_HALF_UP by default)
getcontext().prec = 28
getcontext().rounding = BasicContext.rounding

# Configure logging to write to bank.log with DEBUG level.
logging.basicConfig(
    filename="bank.log",
    level=logging.DEBUG,
    format="%(asctime)s|%(levelname)s|%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class BankCLI:
    """Driver class for a command-line REPL interface to the Bank application."""
    def __init__(self) -> None:
        self._load()
        self._selected_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._monthly_triggers,
            "7": self._quit,
        }

    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit""")

    def run(self):
        """Displays the menu and responds to choices."""
        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                try:
                    action()
                except AttributeError:
                    # Likely no account selected.
                    print("This command requires that you first select an account.")
                except (OverdrawError, TransactionLimitError, TransactionSequenceError) as e:
                    print(e)
            else:
                print("Invalid choice. Please try again.")

    def _summary(self) -> None:
        for account in self._bank.show_accounts():
            print(account)

    def _load(self) -> None:
        if os.path.exists("bank.pickle"):
            with open("bank.pickle", "rb") as f:
                self._bank = pickle.load(f)
            logging.debug("Loaded from bank.pickle")
        else:
            self._bank = Bank()

    def _save(self) -> None:
        with open("bank.pickle", "wb") as f:
            pickle.dump(self._bank, f)
        logging.debug("Saved to bank.pickle")

    def _quit(self):
        self._save()
        sys.exit(0)

    def _add_transaction(self):
        if self._selected_account is None:
            print("This command requires that you first select an account.")
            return

        # Prompt for a valid amount.
        while True:
            amount_input = input("Amount?\n>")
            try:
                amount = Decimal(amount_input)
            except (InvalidOperation, ValueError):
                print("Please try again with a valid dollar amount.")
                continue
            else:
                break

        # Prompt for a valid date.
        while True:
            date_input = input("Date? (YYYY-MM-DD)\n>")
            try:
                date_val = datetime.strptime(date_input, "%Y-%m-%d").date()
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")
                continue
            else:
                break

        try:
            self._selected_account.add_transaction(amount, date_val)
        except OverdrawError as e:
            print(e)
        except TransactionLimitError as e:
            print(e)
        except TransactionSequenceError as e:
            print(e)

    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        self._bank.add_account(acct_type)

    def _select(self):
        try:
            num = int(input("Enter account number\n>"))
        except ValueError:
            print("Invalid account number.")
            return
        acct = self._bank.get_account(num)
        if acct is None:
            print("Account not found.")
        else:
            self._selected_account = acct

    def _monthly_triggers(self):
        if self._selected_account is None:
            print("This command requires that you first select an account.")
            return
        try:
            self._selected_account.assess_interest_and_fees()
        except TransactionSequenceError as e:
            print(e)

    def _list_transactions(self):
        if self._selected_account is None:
            print("This command requires that you first select an account.")
            return
        for t in self._selected_account.get_transactions():
            print(t)


if __name__ == "__main__":
    try:
        BankCLI().run()
    except Exception as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(f"{type(e).__name__}: {str(e).replace(chr(10), ' ')}")
        sys.exit(0)
