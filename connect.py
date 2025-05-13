import socket
import json
import time
import threading
from algo import game,find_best_negamax_move # Imports game logic and AI decision making.
import json
import os

def save_error(seconds): # Saves timing data or errors to a JSON file.
    file_path = os.path.join(os.path.dirname(__file__), 'times.json')
    error = []
    try:
        with open(file_path, 'r') as f:
            times = json.load(f)
    except FileNotFoundError:
        pass
    error.append(seconds)
    try:
        with open(file_path, 'w') as f:
            json.dump(times, f)
    except Exception as e:
        print(e)

def connection(): # Establishes and returns a socket connection to the game server.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        host = "192.168.1.101" # Server IP address
        port = 3000 # Server port
        try:
            port = int(port) 
            s.connect((host, port))
            print(f"You are connected to {host}:{port}")
            break
        except socket.error as e:
            print(f"Connection error: {e}. Please check the server address and port.")
            continue
    return host, s

def identification(s): # Sends identification to server, returns the port for server to connect back.
    try:
        identifiant = {"request": "subscribe", 
                        "port": 54345, # Port this client will listen on for server messages.
                        "name": "BotBotBot", # Name of the client
                        "matricules": ["23383"]} # Matricule
        json_identifiant = json.dumps(identifiant)
        s.sendall(json_identifiant.encode('utf-8'))
        response = s.recv(1024).decode('utf-8') # Receive server's response.
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
        return None
    return identifiant['port']

def refreshdata(conn, addr): # Handles requests (ping, play) from a game server connection.
    try:
        while True:
            ping = conn.recv(1024).decode('utf-8') # Receive and decode data from the game server continually

            try:
                ping_data = json.loads(ping)
                if ping_data.get('request') == 'ping': # Answer pong in json if receive ping from server
                    pong = {"response": "pong"}
                    conn.sendall(json.dumps(pong).encode('utf-8'))

                elif ping_data.get('errors') != []: # Save error list 
                    save_error(ping_data.get('errors'))

                elif ping_data.get('request') == 'play': # Play if server requests a move.
                    state_game = ping_data.get('state')
                    try:
                            pos, piece_to_give = game(state_game) # AI calculates the best move.
                            
                            while pos is None and state_game["board"] != [None]*16: # Retry logic if move calculation failed initially.
                                depth = 6
                                player = str(state_game["current"])
                                pos, piece_to_give= game(state_game, player, depth+1)

                            move_payload = { "pos": pos, "piece": piece_to_give }
                            move_response = { "response": "move", "move": move_payload, "message": f"^^)" }
                            print(f"==> Sending Move: Place at {pos}, Give piece {piece_to_give} in {timeop:.4f}s")
                            conn.sendall((json.dumps(move_response) + '\n').encode('utf-8')) # Send the calculated move.
                            print("Move sent successfully.")
                    except TimeoutError:
                        print("AI Error: Calculation timed out! Cannot send move.")
                    except Exception as ai_error:
                        save_time(state_game)
                        print(f"!!! AI Error during move calculation: {ai_error}")
                        import traceback
                        traceback.print_exc()
                # else: # Potentially invalid or unhandled request.
                    # print(f"Invalid request from {addr}: {ping_data}") 
            except json.JSONDecodeError:
                continue # Ignores malformed JSON messages.
    except socket.error as e:
        print(f"Socket error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed with {addr}")

def main(port, host): # Sets up this client's server to listen for game server's requests.
    address = (host, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(address)
        s.listen() # Listen for incoming connections from the game server.
        print(f"Server listening on {address}...")
        while True:
            try:
                conn, addr = s.accept() # Accept connection from game server.
                client_thread = threading.Thread(target=refreshdata, args=(conn, addr)) # Handle each connection in a new thread.
                client_thread.start()
            except socket.timeout:
                continue
    finally:
        s.close()
        print("Server socket closed")

# Main program execution
try:
    _, s = connection() # Connect to the main game server.
    host = "0.0.0.0" # Listen on all available interfaces.
    if s:
        port_to_listen = identification(s) # Identify and get the port to listen on.
        s.close() # Close initial connection; server will connect back.
        if port_to_listen:
            main(port_to_listen, host) # Start this client's listening server.
        else:
            print("Failed to get a port from identification. Exiting.")
    else:
        print("Failed to establish initial connection. Exiting.")
except Exception as e:
    print(f"An unexpected error occurred in main execution: {e}")