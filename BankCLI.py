import sys
import pickle
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging

from Bank import Bank
from Transactions import Transaction
from Accounts import OverdrawError, TransactionLimitError, TransactionSequenceError


class BankCLI():
    def __init__(self):
        self._bank = Bank()
        self._selected_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._list_transactions,
            "5": self._add_transaction,
            "6": self._monthy_triggers,
            "7": self._save,
            "8": self._load,
            "9": self._quit,
        }


    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: list transactions
5: add transaction
6: interest and fees
7: save
8: load
9: quit""")

    def run(self):        
        """Display the menu and respond to choices."""

        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                try:
                    action()
                except TransactionSequenceError as err:
                    print("New transactions must be from %s onward.\n" %(err.latest_date))
                    break
                except AttributeError:
                    print("This command requires that you first select an account.\n")
                    continue
                except OverdrawError:
                    print("This transaction could not be completed due to an insufficient account balance.\n")
                    continue
                except TransactionLimitError:
                    print("This transaction could not be completed because the account has reached a transaction limit.\n")
                    continue

            # else:
            #     assert (False)
            else:
                print("{0} is not a valid choice".format(choice))


    def _summary(self):
        for x in self._bank.show_accounts():
            print(x)

    def _load(self):
        with open("save.pickle", "rb") as f:
            self._bank = pickle.load(f)

    def _save(self):
        
        with open("save.pickle", "wb") as f:
            pickle.dump(self._bank, f)

    def _quit(self):
        sys.exit(0)

    def _add_transaction(self):
        while True:
            try:
                amount = input("Amount?\n>")
                amount = Decimal(amount)
                break
            except InvalidOperation:
                print("Please try again with a valid dollar amount.\n")
                continue

        while True:
            try:
                date = input("Date? (YYYY-MM-DD)\n>")
                date = datetime.strptime(date, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.\n")
                continue 

        if not self._selected_account:
            raise AttributeError
        t = Transaction(amount, date)

        self._selected_account.add_transaction(t)

    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        initial_deposit = input("Initial deposit amount?\n>")

        t = Transaction(initial_deposit)

        a = self._bank.add_account(acct_type)
        a.add_transaction(t)
        
    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthy_triggers(self):
        if not self._selected_account:
            raise AttributeError
        try:
            self._selected_account.assess_interest_and_fees()
        except TransactionSequenceError as err:
            print
            

    def _list_transactions(self):
        if not self._selected_account:
            raise AttributeError
        for x in self._selected_account.get_transactions():
            print(x)



if __name__ == "__main__":
    logging.basicConfig(filename='bank.log', filemode = 'w', level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        BankCLI().run()
    except Exception as err:
        print('Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.\n')
        logging.error(str(type(err).__name__) + ": " + repr(err))
        #logging.error(err)