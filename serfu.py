import os
import sys
import time
import requests
import json

# === CONFIG ===
SERVER_URL = "https://sarfu.onrender.com"
GLOBAL_PASSWORD = "sarfu123"

# === COLOR CODES ===
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"

# === RED LOGO WITH ANIMATION ===
def print_logo():
    logo_lines = [
        "                  __                    _ _           ",
        "                 / _|                  | | |          ",
        "  ___  __ _ _ __| |_ _   _   _ __ _   _| | | _____  __",
        " / __|/ _` | '__|  _| | | | | '__| | | | | |/ _ \\ \\/ /",
        " \\__ \\ (_| | |  | | | |_| | | |  | |_| | | |  __/>  < ",
        " |___/\\__,_|_|  |_|  \\__,_| |_|   \\__,_|_|_|\\___/_/\\_\\",
        "                                                    ",
        "                                                    ",
    ]
    for line in logo_lines:
        print(f"{RED}{line}{RESET}")
        time.sleep(0.1)

# === DISPLAY LOGIN TIME ===
def show_login_time():
    login_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{YELLOW}🔓 Login Time: {login_time}{RESET}")

# === ASK FOR PASSWORD ===
def ask_password():
    print(f"{GREEN}🔐 Please enter your password to access the tool:{RESET}")
    password = input("Password: ")
    if password == GLOBAL_PASSWORD:
        print(f"{GREEN}✅ Access Granted!{RESET}")
        return True
    else:
        print(f"{RED}❌ Incorrect Password. Access Denied.{RESET}")
        return False

# === NOTE WITH ANIMATION ===
def print_note():
    note_lines = [
        "\n",
        f"{CYAN}⚠️  Note:{RESET}",
        f"{CYAN}If any user tries to access another user's account, their approval will be revoked.{RESET}",
        f"{CYAN}Also, using bad language or abuse will result in removal from the tool.{RESET}",
        f"{CYAN}This tool is strictly for LEGENDS only!{RESET}",
        f"\n{YELLOW}Made by ArYan.x3{RESET}\n"
    ]
    for line in note_lines:
        print(line)
        time.sleep(0.3)

# === MAIN MENU ===
def main_menu():
    while True:
        print(f"\n{CYAN}=== Main Menu ==={RESET}")
        print(f"{GREEN}[1]{RESET} Start New Conversation")
        print(f"{GREEN}[2]{RESET} View Active Conversations")
        print(f"{GREEN}[3]{RESET} Resume Previous Conversation")
        print(f"{GREEN}[4]{RESET} Stop Conversation")
        print(f"{GREEN}[5]{RESET} Exit")
        choice = input(f"{YELLOW}Enter choice: {RESET}")

        if choice == "1":
            start_convo()
        elif choice == "2":
            view_convos()
        elif choice == "3":
            resume_convo()
        elif choice == "4":
            stop_convo()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print(f"{RED}Invalid choice! Try again.{RESET}")

# === START NEW CONVERSATION ===
def start_convo():
    convo_type = input("Single or Multi Login (single/multi): ").strip()
    accounts = []

    if convo_type == "multi":
        file_path = input("Enter file path containing token/cookie: ")
        if not os.path.exists(file_path):
            print(f"{RED}File not found!{RESET}")
            return
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            for line in lines:
                try:
                    name, token, cookie = line.split("|")
                    accounts.append({"name": name, "token": token, "cookie": cookie})
                except ValueError:
                    print(f"{RED}Invalid format in file line: {line}{RESET}")
    else:
        name = input("Account Name: ")
        token = input("Token: ")
        cookie = input("Cookie: ")
        accounts.append({"name": name, "token": token, "cookie": cookie})

    valid_accounts = [a for a in accounts if a['token'] or a['cookie']]
    if not valid_accounts:
        print(f"{RED}No valid accounts found.{RESET}")
        return

    print(f"{GREEN}Valid Accounts:{RESET}")
    for acc in valid_accounts:
        print(f" - {acc['name']}")

    group_count = int(input("How many Messenger groups: "))
    group_ids = [input(f"Group UID {i+1}: ") for i in range(group_count)]
    hatter_name = input("Hatter Name: ")
    message_mode = input("Message Mode (file/single): ")

    if message_mode == "file":
        file_path = input("Message file path: ")
        if not os.path.exists(file_path):
            print(f"{RED}File not found!{RESET}")
            return
        with open(file_path, "r") as f:
            messages = [line.strip() for line in f if line.strip()]
    else:
        messages = [input("Enter your message: ")]

    delay = int(input("Message Delay (seconds): "))
    convo_name = input("Conversation Name: ")

    data = {
        "type": convo_type,
        "accounts": valid_accounts,
        "group_ids": group_ids,
        "hatter_name": hatter_name,
        "messages": messages,
        "delay": delay,
        "convo_name": convo_name
    }

    res = requests.post(f"{SERVER_URL}/start_convo", json=data)
    print(res.text)

# === VIEW ACTIVE CONVERSATIONS ===
def view_convos():
    res = requests.get(f"{SERVER_URL}/view_convos")
    convos = res.json().get("conversations", [])
    print(f"{CYAN}Available Conversations:{RESET}")
    for name in convos:
        print(f" - {name}")
    convo_name = input("Enter convo name to view live: ")
    r = requests.get(f"{SERVER_URL}/stream_convo/{convo_name}", stream=True)
    print("\n--- Live Messages ---")
    try:
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass

# === RESUME PREVIOUS CONVO ===
def resume_convo():
    res = requests.get(f"{SERVER_URL}/resume_convos")
    convos = res.json().get("resumable", [])
    print(f"{CYAN}Resumable Conversations:{RESET}")
    for name in convos:
        print(f" - {name}")
    convo_name = input("Enter convo name to resume: ")
    r = requests.get(f"{SERVER_URL}/stream_resume/{convo_name}", stream=True)
    print("\n--- Resume Stream ---")
    try:
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass

# === STOP CONVERSATION ===
def stop_convo():
    res = requests.get(f"{SERVER_URL}/view_convos")
    convos = res.json().get("conversations", [])
    print(f"{CYAN}Running Conversations:{RESET}")
    for name in convos:
        print(f" - {name}")
    convo_name = input("Enter convo name to stop: ")
    res = requests.post(f"{SERVER_URL}/stop_convo", json={"convo_name": convo_name})
    print(res.text)

# === RUN MAIN ===
def start_tool():
    os.system("clear")
    print_logo()
    show_login_time()
    if ask_password():
        print_note()
        main_menu()
    else:
        sys.exit()

if __name__ == "__main__":
    start_tool()
