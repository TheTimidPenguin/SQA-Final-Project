logged_in_status = False #variable to determine logged in status

def login(): #login function
    global logged_in_status
    session_type = input("Please enter a session type\n") #asks information from user, displaying errors if any are encountered
    if session_type.lower() == "standard":
            account_name = input("Enter the account name\n")
            account_name = account_name.replace(" ", "_") #replaced the space with an underscore to searching purposes
            try:
                with open("BankAccountFile.txt", "r") as file: #opens BankAccountFile.txt
                    if file.read().find(account_name) != 1: #checks if user exists in the bank account file
                        bank_accounts = {}
                        file.seek(0) #moves pointer back to the beginning
                        for line in file: #goes through every bank account (line) and puts the data into a dictionary, which is then added to another dictionary
                            user_account = {}
                            user_account["account_number"] = line[0:5]
                            user_account["name"] = line[6:26].replace("_", " ").strip()
                            user_account["status"] = line[27:28]
                            user_account["balance"] = float(line[29:37])
                            bank_accounts[line[0:5]] = user_account
                        logged_in_status = True
                        return session_type, account_name, line[0:5], bank_accounts #returns relevant info
                    else:
                        print("Account not found")
            except FileNotFoundError:
                print("Error: bank account file does not exist")

    elif session_type.lower() == "admin": #same as above, but for admins. Admins do not require a name to log in
        try:
            with open("BankAccountFile.txt", "r") as file:
                bank_accounts = {}
                for line in file:
                    user_account = {}
                    user_account["account_number"] = line[0:5]
                    user_account["name"] = line[6:26].replace("_", " ").strip()
                    user_account["status"] = line[27:28]
                    user_account["balance"] = float(line[29:37])
                    bank_accounts[line[0:5]] = user_account
                    logged_in_status = True
                return session_type, bank_accounts
        except FileNotFoundError:
            print("Error: bank account file does not exist")
        return session_type
    else:
        print("Invalid session type")

def logout(transactions, account_name, account_number): #logout function
    global logged_in_status
    logged_in_status = False

    with open("TransactionFile", "a") as file: #creates a transaction file
        name_empty_space = 20 - len(account_name) #calculates the length of empty space required
        for x in range(0, len(transactions) - 1, 2): #for loop writes a line containing information on the type of transaction and amount of money involved using the transaction list
            print(x)
            file.write(f"{transactions[x]}_{account_name + ("_" * name_empty_space)}_{account_number}_{transactions[x+1]:08.2f}___\n")
        
        file.write(f"00_{account_name + ("_" * name_empty_space)}_{account_number}_00000000___\n") #writes an end of session transaction line
    print("Logged out successfully")

def withdrawal(session_type, bank_accounts): #withdraw money function
    if session_type == "standard":
        account_number = input("Enter the account number to withdraw from\n") #asks basic information from user
        if account_number in bank_accounts: #checks if account exists
            amount = float(input("Enter amount to withdraw\n"))
            if amount <= bank_accounts[account_number]["balance"] and amount <= 500: #checks if amount to withdraw isn't greater than the balance, as well as the amount being less than or equal to 500
                bank_accounts[account_number]["balance"] -= amount #withdraws
                print("Withdrawal successful")
                return "01", amount
            else:
                print("Cannot withdraw that amount")
        else:
            print("Account not found")
    elif session_type == "admin": #same as above for admins. Admins must input a name
        name = input("Enter the account holder's name\n")
        for x in bank_accounts:
            if x["name"] == name:
                account_number = input("Enter the account number to withdraw from\n")
                if account_number in bank_accounts:
                    amount = float(input("Enter amount to withdraw\n"))
                    if amount <= bank_accounts[account_number]["balance"]:
                        bank_accounts[account_number]["balance"] -= amount
                        print("Withdrawal successful")
                        return "01", amount
                    else:
                        print("Cannot withdraw that amount")
                else:
                    print("Account not found")
            else:
                print("Account not found")


