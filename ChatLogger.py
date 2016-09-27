import time
import socks
import socket
import struct
import datetime
import threading
import ctypes
from datetime import datetime

class Chatlogger:
    def __init__(self, Username, Password, IP, Port):
        self.NullByte = struct.pack('B', 0)
        self.BufSize = 4096
                         
        self.NameToIP = {'2D Central': '74.86.43.9:1138', 'Paper Thin City': '74.86.43.8:1138', 'Fine Line Island':  '198.58.106.101:1138', 'U of SA':  '69.164.207.72:1138',
                                      'Amsterdam':  '139.162.151.57:1138',  'Mobius Metro':  '45.56.72.83:1138', 'Cartesian':  '198.58.106.101:1139'}

        self.IPToName = {'74.86.43.9:1138': '2D Central', '74.86.43.8:1138': 'Paper Thin City', '198.58.106.101:1138': 'Fine Line Island', '69.164.207.72:1138': 'U of SA',
                                               '139.162.151.57:1138': 'Amsterdam', '45.56.72.83:1138': 'Mobius Metro', '198.58.106.101:1139': 'Cartesian'}

        self.ServerIP = IP
        self.ServerPort = Port
        self.BotServer = self.IPToName[ '{}:{}'.format(self.ServerIP, self.ServerPort)]
        ctypes.windll.kernel32.SetConsoleTitleW("StickArena Chat Messages Logger")

        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150)
        socket.create_connection = socks.create_connection
        socket.socket = socks.socksocket

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

    def connectionHandler(self):
        Buffer = b''

        while hasattr(self, 'SocketConn'):
            try:
                Buffer += self.SocketConn.recv(self.BufSize)
            except OSError:
                if hasattr(self, 'SocketConn'):
                    self.SocketConn.shutdown(socket.SHUT_RD)
                    self.SocketConn.close()

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
                        Username = self.OnlineUsers[UserID]

                        del self.OnlineUserMap[Username]
                        del self.OnlineUsers[UserID]
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
                    elif Data.startswith('0c'):
                        print(Data[2:])

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
                    self.BotID = Data[1:][:3]
                    self.BotUsername = Data[4:][:20].replace('#', '')
                    self.BotCred = Data[43:].split(';')[8]

                    print('Bot Username: {} / Bot ID: {} / Bot Cred: {} / Located in {}'.format(self.BotUsername, self.BotID, self.BotCred, self.BotServer))

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
                StatsString = StatsString[24:]

                self.OnlineUsers[UserID] = Username
                self.OnlineUserMap[Username] = UserID

                RGBString = StatsString[:9]
                R = int(RGBString[:3])
                G = int(RGBString[3:][:3])
                B = int(RGBString[6:][:3])
                HexString = '#%02x%02x%02x' % (R, G, B)

                Stats = StatsString[9:].split(';')
                CurrentInfo = '{}:{};{}'.format(self.ServerIP, self.ServerPort, time.strftime('%m/%d/%Y at %H:%M (EST)'))
                Data = [(Username, RGBString, HexString, Stats[0], Stats[1], Stats[2], Stats[3], Stats[4], Stats[5], Stats[6], CurrentInfo, '1')]                
            else:
                Username = StatsString[9:][:20].replace('#', '')

                self.OnlineUsers[UserID] = Username
                self.OnlineUserMap[Username] = UserID

    def parseUserMessage(self, SenderID, Packet):
        if SenderID in self.OnlineUsers:
            Sender = self.OnlineUsers[SenderID]

            if Sender in self.Blacklist:
                return

            NoUseTypes = ['1', '2', '4', '5', '6', '7', '8', '~']
            MessageType = Packet[4:][:1]
            SenderMessage = Packet[5:]
            RawMessage = Packet[1:].replace(SenderID, '')

            if MessageType in NoUseTypes:
                return
            elif MessageType == '9':
                if self.Commands:
                    self.handleCommand(SenderID, Sender, SenderMessage, False)
            elif MessageType == 'P':
                if self.Commands:
                    self.handleCommand(SenderID, Sender, SenderMessage, True)
            else:
                try:
                    print('[' + Sender + ']: ' + RawMessage)
                except:
                    pass
            if not Private:
                try:
                    print('[{} in {}] Message: {}'.format(Sender, self.BotServer, SenderMessage))
                    Data = open('logs.txt', 'a')
                    Data.write('[{} in {} on {}] Message: {}\n'.format(Sender, self.BotServer, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), SenderMessage))
                    Data.close()
                    if Private:
                        print('[PM from {} in {}] Message: {}'.format(Sender, self.BotServer, SenderMessage))
                        Data = open('logs.txt', 'a')
                        Data.write('[PM from {} in {} on {}] Message: {}\n'.format(Sender, self.BotServer, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), SenderMessage))
                        Data.close()
                except UnicodeEncodeError:
                    print('[UNICODE]')
                except UnicodeDecodeError: 
                    print('[{} - "UNICODE"]'.format(Sender))

if __name__ == '__main__': # username, pw
    Chatlogger('',  '', '74.86.43.9', 1138)
    chatlogger('', '', '74.86.43.8', 1138)
    Chatlogger('', '', '198.58.106.101', 1138) 
    Chatlogger('', '', '69.164.207.72', 1138)
    Chatlogger('', '', '139.162.151.57', 1138)
    Chatlogger('', '', '45.56.72.83', 1138)
    Chatlogger('', '', '198.58.106.101', 1139)
