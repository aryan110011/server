import requests
import time
import json
import os
from dotenv import load_dotenv
from getpass import getpass

# Load .env
load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")

# Terminal colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_logo():
    print(RED + r"""
████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗   ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║██║   ██╔╝
   ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║█████╔╝  
   ██║   ██╔══╝  ██╔═══╝ ██║╚██╔╝██║██║   ██║██╔═██╗  
   ██║   ███████╗██║     ██║ ╚═╝ ██║╚██████╔╝██║  ██╗
   ╚═╝   ╚══════╝╚═╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
""" + RESET)

def main_menu():
    print_logo()
    login_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{YELLOW}Login Time: {login_time}{RESET}")

    password = getpass(f"{BLUE}Password: {RESET}")
    if password != "admin123":  # Optional: move to .env if needed
        print(RED + "❌ Wrong password. Access denied." + RESET)
        return

    while True:
        print(f"\n{BLUE}--- Main Menu ---{RESET}")
        print("1. Start Convo")
        print("2. View Convo")
        print("3. Resume Convo")
        print("4. Stop Convo")
        print("5. Exit")
        choice = input(f"{GREEN}Enter your choice (1-5): {RESET}")

        if choice == "1":
            start_convo()
        elif choice == "2":
            view_convos()
        elif choice == "3":
            resume_convo()
        elif choice == "4":
            stop_convo()
        elif choice == "5":
            print(GREEN + "✅ Exiting... Thank you!" + RESET)
            break
        else:
            print(RED + "❌ Invalid choice. Try again." + RESET)

def start_convo():
    convo_type = input(f"{BLUE}Single or Multi (single/multi): {RESET}").lower()
    accounts = []

    if convo_type == "multi":
        count = int(input("How many accounts: "))
        for i in range(count):
            print(f"{GREEN}Account {i+1}:{RESET}")
            name = input(" Name: ")
            token = input(" Token: ")
            cookie = input(" Cookie: ")
            accounts.append({"name": name, "token": token, "cookie": cookie})
    else:
        name = input("Account Name: ")
        token = input("Token: ")
        cookie = input("Cookie: ")
        accounts.append({"name": name, "token": token, "cookie": cookie})

    group_count = int(input("How many groups: "))
    group_ids = [input(f"Group UID {i+1}: ") for i in range(group_count)]

    hatter_name = input("Hatter Name: ")
    message_mode = input("Message Mode (file/single): ").lower()

    if message_mode == "file":
        file_path = input("Enter message file path: ")
        with open(file_path, "r") as f:
            messages = [line.strip() for line in f if line.strip()]
    else:
        messages = [input("Enter your message: ")]

    delay = int(input("Message delay (seconds): "))
    convo_name = input("Convo Name: ")

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
        response = requests.post(f"{SERVER_URL}/start_convo", json=data)
        print(GREEN + response.text + RESET)
    except Exception as e:
        print(RED + f"❌ Failed to connect to server: {e}" + RESET)

def view_convos():
    try:
        res = requests.get(f"{SERVER_URL}/view_convos")
        convos = res.json().get("conversations", [])
        print(f"{YELLOW}Available Convos:{RESET}")
        for name in convos:
            print(f" - {name}")

        convo_name = input("Enter convo name to view live: ")
        r = requests.get(f"{SERVER_URL}/stream_convo/{convo_name}", stream=True)
        print("\n--- Live Messages ---")
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        print(RED + "\nStopped viewing." + RESET)
    except Exception as e:
        print(RED + f"❌ Error: {e}" + RESET)

def resume_convo():
    try:
        res = requests.get(f"{SERVER_URL}/resume_convos")
        resumables = res.json().get("resumable", [])
        print(f"{YELLOW}Resumable Convos:{RESET}")
        for name in resumables:
            print(f" - {name}")

        convo_name = input("Enter convo name to resume view: ")
        r = requests.get(f"{SERVER_URL}/stream_resume/{convo_name}", stream=True)
        print("\n--- Resume Stream ---")
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        print(RED + "\nStopped resume." + RESET)
    except Exception as e:
        print(RED + f"❌ Error: {e}" + RESET)

def stop_convo():
    try:
        res = requests.get(f"{SERVER_URL}/view_convos")
        convos = res.json().get("conversations", [])
        print(f"{YELLOW}Running Convos:{RESET}")
        for name in convos:
            print(f" - {name}")

        convo_name = input("Enter convo name to stop: ")
        res = requests.post(f"{SERVER_URL}/stop_convo", json={"convo_name": convo_name})
        print(GREEN + res.text + RESET)
    except Exception as e:
        print(RED + f"❌ Error: {e}" + RESET)

if __name__ == "__main__":
    main_menu()
