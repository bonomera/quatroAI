import pytest
import socket
import json
import os
import threading
from unittest.mock import patch, MagicMock, mock_open

# Import the functions from your module
# Note: You might need to adjust the import depending on the structure of your project
import sys
sys.path.append('.')  # Add the current directory to path if needed

# We need to patch the 'game' function BEFORE importing the connect module
with patch('algo.game') as mock_game_func:
    # Set up the mock to return a valid response
    mock_game_func.return_value = (3, 4)
    
    # Now import the client module that uses the mocked function
    import connect as client  # Import the main file
    import algo 

class TestClient:
    
    @patch('socket.socket')
    def test_connection(self, mock_socket):
        # Setup the mock socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Test successful connection
        host, s = client.connection()
        
        # Assertions
        assert host == "192.168.1.101"
        assert s == mock_socket_instance
        mock_socket_instance.connect.assert_called_once_with(("192.168.1.101", 3000))
    
    @patch('socket.socket')
    def test_identification_success(self, mock_socket):
        # Setup mock socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Mock the receive data with successful response
        mock_socket_instance.recv.return_value = json.dumps({"response": "ok"}).encode('utf-8')
        
        # Call the function
        port = client.identification(mock_socket_instance)
        
        # Assertions
        assert port == 54345
        mock_socket_instance.sendall.assert_called_once()
        sent_data = json.loads(mock_socket_instance.sendall.call_args[0][0].decode('utf-8'))
        assert sent_data['request'] == "subscribe"
        assert sent_data['name'] == "BotBotBot"
        assert sent_data['matricules'] == ["23383"]
    
    @patch('socket.socket')
    def test_identification_failure(self, mock_socket):
        # Setup mock socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Mock the receive data with error response
        mock_socket_instance.recv.return_value = json.dumps({"response": "error", "error": "Invalid request"}).encode('utf-8')
        
        # Call the function
        port = client.identification(mock_socket_instance)
        
        # Assertions
        assert port == 54345  # The function still returns the port even on server error
    @patch('socket.socket')
    def test_identification_socket_error(self, mock_socket):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate a error
        mock_socket_instance.sendall.side_effect = socket.error("send error")

        result = client.identification(mock_socket_instance)
        assert result is None
    @patch('socket.socket')
    def test_identification_json_decode_error(self, mock_socket):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Send invalid message for json
        mock_socket_instance.recv.return_value = b'{invalid json'

        result = client.identification(mock_socket_instance)
        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('json.dump')
    def test_save_time(self, mock_json_dump, mock_file):
        # Test save_time function
        client.save_time(1.23)
        
        # Check if file was opened for writing
        mock_file.assert_called_with(os.path.join(os.path.dirname(client.__file__), 'times.json'), 'w')
        
        # Check if json.dump was called with the correct data
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        assert 1.23 in args[0]

    @patch('socket.socket')
    def test_refreshdata_ping(self, mock_socket):
        # Setup mock connection and address
        mock_conn = MagicMock()
        mock_addr = ('127.0.0.1', 12345)
        
        # Send ping
        mock_ping_data = {"request": "ping"}
        
        # Call the function
        client.refreshdata(mock_conn, mock_addr, mock_ping_data)
        
        # Assertions
        mock_conn.sendall.assert_called_once()
        sent_data = json.loads(mock_conn.sendall.call_args[0][0].decode('utf-8'))
        assert sent_data['response'] == "pong"
        mock_conn.close.assert_called_once()

    @patch('socket.socket')
    @patch('time.time')
    def test_refreshdata_play(self, mock_time, mock_socket):
        # Setup mock connection and address
        mock_conn = MagicMock()
        mock_addr = ('127.0.0.1', 12345)
        
        # Mock time.time for simulate time
        mock_time.side_effect = [0, 1.5]  
        
        # Mock state for the game
        state_game = {
            "players": ["BotBotBot", "FKY"],
            "current": 0,
            "board": ['SDFC', 'BLEP', None, 'BLFC',
                      None, 'BDEC', None, None,
                      'SLEC', None, 'SLFC', None,
                      None, None, None, 'BDFP'],
            "piece": "BLEP"
        }

        # Send request
        mock_ping_data = {
                "request": "play",
                "lives": 3,
                "errors": [],  
                "state": state_game
            }
        
        # Call the function
        client.refreshdata(mock_conn, mock_addr,mock_ping_data)
        
        # Assertions
        assert mock_conn.sendall.call_count == 1
        
        # Decode Json send by client
        sent_data_raw = mock_conn.sendall.call_args[0][0].decode('utf-8').strip()
        sent_data = json.loads(sent_data_raw)
        assert sent_data['response'] == "move"
        assert sent_data['move']['pos'] == 3  
        assert sent_data['move']['piece'] == 4 
        mock_conn.close.assert_called_once()

    @patch('socket.socket')
    def test_refreshdata_with_errors(self, mock_socket):
        # Setup mock connection and address
        mock_conn = MagicMock()
        mock_addr = ('127.0.0.1', 12345)
        
        # Mock state for the game with errors
        state_game = {
            "players": ["BotBotBot", "FKY"],
            "current": 0,
            "board": ['SDFC', 'BLEP', None, 'BLFC',
                      None, 'BDEC', None, None,
                      'SLEC', None, 'SLFC', None,
                      None, None, None, 'BDFP'],
            "piece": "BLEP"
        }

        mock_ping_data = {
                "request": "play",
                "lives": 2,
                "errors": ["error1", "error2"],  # List of error for test
                "state": state_game
            }
        

        with patch('connect.save_time') as mock_save_time:
            # Call the function
            client.refreshdata(mock_conn, mock_addr,mock_ping_data)
            
            # If save_time is called when list of error
            mock_save_time.assert_called_once_with(["error1", "error2"])
            mock_conn.close.assert_called_once()

    @patch('socket.socket')
    @patch('threading.Thread')
    def test_main(self, mock_thread, mock_socket):
        # Setup mock socket
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Fake a connection
        mock_socket_instance.accept.side_effect = [
            (MagicMock(), ('127.0.0.1', 12345)),
            Exception("Test end")
        ]
        
        # Call the function with expected exception
        with pytest.raises(Exception, match="Test end"):
            client.main(54345, "0.0.0.0")
        
        # Assertions
        mock_socket_instance.bind.assert_called_once_with(("0.0.0.0", 54345))
        mock_socket_instance.listen.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

if __name__ == "__main__":
    pytest.main(["-v", "test_client.py"])