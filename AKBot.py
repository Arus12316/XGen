'''
the "altkilling" bot, or suicide hacks for short, run this bad boy and you get 60 kills in less than a minute; even faster if you can
set the time without killing the socket connection

P.S: permanent account ban, 2 week game ban
'''

import time
import socks
import socket
import struct
import string
import random
import threading
import ctypes

class AKBot:
    def __init__(self, Username, Password, IP, Port):
        self.NullByte = struct.pack('B', 0)
        self.BufSize = 4096
        self.CommandChar = '!'
        self.InLobby = False
        self.OnlineUsers = {}
        self.OnlineUserMap = {}
        self.RoomList = []
        self.Allowed = []

        self.KillCount = 0
        self.Alted = []
        self.Alting = False

        self.NameToIP = {'2D Central': '74.86.43.9:1138', 'Paper Thin City': '74.86.43.8:1138', 'Fine Line Island':  '198.58.106.101:1138', 'U of SA':  '69.164.207.72:1138',
                                      'Amsterdam':  '139.162.151.57:1138',  'Mobius Metro':  '45.56.72.83:1138', 'Cartesian':  '198.58.106.101:1139'}

        self.IPToName = {'74.86.43.9:1138': '2D Central', '74.86.43.8:1138': 'Paper Thin City', '198.58.106.101:1138': 'Fine Line Island', '69.164.207.72:1138': 'U of SA',
                                               '139.162.151.57:1138': 'Amsterdam', '45.56.72.83:1138': 'Mobius Metro', '198.58.106.101:1139': 'Cartesian'}

        self.BotPassword = Password
        self.ServerIP = IP
        self.ServerPort = Port
        self.BotServer = self.IPToName[ '{}:{}'.format(self.ServerIP, self.ServerPort)]

        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9150)
        socket.create_connection = socks.create_connection
        socket.socket = socks.socksocket
        ctypes.windll.kernel32.SetConsoleTitleW("StickArena Alting Bot @Anubis")

        self.connectToServer(Username, Password, self.ServerIP, self.ServerPort)

    def sendPacket(self, Socket, PacketData, Receive = False):
        Packet = bytes(PacketData, 'utf-8')

        if Socket:
            Socket.send(Packet + self.NullByte)

            if Receive:
                return Socket.recv(self.BufSize).decode('utf-8')

    def startKeepAlive(self, TimerSeconds = 20):
        if hasattr(self, 'SocketConn'):
            KeepAliveTimer = threading.Timer(TimerSeconds, self.startKeepAlive)
            KeepAliveTimer.daemon = True
            KeepAliveTimer.start()

            self.sendPacket(self.SocketConn, '0')

    def sendPrivateMessage(self, UserID, Message):
        if UserID != self.BotID:
            if UserID in self.OnlineUsers:
                self.sendPacket(self.SocketConn, '00' + UserID + 'P' + Message)

    def sendPublicMessage(self, Message):
        self.sendPacket(self.SocketConn, '9' + Message)

    def connectionHandler(self):
        Buffer = b''

        while hasattr(self, 'SocketConn'):
            try:
                Buffer += self.SocketConn.recv(self.BufSize)
            except OSError:
                if hasattr(self, 'SocketConn'):
                    try:
                        self.SocketConn.shutdown(socket.SHUT_RD)
                        self.SocketConn.close()
                    except:
                        pass

            if len(Buffer) == 0:
                print('Disconnected')
                break
            elif Buffer.endswith(self.NullByte):
                Receive = Buffer.split(self.NullByte)
                Buffer = b''

                for Data in Receive:
                    Data = Data.decode('utf-8')

                    if Data.startswith('U'):
                        UserID = Data[1:][:3]
                        Username = Data[4:][:20].replace('#', '')

                        self.parseUserData(Data)
                    elif Data.startswith('D'):
                        UserID = Data[1:][:3]

                        try:
                            Username = self.OnlineUsers[UserID]

                            del self.OnlineUserMap[Username]
                            del self.OnlineUsers[UserID]
                        except KeyError:
                            pass
                    elif Data.startswith('M'):
                        UserID = Data[1:][:3]

                        self.parseUserMessage(UserID, Data)
                    elif Data.startswith('0g') or Data.startswith('0j'):
                        print('{{Server}}: {}'.format(Data[2:]))
                    elif Data.startswith('093'):
                        print('Secondary login')
                        break
                    elif Data.startswith('0f') or Data.startswith('0e'):
                        Time, Reason = Data[2:].split(';')
                        print('This account has just been banned [Time: {} / Reason: {}]'.format(Time, Reason))
                    elif Data.startswith('01'):
                        for Room in Data[2:].split(';'):
                            self.RoomList = Data[2:].split(';')

    def connectToServer(self, Username, Password, ServerIP, ServerPort):
        try:
            self.SocketConn = socket.create_connection((ServerIP, ServerPort), socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150)
        except Exception as Error:
            print(Error)
            return

        Handshake = self.sendPacket(self.SocketConn, '08HxO9TdCC62Nwln1P', True).strip(self.NullByte.decode('utf-8'))

        if Handshake == '08':
            Credentials = '09{};{}'.format(Username, Password)
            RawData = self.sendPacket(self.SocketConn, Credentials, True).split(self.NullByte.decode('utf-8'))

            for Data in RawData:
                if Data.startswith('A'):
                    self.InLobby = True
                    self.BotID = Data[1:][:3]
                    self.BotUsername = Data[4:][:20].replace('#', '')

                    print('Connected.')

                    EntryPackets = ['02Z900_', '03_', '0a']

                    for Packet in EntryPackets:
                        self.sendPacket(self.SocketConn, Packet)

                    self.startKeepAlive()
                    ConnectionThread = threading.Thread(target=self.connectionHandler)
                    ConnectionThread.start()
                    break
                elif Data == '09':
                    print('Incorrect password')
                    break
                elif Data == '091':
                    print('Currently banned')
                    break
        else:
            print('Server capacity check failed')

    def parseUserData(self, Packet, Password = None):
        StatsString = Packet.replace('\x00', '')
        UserID = StatsString[1:][:3]
        Type = StatsString[:1]

        if Type == 'U':
            if self.InLobby == True:
                Username = StatsString[4:][:20].replace('#', '')

                self.OnlineUsers[UserID] = Username
                self.OnlineUserMap[Username] = UserID
            else:
                Username = StatsString[9:][:20].replace('#', '')

                self.OnlineUsers[UserID] = Username
                self.OnlineUserMap[Username] = UserID

    def parseUserMessage(self, SenderID, Packet):
        if SenderID in self.OnlineUsers:
            Sender = self.OnlineUsers[SenderID]
            MessageType = Packet[4:][:1]
            SenderMessage = Packet[5:]
            RawMessage = Packet[1:].replace(SenderID, '')

            if MessageType == '9':
                self.handleCommand(SenderID, Sender, SenderMessage, False)
            elif MessageType == 'P':
                self.handleCommand(SenderID, Sender, SenderMessage, True)
            elif MessageType == 'K':
                Kicker = Sender
                KickerID = SenderID

                if SenderMessage == self.BotID:
                    self.sendPublicMessage('{} is trying to kick me.'.format(Kicker))
                    return

                try:
                    ToKick = self.OnlineUsers[SenderMessage]
                except KeyError:
                    ToKick = None

                if ToKick != None:
                    ToKickID = SenderMessage

                    if ToKick in self.Allowed:
                        self.sendPublicMessage('Do not kick {}, {}.'.format(ToKick, Kicker))
                    else:
                        if Kicker in self.Allowed:
                            self.sendPublicMessage('Autokicking {}'.format(ToKick))
                            self.sendPacket(self.SocketConn, 'K{}'.format(ToKickID))
                        else:
                            self.sendPublicMessage('{} is trying to kick {}'.format(Kicker, ToKick))
            else:
                self.handleCommand(SenderID, Sender, RawMessage, True)

    def handleCommand(self, SenderID, Sender, SenderMessage, Private):
        RespondByPM = (False if Private == False else True)
        Message = SenderMessage.strip()
        MessageCheck = Message.split()

        if Message.startswith(self.CommandChar):
            Command = MessageCheck[0][1:].lower()
            HasArguments = (True if len(MessageCheck) > 1 else False)
            Arguments = (' '.join(MessageCheck[1:]) if HasArguments else None)

            if Command == 'move':
                if HasArguments and Private:
                    ServerName = Arguments.lower()
                    LNameToIP = {Key.lower():Value for Key, Value in self.NameToIP.items()}

                    if ServerName in LNameToIP:
                        self.SocketConn.shutdown(socket.SHUT_RD)
                        self.SocketConn.close()
                        del self.SocketConn

                        ServerIP, ServerPort = LNameToIP[ServerName].split(':')
                        self.connectToServer(self.BotUsername, self.BotPassword, ServerIP, int(ServerPort))
            elif Command == 'servers':
                ServerList = []

                for Key, Value in self.NameToIP.items():
                    ServerList.append(Key)

                self.sendPrivateMessage(SenderID, 'Servers: {}'.format( ', '.join(ServerList)))
            elif Command == 'start':
                if BotUsername not in self.Alted and self.InLobby and Private:
                    print('{} started their game.'.format(BotUsername))

                    self.Allowed.append(Sender)
                    #self.Alted.append(Sender)
                    self.OnlineUsers = {}
                    self.OnlineUserMap = {}
                    self.InLobby = False

                    RoomName = ' '
                    CreateRoom = '027200{}'.format(RoomName)
                    CheckRoom = '04{}'.format(RoomName)
                    Packets = [CreateRoom, CheckRoom, '05mp=77']

                    for Packet in Packets:
                        self.sendPacket(self.SocketConn, Packet)

                    self.Alting = True
                    AltingThread = threading.Thread(target=self.startAltingBot, args=(self.BotID, Sender))
                    AltingThread.daemon = True
                    AltingThread.start()
            elif Command == 'stop':
                if Sender in self.Allowed and not self.InLobby:
                    if self.Alting:
                        self.resetToLobby()

    def startAltingBot(self, SemderID, BotUsername):
        UserJoined = False

        while self.Alting:
            if SenderID in self.OnlineUsers:
                UserJoined = True
                Packets = ['509', '800500350', '10337103963020000000000000030', '4033703960037', '6807090', '7{}7090'.format(SemderID)]

                for Packet in Packets:
                    self.sendPacket(self.SocketConn, Packet)

                self.KillCount += 1
                time.sleep(1)
            else:
                if UserJoined:
                    break

        print('{}\'s game has ended.'.format(BotUsername))
        self.resetToLobby()

    def resetToLobby(self):
        self.OnlineUsers = {}
        self.OnlineUserMap = {}
        self.Allowed = ['']
        self.KillCount = 0
        self.Alting = False
        self.InLobby = True
        self.sendPacket(self.SocketConn, '03_')

if __name__ == '__main__':
    AKBot('', '', '69.164.207.72', 1138) # username, pw, ip, port
