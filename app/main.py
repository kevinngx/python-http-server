# Uncomment this to pass the first stage
import socket
import socket
import threading
import sys

status_200 = "HTTP/1.1 200 OK"
status_201 = "HTTP/1.1 201 Created"
status_400 = "HTTP/1.1 404 Bad Request"
status_404 = "HTTP/1.1 404 Not Found"

def handle_user_agent(user_agent):
    return (f"{status_200}\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(user_agent)}\r\n"
            f"\r\n"
            f"{user_agent}")

def handle_echo(path_args):
    echo_text = path_args[2]
    if len(path_args) >= 3:
        response = (f"{status_200}\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(echo_text)}\r\n"
                    f"\r\n"
                    f"{echo_text}")
    else:
        response = f"{status_400}\r\n\r\n"  # Handle case where text to echo is missing
    return response

def handle_files_get(path_args):
    directory = sys.argv[2]
    filename = path_args[2]
    if len(path_args) >= 3:
        try:
            with open(f'/{directory}/{filename}', 'r') as f:
                body = f.read()
                print(body)
                response = (f"{status_200}\r\n"
                            f"Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(body)}\r\n"
                            f"\r\n"
                            f"{body}")
        except Exception as e:
            print(f"Error: Reading /{directory}/{filename} failed. Exception: {e}")
            response = f"{status_404}\r\n\r\n"    
    else:
        response = f"{status_400}\r\n\r\n"  # Handle case where text to echo is missing
    return response

def handle_files_post(path_args, data):
    print("HANDLING POST REQUEST")
    directory = sys.argv[2]
    filename = path_args[2]
    if len(path_args) >= 3:
        try:
            with open(f'{directory}{filename}', 'wb') as f:
                print("WRITING TO FILE")
                f.write(data.encode("utf-8"))
                response = f"{status_201}\r\n\r\n"
        except Exception as e:
            print(f"Error: Reading /{directory}/{filename} failed. Exception: {e}")
            response = f"{status_404}\r\n\r\n"    
    else:
        response = f"{status_400}\r\n\r\n"  # Handle case where text to echo is missing
    return response

def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    try:
        request = client_socket.recv(1024).decode("utf-8")  # 1024 bytes is a common convention for the size of the payload
        print(f'Received: {request}')
        

        lines = request.splitlines()

        if lines:
            # Parse Request Line
            request_line = lines[0]
            parts = request_line.split()
            
            # Parse Headers
            headers = {}
            for i in range(1, len(lines)):
                split = lines[i].split(": ")
                if len(split) > 1:
                    headers[split[0]] = split[1]

            if len(parts) >= 2:
                method, path = parts[0], parts[1]
                print(f'Method = {method}, Path = {path}')

                path_args = path.split("/")
                print(f'path list = {path_args}')
                
                # empty endpoint "/"
                if len(path_args) >= 2 and path_args[1] == '':
                    response = f"{status_200}\r\n\r\n"

                # echo endpoint "/eco/{echo_text}"
                elif len(path_args) >= 2 and path_args[1] == 'echo':
                    response = handle_echo(path_args)
                    
                # user-agent endpoint "/user-agent"
                elif len(path_args) >= 2 and path_args[1] == 'user-agent':
                    response = handle_user_agent(headers['User-Agent'])

                # user-agent endpoint "/files"
                elif len(path_args) >= 2 and path_args[1] == 'files':
                    if method == 'GET':
                        response = handle_files_get(path_args)
                    if method == 'POST':
                        post_body = request.split("\r\n")[-1]
                        response = handle_files_post(path_args, post_body)

                # invalid endpoint    
                else:
                    response = f"{status_404}\r\n\r\n"
                client_socket.send(response.encode("utf-8"))    
    except Exception as e:
        print(f'Error when handling client: {e}')
    finally:
        client_socket.close()
        print(f"Connection to client ({client_address[0]}:{client_address[1]}) closed")


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True) # create_server returns a socket object bound to the server

    while True:
        client_socket, client_address = server_socket.accept() # connection returns a tuple pair of (conn, address) 
        # addresss is a tuple of client (ip, port), 
        # conn is a new socket object which shares a connection with the client
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    main()