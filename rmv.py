
import socket


def connect_RSI(self):
    # Create Socket
    rServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to host and port
    rServer.bind((self.host, self.port))

    # Listen For msgs
    rServer.listen(1)

    # Accept connection
    connection, s_server = rServer.accept()

    print("Connected to", s_server)

    self.connection = connection


def update_RSI(self):
    # Loop
    while self.auto_trade and self.connection:
        # Receive RSI
        rsi = self.connection.recv(1024).decode().split(",")

        # Update
        self.lvl = rsi

    self.connection.close()
