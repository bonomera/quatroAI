import socket
import json
import time
import threading

def connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        #host = input("Enter the server's IP address: (default address: 192.168.0.8)") or "192.168.0.8" # Choose the server's IP address, and if not specified, the default address will be used
        #port = input("Enter the server's port: (default port: 3000)") or 3000 # Choose the server's port, and if not specified, the default port will be used
        host = "192.168.1.102" # Default address
        port = 3000

        try:
            port = int(port) 
            s.connect((host, port))
            print(f"You are connected to {host}:{port}")
            break

        except socket.error as e:
            print(f"Connection error: {e}. Please check the server address and port.")
            continue
    return host, s

def identification(s):
    # This is for identification, where the name, matricule, and port will be used by the server to send data to the client.
    try:
        identifiant = {"request": "subscribe", 
                        "port": 12345, # Port to be used by the server to send data to the client
                        "name": "fun_name_for_the_client", # Name
                        "matricules": ["12345", "67891"]} # Identifiant
        json_identifiant = json.dumps(identifiant)
        s.sendall(json_identifiant.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        try:
            response = json.loads(response)
            if response['response'] == "ok":
                print(f"Identification was successful: {response['response']}")
            else:
                print(f"Identification failed due to: {response['error']}")
        except json.JSONDecodeError:
            print("JSON decoding error: invalid response")
            return
    except socket.error as e:
        print(f"Connection error1: {e}")
        
    return identifiant['port']

def refreshdata(conn, addr):
    try:
        while True:
            ping= conn.recv(1024).decode('utf-8')
            print(f"Received from {addr}: {ping}")
            try:
                ping_data = json.loads(ping)
                if ping_data.get('request') == 'ping':
                    print(f"Ping received from {addr}, sending pong...")
                    pong = {"response": "pong"}
                    json_pong = json.dumps(pong)
                    conn.sendall(json_pong.encode('utf-8'))
                    print(f"Pong sent to {addr}")
                elif ping_data.get('request') == 'play':
                    print(f"Play request received from {addr}, starting game...")
                    game()
                else:
                    print(f"Invalid request from {addr}: {ping_data}")
            except json.JSONDecodeError:
                print(f"Received non-JSON data from {addr}: {ping}")
    except socket.error as e:
        print(f"Socket error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed with {addr}")

def main(port, host):
    address = (host, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(address)
        s.listen()
        print(f"Server listening on {address}...")
        while True:
            try:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=refreshdata, args=(conn, addr))
                client_thread.start()
            except socket.timeout:
                print("Accept timed out, continuing to listen...")
                continue
    finally:
        s.close()
        print("Server socket closed")

def game():
    pass


# execution of the program
try:
    host, s = connection()
    if s:
        port = identification(s)
        if port:
            main(port, host)
        
except Exception as e:
    print(f"An unexpected error occurred in main execution: {e}")
finally:
    if s:
        print("Closing main connection socket.")
        try:
            s.close()
        except socket.error as e:
             print(f"Error closing main socket: {e}")