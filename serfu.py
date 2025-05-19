import os
import requests
import time
from datetime import datetime
from colorama import Fore, Style, init
import sys

init(autoreset=True)

SERVER_URL = "https://server-evn1.onrender.com"
GITHUB_APPROVAL_URL = "https://raw.githubusercontent.com/aryan110011/sarfu/main/aproval.txt"

# Stylized Red Logo
def print_logo():
    logo = f"""{Fore.RED}
                  __                    _ _           
                 / _|                  | | |          
  ___  __ _ _ __| |_ _   _   _ __ _   _| | | _____  __
 / __|/ _` | '__|  _| | | | | '__| | | | | |/ _ \ \/ /
 \__ \ (_| | |  | | | |_| | | |  | |_| | | |  __/>  < 
 |___/\__,_|_|  |_|  \__,_| |_|   \__,_|_|_|\___/_/\_\\
                                                      
    """
    for line in logo.splitlines():
        print(line)
        time.sleep(0.03)

# Display login time in Yellow
def show_login_time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.YELLOW}Login Time: {now}")

# Warning Note - Stylish Line by Line
def show_warning_note():
    lines = [
        f"{Fore.RED}[!] Warning: Unauthorized access is strictly prohibited!",
        f"{Fore.MAGENTA}[!] If anyone tries to use someone else's account, their approval will be removed.",
        f"{Fore.CYAN}[!] Abusing this tool may result in permanent ban.",
        f"{Fore.GREEN}[✔] This tool is made only for legends.",
        f"{Fore.YELLOW}\n       ~ Made by ArYan.x3\n"
    ]
    for line in lines:
        print(line)
        time.sleep(0.4)

# GitHub Approval Check
def check_approval(username, password):
    try:
        res = requests.get(GITHUB_APPROVAL_URL)
        if res.status_code == 200:
            data = res.text.splitlines()
            creds = [line.strip().split("|") for line in data if "|" in line]
            return [username, password] in creds
        else:
            print(Fore.RED + "[!] Failed to fetch approval list.")
            return False
    except:
        print(Fore.RED + "[!] Network error during approval check.")
        return False

# Menu
def main_menu():
    while True:
        print(Fore.CYAN + "\n======== Main Menu ========")
        print(f"{Fore.GREEN}[1] Start New Conversation")
        print(f"{Fore.YELLOW}[2] View Active Conversations")
        print(f"{Fore.MAGENTA}[3] Resume Previous Conversation")
        print(f"{Fore.RED}[4] Stop Conversation")
        print(f"{Fore.BLUE}[0] Exit")

        choice = input(Fore.WHITE + "\nEnter your choice: ").strip()
        if choice == "1":
            start_new_conversation()
        elif choice == "2":
            view_active_convos()
        elif choice == "3":
            resume_previous_convo()
        elif choice == "4":
            stop_convo()
        elif choice == "0":
            print(Fore.GREEN + "Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

# Start New Conversation
def start_new_conversation():
    convo_type = input("\nSingle or Multi login (single/multi): ").strip().lower()
    accounts = []

    if convo_type == "multi":
        file_path = input("Enter file path for tokens/cookies: ")
        try:
            with open(file_path, "r") as f:
                lines = [x.strip() for x in f.readlines() if x.strip()]
                for line in lines:
                    parts = line.split("|")
                    if len(parts) == 2:
                        token, cookie = parts
                        accounts.append({"token": token, "cookie": cookie})
                    elif len(parts) == 1:
                        accounts.append({"token": parts[0], "cookie": ""})
        except:
            print(Fore.RED + "[!] Error reading file.")
            return
    else:
        token = input("Enter token: ")
        cookie = input("Enter cookie (optional): ")
        accounts.append({"token": token, "cookie": cookie})

    print(Fore.CYAN + f"\n✅ Total Accounts Loaded: {len(accounts)}")

    group_count = int(input("How many Messenger Group UIDs: "))
    group_ids = [input(f" Group UID {i+1}: ") for i in range(group_count)]

    hatter_name = input("Hatter Name: ")
    msg_mode = input("Message mode (file/single): ").strip().lower()

    messages = []
    if msg_mode == "file":
        path = input("Enter message file path: ")
        try:
            with open(path, "r") as f:
                messages = [x.strip() for x in f.readlines() if x.strip()]
        except:
            print(Fore.RED + "[!] Could not read message file.")
            return
    else:
        messages = [input("Enter message: ")]

    delay = int(input("Delay between messages (seconds): "))
    convo_name = input("Conversation name: ")

    data = {
        "type": convo_type,
        "accounts": accounts,
        "group_ids": group_ids,
        "hatter_name": hatter_name,
        "messages": messages,
        "delay": delay,
        "convo_name": convo_name
    }

    try:
        res = requests.post(f"{SERVER_URL}/start_convo", json=data)
        print(Fore.GREEN + res.text)
    except:
        print(Fore.RED + "[!] Failed to contact server.")

# View Conversations
def view_active_convos():
    try:
        res = requests.get(f"{SERVER_URL}/view_convos")
        convos = res.json().get("conversations", [])
        print(Fore.YELLOW + "\nActive Conversations:")
        for name in convos:
            print(f" - {name}")
        name = input("Enter convo name to view live: ")
        r = requests.get(f"{SERVER_URL}/stream_convo/{name}", stream=True)
        print(Fore.CYAN + "\n--- Live Messages ---")
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass
    except:
        print(Fore.RED + "[!] Failed to load messages.")

# Resume Previous Convo
def resume_previous_convo():
    try:
        res = requests.get(f"{SERVER_URL}/resume_convos")
        convos = res.json().get("resumable", [])
        print(Fore.YELLOW + "\nResumable Conversations:")
        for name in convos:
            print(f" - {name}")
        name = input("Enter convo name to resume: ")
        r = requests.get(f"{SERVER_URL}/stream_resume/{name}", stream=True)
        print(Fore.CYAN + "\n--- Resume Messages ---")
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass
    except:
        print(Fore.RED + "[!] Error resuming conversation.")

# Stop Convo
def stop_convo():
    try:
        res = requests.get(f"{SERVER_URL}/view_convos")
        convos = res.json().get("conversations", [])
        print(Fore.YELLOW + "\nRunning Conversations:")
        for name in convos:
            print(f" - {name}")
        name = input("Enter convo name to stop: ")
        res = requests.post(f"{SERVER_URL}/stop_convo", json={"convo_name": name})
        print(Fore.GREEN + res.text)
    except:
        print(Fore.RED + "[!] Error stopping conversation.")

# Entry point
if __name__ == "__main__":
    os.system("clear")
    print_logo()
    show_login_time()
    print()

    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    if not check_approval(username, password):
        print(Fore.RED + "\n[!] Access Denied. You are not approved.")
        sys.exit()

    print(Fore.GREEN + "\n✅ Access Approved!\n")
    show_warning_note()
    main_menu()
