import socket
import threading
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_message(message_text, key):
    f = Fernet(key)
    return f.encrypt(message_text.encode())

def decrypt_message(cipher_text, key):
    f = Fernet(key)
    return f.decrypt(cipher_text).decode()

clients = []
usernames = []

def broadcast(message_text, sender_conn, key):
    for client in clients:
        if client != sender_conn:
            try:
                # encrypting message before sending
                client.send(encrypt_message(message_text, key))
            except:
                pass

def handle_client(conn, addr, key):
    print(f"Connected with {addr}")

    username = conn.recv(1024).decode()
    usernames.append(username)
    clients.append(conn)

    print(f"{username} joined")

    broadcast(f"{username} joined the chat", conn, key)

    while True:
        try:
            # receiving encrypted data
            data = conn.recv(1024)
            if not data:
                break

            message_text = decrypt_message(data, key)
            print(f"{username}: {message_text}")

            broadcast(f"{username}: {message_text}", conn, key)

        except:
            break

    print(f"{username} left")
    clients.remove(conn)
    usernames.remove(username)
    conn.close()

def start_server():
    HOST = '127.0.0.1'
    PORT = 5000

    key = load_key()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server started, waiting for clients...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, key))
        thread.start()

def start_client():
    HOST = '127.0.0.1'
    PORT = 5000

    key = load_key()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    username = input("Enter your name: ")
    client.send(username.encode())

    def receive_messages():
        while True:
            try:
                # receiving encrypted data
                data = client.recv(1024)
                message_text = decrypt_message(data, key)
                print("\n" + message_text)
            except:
                print("Disconnected")
                break

    def send_messages():
        while True:
            message_text = input("Me: ")
            # encrypting message before sending
            encrypted_msg = encrypt_message(message_text, key)
            client.send(encrypted_msg)

    threading.Thread(target=receive_messages).start()
    threading.Thread(target=send_messages).start()

if __name__ == "__main__":
    print("1. Generate Key")
    print("2. Start Server")
    print("3. Start Client")

    choice = input("Enter choice: ")

    if choice == "1":
        generate_key()
        print("Key generated")

    elif choice == "2":
        start_server()

    elif choice == "3":
        start_client()

    else:
        print("Invalid choice")
