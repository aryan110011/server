import requests
import time
import json
import os
from dotenv import load_dotenv

# Load .env config
load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")

RETRY_LIMIT = 5
RETRY_DELAY = 5  # seconds


def safe_request(method, url, **kwargs):
    for attempt in range(RETRY_LIMIT):
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"[!] Attempt {attempt+1} failed: {e}")
            time.sleep(RETRY_DELAY)
    print("[×] Server not responding after multiple attempts.")
    return None


def print_logo():
    print("""
████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗   ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║██║   ██║
   ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║███████║
   ██║   ██╔══╝  ██╔═══╝ ██║╚██╔╝██║██║   ██║██╔══██║
   ██║   ███████╗██║     ██║ ╚═╝ ██║╚██████╔╝██║  ██║
   ╚═╝   ╚══════╝╚═╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
""")


def main_menu():
    print_logo()
    login_time = input("Login Time: ")
    password = input("Password: ")

    while True:
        print("\n--- Main Menu ---")
        print("1. Start Convo")
        print("2. View Convo")
        print("3. Resume Convo")
        print("4. Stop Convo")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            start_convo()
        elif choice == "2":
            view_convos()
        elif choice == "3":
            resume_convo()
        elif choice == "4":
            stop_convo()
        else:
            print("Invalid choice. Try again.")


def start_convo():
    convo_type = input("Single or Multi (single/multi): ")
    accounts = []

    if convo_type == "multi":
        count = int(input("How many accounts: "))
        for i in range(count):
            print(f"Account {i+1}:")
            name = input("  Name: ")
            token = input("  Token: ")
            cookie = input("  Cookie: ")
            accounts.append({"name": name, "token": token, "cookie": cookie})
    else:
        name = input("Account Name: ")
        token = input("Token: ")
        cookie = input("Cookie: ")
        accounts.append({"name": name, "token": token, "cookie": cookie})

    group_count = int(input("How many groups: "))
    group_ids = [input(f"Group UID {i+1}: ") for i in range(group_count)]

    hatter_name = input("Hatter Name: ")
    message_mode = input("Message Mode (file/single): ")

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

    response = safe_request("POST", f"{SERVER_URL}/start_convo", json=data)
    if response:
        print(response.text)


def view_convos():
    res = safe_request("GET", f"{SERVER_URL}/view_convos")
    if not res:
        return
    convos = res.json().get("conversations", [])
    print("Available Convos:")
    for name in convos:
        print(f" - {name}")

    convo_name = input("Enter convo name to view live: ")
    r = safe_request("GET", f"{SERVER_URL}/stream_convo/{convo_name}", stream=True)
    if not r:
        return
    print("\n--- Live Messages ---")
    try:
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass


def resume_convo():
    res = safe_request("GET", f"{SERVER_URL}/resume_convos")
    if not res:
        return
    resumables = res.json().get("resumable", [])
    print("Available resumable convos:")
    for name in resumables:
        print(f" - {name}")

    convo_name = input("Enter convo name to resume view: ")
    r = safe_request("GET", f"{SERVER_URL}/stream_resume/{convo_name}", stream=True)
    if not r:
        return
    print("\n--- Resume Stream ---")
    try:
        for line in r.iter_lines():
            print(line.decode())
    except KeyboardInterrupt:
        pass


def stop_convo():
    res = safe_request("GET", f"{SERVER_URL}/view_convos")
    if not res:
        return
    convos = res.json().get("conversations", [])
    print("Available running convos:")
    for name in convos:
        print(f" - {name}")

    convo_name = input("Enter convo name to stop: ")
    res = safe_request("POST", f"{SERVER_URL}/stop_convo", json={"convo_name": convo_name})
    if res:
        print(res.text)


if __name__ == "__main__":
    main_menu()
