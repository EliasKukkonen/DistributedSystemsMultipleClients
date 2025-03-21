#######################################################
#Sources and AI declaration:

#Sources:
#Intial idea on how to implement the application, I got from here, followed the video and immplemented code in same manner: https://www.youtube.com/watch?v=5G_bNVKdECk
#As well took ideas for the client code from this source: https://www.geeksforgeeks.org/simple-chat-room-using-python/
#Ideas on how to implement the client side with direct messaging was taken from here: https://github.com/kabizzle/Python-Chat-App/blob/master/client.py

#AI Declaration:
#ChatGPT 4o, o1 was used in the debugging purposes and some problem resolving.
#############################################################





import socket
from threading import Thread
import os
from colorama import init, Fore, Style
#Intialize colors.
init(autoreset=True)
#Client class handles connection to the server and message exchange.
class Client:


    def __init__(self, host, port):
        self.socket=socket.socket() #TCP socket for client.
        self.socket.connect((host, port)) #Connect to the server at the specific host and port.
        #Prompts to the user while logging in for the first time.
        print("To connect to the new channel, simple input, :channel join <channelName>")
        print("To leave the channel, simple input, :channel leave <channelName>")
        print("To send private message, input: @<nickname of user> 'message'")
        print("To quit, input: 'exit'")
        print("Have fun in chat!")
        self.name=input("Enter nickname: ")

        self.talkToServer() #Communication with server.

    #talkToServer sends the client's nickname to the server and starts two threads.
    #one for sending messages and other for receiving.
    def talkToServer(self):
        #Send the nickname to the server upon connection.
        self.socket.send(self.name.encode())
        #Separate thread to continuosly receive messages from server.
        Thread(target =self.ReceiveMessage).start() #Enter loop to send messages to the server.
        self.sendMessage()

    #sendMessage continuosly reads input from the user and sends it to the server.
 
    def sendMessage(self):
        while True:
            #Read user input. 
            clientInput = input("")
            # The input starts with a command character (':' or '@').
            # If the input is a command, send it as is; otherwise, add the nickname.
            if clientInput.startswith(":") or clientInput.startswith("@"):
                message = clientInput
            else:
                message = self.name + ": " + clientInput
                # Send the message over the socket to the server.
            self.socket.send(message.encode())

    
    #ReceiveMessage continuosly listens for messages from the server.
    #Private messages are in red and all other in green.
    def ReceiveMessage(self):
         # Continuously receive messages from the server.
        while True:
            ServerMessage=self.socket.recv(1024).decode()
             # If the message is empty, exit the program.
            if not ServerMessage.strip():
                os._exit(0)
                # Colorize private messages in red; all other messages in green.
            if "Private" in ServerMessage:
                print(Fore.RED + ServerMessage)
            else:
                print(Fore.GREEN + ServerMessage)
                


if __name__ =='__main__':
    try:
         # Prompt for the server's IP address.
        ip=input("Provide correct ip address: ")
        # Create a Client instance which connects to the server.
        Client(ip, 1234)
    except Exception:
        print("Wrong Ip address")
        os._exit(1)
        
            

    
        
        