def deposit(session_type, bank_accounts): #deposit function
    if session_type == "standard":
        account_number = input("Enter the account number to deposit to\n") #asks basic information from users
        if account_number in bank_accounts: #checks if account exists
            amount = float(input("Enter amount to deposit\n"))
            bank_accounts[account_number]["balance"] += amount #deposits
            print("Deposit successful")
            return "04", amount
        else:
            print("Account not found")
    elif session_type == "admin": #same as above, for admins
        name = input("Enter the account holder's name\n")
        for x in bank_accounts:
            if x["name"] == name:
                account_number = input("Enter the account number to deposit to\n")
                if account_number in bank_accounts:
                    amount = float(input("Enter amount to deposit\n"))
                    bank_accounts[account_number]["balance"] += amount
                    print("Deposit successful")
                    return "04", amount
                else:
                    print("Account not found")
            else:
                print("Account not found")

def transfer(session_type, bank_accounts): #transfer function
    if session_type == "standard":
        transfer_from = input("Enter the account number to transfer from\n") #asks basic information from users
        if transfer_from in bank_accounts: #checks if account exists
            transfer_to = input("Enter the account number to transfer to\n")
            if transfer_to in bank_accounts: #checks if account exists
                amount = float(input("Enter amount to transfer\n"))
                if amount <= bank_accounts[transfer_from]["balance"] and amount <= 1000: #checks if amount is less than or equal to the balance, and amount is less than 1000
                    bank_accounts[transfer_from]["balance"] -= amount #subtracts from user being transfered from
                    bank_accounts[transfer_to]["balance"] += amount #adds to user being transferred to
                    print("Transfer successful")
                    return "02", amount
                else:
                    print("Cannot transfer that amount")
            else:
                print("Cannot transfer to that account")
        else:
            print("Cannot transfer from that account")
    elif session_type == "admin": #same as above, for admins
        name = input("Enter the account holder's name\n")
        for x in bank_accounts:
            if x["name"] == name:
                transfer_from = input("Enter the account number to transfer from\n")
                if transfer_from in bank_accounts:
                    transfer_to = input("Enter the account number to transfer to\n")
                    if transfer_to in bank_accounts:
                        amount = float(input("Enter amount to transfer\n"))
                        if amount <= bank_accounts[transfer_from]["balance"]:
                            bank_accounts[transfer_from]["balance"] -= amount
                            bank_accounts[transfer_to]["balance"] += amount
                            print("Transfer successful")
                            return "02", amount
                        else:
                            print("Cannot transfer that amount")
                    else:
                        print("Cannot transfer to that account")
                else:
                    print("Cannot transfer from that account")
            else: 
                print("Account not found")

while True: #infinite loop
    while logged_in_status == False:
        command = input("Please login (Type login)\n") #asks to login
        if command.lower() == "login":
            session_type, account_name, account_number, bank_accounts = login() #runs login function
            transactions = []
            while logged_in_status == True: #infinite loop while logged in
                if session_type.lower() == "standard":
                    print(bank_accounts)
                    
                    command = input("Please enter a command. Commands are withdrawal, transfer, paybill, deposit, logout\n")
                    match command.lower():
                        case "login":
                            print("Already logged in")
                        case "logout":
                            logout(transactions, account_name, account_number) #runs logout function
                        case "withdrawal":
                            cc, amount = withdrawal(session_type, bank_accounts) #runs withdrawal function and saves transaction code and amount of funds involved
                            transactions.append(cc)
                            transactions.append(amount)
                        case "deposit":
                            cc, amount = deposit(session_type, bank_accounts) #runs deposit function and saves transaction code and amount of funds involved
                            transactions.append(cc)
                            transactions.append(amount)
                        case "transfer":
                            cc, amount = transfer(session_type, bank_accounts) #runs transfer function and saves transaction code and amount of funds involved
                            transactions.append(cc)
                            transactions.append(amount)
                        case _:
                            "Invalid command"
                
                elif session_type.lower() == "admin":
                    command = input("Please enter a command. Commands are withdrawal, transfer, paybill, deposit, create, delete, disable, changeplan, logout\n")

        else:
            print("Not logged in")