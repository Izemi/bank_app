"""
A simple bank application with a command‐line interface. This application supports:
  - Opening checking 
  - Displaying an account summary 
  - Selecting an account to work with
  - Adding transactions 
  - Listing transactions 
  - Applying monthly interest 
  - Saving (when quitting) and loading the bank’s data (using pickle)
"""

import sys
import os
import datetime
from decimal import Decimal, getcontext, ROUND_HALF_UP
from bank import Bank, save_bank, load_bank

# Global rounding so that Decimal quantization rounds half‐up.
getcontext().rounding = ROUND_HALF_UP

def safe_input(prompt: str) -> str:
    """
    Wrapper for input() that exits gracefully if EOF is encountered.
    """
    try:
        return input(prompt)
    except EOFError:
        sys.exit(0)

def main():
    """
    Main command-line loop.
    
    When starting, if bank.pickle exists, it is loaded.
    The program always displays the simple menu:
    
      1: open account
      2: summary
      3: select account
      4: add transaction
      5: list transactions
      6: interest and fees
      7: quit
    
    When quitting, the bank is saved.
    """
    # Load bank from pickle if available; otherwise, create a new bank.
    if os.path.exists("bank.pickle"):
        try:
            bank = load_bank("bank.pickle")
        except Exception:
            bank = Bank()
    else:
        bank = Bank()

    current_account = None

    while True:
        print("-" * 32)
        if current_account is None:
            print("Currently selected account: None")
        else:
            print(f"Currently selected account: {current_account}")
        print("Enter command")
        print("1: open account")
        print("2: summary")
        print("3: select account")
        print("4: add transaction")
        print("5: list transactions")
        print("6: interest and fees")
        print("7: quit")
        command = safe_input(">").strip()
        try:
            cmd = int(command)
        except ValueError:
            continue  # per assumptions, inputs are valid

        if cmd == 1:
            acc_type = safe_input("Type of account? (checking/savings)\n>").strip()
            bank.open_account(acc_type)
        elif cmd == 2:
            for acc in bank.accounts:
                print(acc.summary_str())
        elif cmd == 3:
            acc_num_str = safe_input("Enter account number\n>").strip()
            try:
                acc_num = int(acc_num_str)
            except ValueError:
                continue
            account = bank.get_account_by_number(acc_num)
            if account is not None:
                current_account = account
        elif cmd == 4:
            if current_account is None:
                continue
            amt_str = safe_input("Amount?\n>").strip()
            try:
                amt = Decimal(amt_str)
            except Exception:
                continue
            date_str = safe_input("Date? (YYYY-MM-DD)\n>").strip()
            try:
                trans_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                continue
            current_account.add_transaction(amt, trans_date, is_user=True)
        elif cmd == 5:
            if current_account is None:
                continue
            for t in current_account.list_transactions():
                print(t)
        elif cmd == 6:
            if current_account is None:
                continue
            current_account.apply_interest_and_fees()
        elif cmd == 7:
            save_bank(bank, "bank.pickle")
            sys.exit(0)

if __name__ == "__main__":
    main()
