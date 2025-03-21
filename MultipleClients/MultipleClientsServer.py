#######################################
#Sources and AI declaration:

#Sources:
#Intial idea on how to implement the code, I got from here, followed the video and implemented code in same manner: https://www.youtube.com/watch?v=5G_bNVKdECk
#As well took ideas for the code from this source, especially for broadcast function: https://www.geeksforgeeks.org/simple-chat-room-using-python/
#Ideas on how to implement the direct messaging and channel creation was taken from this source: https://github.com/kabizzle/Python-Chat-App/blob/master/server.py

#AI Declaration:
#ChatGPT 4o, o1 was used in the debugging purposes and some problem resolving.
#####################################################

import socket
from threading import Thread



#Server class handles all incoming client connections
#channel management, private messaging

class Server:
    #Global list to store clients.
    Clients=[]
    #Dictionary to map channel names to a list of clients in that channel
    Channels={}

    def __init__(self, host, port):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
        self.socket.bind((host, port))#Bind the socket to the provided host and port.
        self.socket.listen(10) #Maximum 10 queued connections
        self.Channels={} #Initialize the channels
        print("Server is ready for users...")

    #listenForConnections continuosly accepts new client connections.
    #For each new client, function receives nickname, assigns to default channel "Main".
    #Notify everyone in the channel that new user appeared, and creates new thread to handle that client.
    def listenForConnections(self):
        while True:
            ClientSocket, address = self.socket.accept() #Accept an incoming connection.
            print("Connection is coming from: " +str(address)) #Message that connection is succesfull.

            NameOfClient=ClientSocket.recv(1024).decode() #First message is nickname.
            client={'NameOfClient': NameOfClient, 'ClientSocket': ClientSocket, 'channel': "Main"} #Create a dictionary to hold client info.

            if "Main" not in self.Channels: #if main channel does not exists inialize one. And assign to the dictionary.
                self.Channels["Main"] = [] 
            self.Channels["Main"].append(client) #Add client to the main channel.

            self.BroadcastToChannel("Main", NameOfClient, NameOfClient +" Joined main chat, weclome") # Notify everyone.

            Server.Clients.append(client) #Add the client to the client list.
            Thread(target=self.NewClientHandling, args=(client,)).start() #Initialize a new thread to handle messages from the client.

    #NewClientHandling runs one thread per one client.
    #Listens for messages from client and processes them.
    #Disconnection, channel commands, private messages, regular messages.
    def NewClientHandling(self, client):
        #Retireve the client nickname and socket for easier access.
        NameOfClient=client['NameOfClient']
        ClientSocket=client['ClientSocket']
        #Handle messages from clients using loop.
        while True:
            MessagesFromClient = ClientSocket.recv(1024).decode() #Decode the message.

            if MessagesFromClient.strip() == NameOfClient + ": exit" or not MessagesFromClient.strip(): #IF message have exit, exit the system.
                CurrentChannel = client["channel"] #Find the current channel.
                self.BroadcastToChannel(CurrentChannel, NameOfClient, NameOfClient + " has left the chat, bye!") #Notify everyone.
                Server.Clients.remove(client)#Remove client from the list.
                if CurrentChannel in self.Channels and client in self.Channels[CurrentChannel]: #Remove from the channel.
                        self.Channels[CurrentChannel].remove(client)
                ClientSocket.close()
                break
            #If message contain the channel, use function HandleChannelCommand.
            elif MessagesFromClient.startswith(":channel"):
                self.HandleChannelCommand(client, MessagesFromClient)
            #If message contain the @, use function HandlePrivateMessage.
            elif MessagesFromClient.startswith("@"):
                self.HandlePrivateMessages(client, MessagesFromClient)
            else:
                #OTherwise, retrieve the current channel on where currently is client.
                #Post messages there.
                CurrentChannel = client["channel"]
                self.BroadcastToChannel(CurrentChannel, NameOfClient, MessagesFromClient)

    #HandleChannelCommand processes commands to join or leave the channels.

    def HandleChannelCommand(self, client, message):
        # Expected format: ":channel join NewChannel" or ":channel leave NewChannel".
        parts = message.split() #Split message.
        if len(parts) < 3:
            client["ClientSocket"].send("Invalid channel command format. Use: :channel join <ChannelName>".encode()) #Error messagel.
            return

        #What to do, and where to join.
        action = parts[1].lower()
        new_channel = parts[2]

        if action == "join":
            # Remove client from its current channel.
            CurrentChannel = client["channel"]
            if CurrentChannel in self.Channels and client in self.Channels[CurrentChannel]: #Find client and channel.
                self.Channels[CurrentChannel].remove(client) #Remove client.
                self.BroadcastToChannel(CurrentChannel, client["NameOfClient"], f"{client['NameOfClient']} has left the channel.") 

            # Update client's active channel.
            client["channel"] = new_channel #Assign new channel.
            if new_channel not in self.Channels:
                self.Channels[new_channel] = []
            self.Channels[new_channel].append(client) #Append client to the new channel.
            client["ClientSocket"].send(f"You joined channel {new_channel}".encode()) #Notify client.
            self.BroadcastToChannel(new_channel, client["NameOfClient"], f"{client['NameOfClient']} joined the channel, welcome!") #Notify others on the channel.
        elif action == "leave":
            # For leaving, go back to "Main" channel.
            CurrentChannel = client["channel"]
            if CurrentChannel in self.Channels and client in self.Channels[CurrentChannel]:
                self.Channels[CurrentChannel].remove(client) #Remove the current channel.
                self.BroadcastToChannel(CurrentChannel, client["NameOfClient"], f"{client['NameOfClient']} has left the channel.") #Notify everyone.
            client["channel"] = "Main" #Assign to the main channel.
            if "Main" not in self.Channels:
                self.Channels["Main"] = [] #IF there is no main assigned to the client, create one.
            self.Channels["Main"].append(client) #Assign client to the main channel.
            client["ClientSocket"].send("You left the channel and are now in Main.".encode()) #Notify client.
            self.BroadcastToChannel("Main", client["NameOfClient"], f"{client['NameOfClient']} joined Main channel, welcome!")
        else:
            client["ClientSocket"].send("Unknown channel action. Use join/leave.".encode()) #Message if problem occured.


    #HandlePrivateMessages processes private messages sent by each clients.
    def HandlePrivateMessages(self, client, message):
        # Expected format: "@nickname message".
        parts = message.split(" ", 1) #Split the message .
        if len(parts) < 2: 
            client["ClientSocket"].send("Invalid private message format. Use: @<nickname> <message>".encode())
            return

        target_nick = parts[0][1:]  # Remove '@' from the beginning, nickname of end user.
        private_msg = parts[1] #Message itself.
        target_client = None
        for c in Server.Clients: #Find the target client.
            if c["NameOfClient"] == target_nick: #Find the client.
                target_client = c 
                break

        if target_client: #if found.
            # Send private message to the target.
            target_client["ClientSocket"].send(f"Private from {client['NameOfClient']}: {private_msg}".encode())
            client["ClientSocket"].send(f"Private to {target_nick}: {private_msg}".encode()) 
        else:
            client["ClientSocket"].send("User not found.".encode()) #Otherwise notify about error.

    

    #BroadcastToChannel sends a message to all clients in a specific channel,
    #sender is not included in the message.
    def BroadcastToChannel(self, channel, sender, message):
        #This function broadcast the message to all clients in specific channel except the sender.
        if channel in self.Channels: #Find the channel.
            for client in self.Channels[channel]: #Find the client in the Channels.
                if client["NameOfClient"] != sender: #IF not sender, send the message.
                    client["ClientSocket"].send(f"[{channel}]: {message}".encode())

    
#If runned directly, create the server instance and start listening for connections.
if __name__ =='__main__':
    #Start the server.
    try:
        server=Server('127.0.0.1', 1234)
        server.listenForConnections()
    except KeyboardInterrupt:
        print("Shutting down")
            
        
            
