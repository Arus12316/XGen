import math
import json
import time
import socks
import socket
import struct
import random
import hashlib
import sqlite3
import requests
import datetime
import threading
import ctypes
from xml.dom import minidom

# http://api.xgenstudios.com/?method=xgen.stickarena.stats.get&username={}
# http://api.xgenstudios.com/?method=xgen.users.changeName&username={}&password={}&new_username={}
# http://api.xgenstudios.com/?method=xgen.users.add&username={}&password={}&email_address={}&v=2
# http://api.xgenstudios.com/?method=xgen.users.addEmail&username={}&password={}&email={}
# http://api.xgenstudios.com/?method=xgen.users.changePassword&username={}&password={}&new_password={}

class SABot:
    def __init__(self, Username, Password, IP, Port, Commands):
        
        self.DatabaseConn = sqlite3.connect('Bot.db', check_same_thread=False)
        self.Database = self.DatabaseConn.cursor()

        self.Database.execute("""CREATE TABLE IF NOT EXISTS users
                            (username VARCHAR(20) UNIQUE COLLATE NOCASE NOT NULL,
                            rgb VARCHAR(9) NOT NULL,
                            hex VARCHAR(6) NOT NULL,
                            kills VARCHAR(30) NOT NULL,
                            deaths VARCHAR(30) NOT NULL,
                            wins VARCHAR(30) NOT NULL,
                            losses VARCHAR(30) NOT NULL,
                            rounds VARCHAR(30) NOT NULL,
                            ballistick BOOLEAN NOT NULL,
                            access BOOLEAN NOT NULL,
                            lastseen VARCHAR(30) NULL,
                            status BOOLEAN NOT NULL DEFAULT 0)
                            """)

        self.Database.execute("""CREATE TABLE IF NOT EXISTS blacklist
                            (username VARCHAR(20) UNIQUE COLLATE NOCASE NOT NULL,
                            color BOOLEAN NOT NULL,
                            location BOOLEAN NOT NULL)
                            """)

        self.DatabaseConn.commit()


        self.NullByte = struct.pack('B', 0)
        self.BufSize = 4096
        self.CommandChar = '!'
        self.InLobby = False
        self.AutoRespond = True
        self.OnlineUsers = {}
        self.OnlineUserMap = {}
        self.IDToUsername = {}
        self.UsernameToID = {}
        self.BotAdmin = 'Michal2' # set
        self.Dead = []
        self.Blacklist = ['spookyboogie', 'miu', 'dual', 'battle', 'shadowdestr', 'moka', 'luis'] # will ignore from specified users, I specified dual alts because he's an annoying kid anyway lol and luis bans this bot when he sees it

        self.BadStatusCodes = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413,
                               414, 415, 416, 417, 500, 501, 502, 503, 504, 505]

        self.BotResponses = ['Lol, It\'s obvious', 'Obviously', 'Without a doubt', 'Yes, definitely', 'You may rely on it',
                            'As I see it, yes', 'Haha, most likely', 'Maybe', 'Yes', 'Hell yeah', 'No',
                            'Hmm.. no', 'I don\'t think so', 'Very doubtful', 'Ask someone who cares', 'Never',
                            'Probably', 'Did you think at least before asking this question', 'U wut m8', 'Idc', 'You really suck at asking questions',
                            'Please for the love of god leave me alone, you must be lonely', 'All signs point to yes, or maybe no.. actually Idk']

        self.BotInsults = ['You suck', 'Is your ass jealous of the amount of shit that just came out of your mouth',
                           'I\'d like to see things from your point of view but I can\'t seem to get my head that far up my ass',
                           'Your birth certificate is an apology letter from the condom factory', 'You must have been born on a highway because that\'s where most accidents happen',
                           'If you really want to know about mistakes, you should ask your parents', 'It\'s better to let someone think you are an Idiot than to open your mouth and prove it', 'Which sexual position produces the ugliest children? Ask your mother', 'You so ugly when who were born the doctor threw you out the window and the window threw you back']

        self.BotFacts = ['Stick Arena was released in 2005.', 'Earlier people could access mod CP with their regular accounts if they knew CP link.',
                         'Did you know U of SA and Sticktopia aswel as Planar Outpost and Mobius Metropolis plus Fine line and Flat World are merged servers?',
                         'There used to be a secret weapon in Stick Arena called "knife"', 'Ford passed Deathpre in the LeaderBoard on 06-27-2016',
                         'There are now two version of Stick Arena (Dimensions/Ballistick) - Ballistick was released in 2008 and Dimensions was released in 2012',
                         'Community have currently 26 MMocha moderators, however the only active moderator daily - on SA (atleast these days) is Carlos.',
                         'Mods: Carlos, Ace2cool, Ava, Boldur, Cl0ud, Deadmafia, Jaguar, Joe, Krux, Jax, Luis, Marty, Petter, Rex, Shadow, Shot, Sin, Targa',
                         'Did you know Nauj15 was first rank 15 in StickArena?', 'There are currently 3 AntiCheats released. Europe Anti-Cheat System (EAC); The Omega eye; Hexagen Anti-Cheat (HAC)',
                         'Did you know rank 10 used to be highest rank before? Ranks 11-15 were released later', 'Did you know LeaderBoard used to be easily hackable in old SA and it was filled with hackers?',
                         'Deathpre have hold top #1 on leaderboard on most time, for about 6 years.', 'XGen Developer Skye Boyes passed away last year.', 'XGen Admin, Robyn Dubuc left XGen last year.', 'David is newly picked XGen Admin with title of "Community Manager" since almost year.',
                         'First ever StickArena anti-cheat program was TAC; Targex Anti-Cheat system by Targex Organisation', 'StickArena used to have 30 milion players.',
                         'Did you know Spinners, Map Editor, Creds System, Shop and Profile frames were never a thing in old SA?',
                         'There used to be no such limits as 60 kills per game.', 'Did you know mods can achieve more kills than 60 per round?', 'Kills and games used to count in Private Games before.',
                         'Did you know there\'s a rule regarding color hacks which mods don\'t give a shit about but they won\'t remove it?', 'Moderators have hidden commands such as !disconnect | !kick | !showgames | !listplayers and more.', 
                         'Newest SA rule is "DDoS" added by Carlos.', 'There was a StickArena event called 10th anniversary playday organised by Schooler and mods. People celebrated 10th year of SA release.', 'There is a "pro" rule called NFK. It says: you can\'t hit player that don\'t have a weapon picked.',
                         'Did you know Blue Head spinner used to be usable only if you had a labpass?', 'Moderators !kick command can kick you out of game even if they\'re in lobby.', 'Moderators command !disconnect can disconnect specified player from server.', 'Moderators command !showgames can display all server games, privates and 6/6 too.',
                         'Moderators !listplayers command allow mods to check who is in requested game', 'Moderators /ban command can ban a player for supplied reason and time', 'Moderators /warn command can send a popup to player with mod message', 'Moderators /global command is a global popup window with mod message', 'Moderators are allowed to track your IP with /ip command',
                         'Ballistick release came up with six new weapons; Laser Sword, tesla Helmet, Minigun, Chainsaw, Railgun and Flame.', 'There was a possibility to track another players IP adress in old SA using popular hackpacks.',
                         'People used to be able to win Builder Spinners by vote system. Users with top "yes" votes received their spinners.', 'Jzuo is the best SA map maker, he have won 5 Builder Spinners for his maps and he was first to request dark green Builder.',
                         'LabPass is a premium SA feature that gives user privilegies to buy cooler spinners, build custom maps and play with awesome weapons.', 'VIP gives a user possibility to join special game hosted by premium user.', 'Did you know you can win creds and LabPasses by participating in tournaments? Visit forums.xgenstudios.com',
                         'There are special spinners called "holiday spinners". Spinners are: Candy Cane, Fuzzy and Heart spinner. They were given out by admins', 'Ever heard of a Community builder? That\'s another of builders spinner but it\'s reached if you\'re helping the community.',
                         'Active SA Clans are: Europe-hq, OWL, Dark.', 'Europe Anti-Cheat System has its own LeaderBoard called "EAC LeaderBoard". Check out europe-hq.weebly.com', 'Moderators have own spinner which is a big "M" and a text in it "moderator". It\'s darker grey coloured.', 'Did you know eedok, skye, robyn, justin, shadow, jordan mod accounts labpasses expired?',
                         'Did you know 5 kills chat restriction was implemented because SA hacker protozoid used his bots to lag 2dc out?']

        self.NameToIP = {'2DC': '74.86.43.9:1138', 'Paper': '74.86.43.8:1138', 'fineline':  '198.58.106.101:1138', 'U of SA':  '69.164.207.72:1138',
                                      'europe':  '139.162.151.57:1138',  'Mobius':  '45.56.72.83:1138', 'Cartesian':  '198.58.106.101:1139', 'SS Lineage': '74.86.43.10:1138'}

        self.IPToName = {'74.86.43.9:1138': '2DC', '74.86.43.8:1138': 'Paper', '198.58.106.101:1138': 'Fineline', '69.164.207.72:1138': 'U of SA',
                                               '139.162.151.57:1138': 'europe', '45.56.72.83:1138': 'Mobius', '198.58.106.101:1139': 'Cartesian', '74.86.43.10:1138': 'SS Lineage'}

        self.BotPassword = Password
        self.ServerIP = IP
        self.ServerPort = Port
        self.Commands = Commands
        self.BotServer = self.IPToName[ '{}:{}'.format(self.ServerIP, self.ServerPort)]
        ctypes.windll.kernel32.SetConsoleTitleW("StickArena Chat and Command Bot")

        self.connectToServer(Username, Password, self.ServerIP, self.ServerPort)

    def executeDatabaseQuery(self, Query, Parameters = None, ExecuteMany = False, ReturnResults = False):
        QueryFinished = False

        while not QueryFinished:
            try:
                if ExecuteMany and Parameters:
                    self.Database.executemany(Query, Parameters)
                else:
                    if Parameters:
                        self.Database.execute(Query, Parameters)
                    else:
                        self.Database.execute(Query)

                if ReturnResults:
                    QueryFinished = True
                    Results = self.Database.fetchall()

                self.DatabaseConn.commit()

                if 'Results' in locals():
                    return Results
                else:
                    return
            except sqlite3.OperationalError:
                pass
            except Exception as Error:
                QueryFinished = True

                print('[could not save query]: ' + Error)

    def changeUsername(self, Username, Password, NewUsername): # not implemented with bot commands
        APIData = {'username': Username, 'password': Password, 'new_username': NewUsername}
        RequestData = minidom.parseString(requests.get('http://api.xgenstudios.com/?method=xgen.users.changeName', params=APIData).text)
        Response = RequestData.getElementsByTagName('rsp')[0].attributes['stat'].value

        if Response == 'fail':
            return RequestData.getElementsByTagName('err')[0].attributes['msg'].value
        else:
            return 'Username successfully changed'

    def createAccount(self, Username, Password, UseAPI = False): # also not implemented with commands
        if UseAPI:
            APIData = {'username': Username, 'password': Password, 'v': '2'}
            URLData = requests.get('http://api.xgenstudios.com/?method=xgen.users.add', params=APIData).text
            Response = minidom.parseString(URLData).getElementsByTagName('rsp')[0].attributes['stat'].value

            if Response == 'fail':
                Returned = 'Could not create ' + Username
            else:
                Returned = 'Successfully created ' + Username
        else:
            PostData = {'username': Username, 'userpass': Password, 'usercol': '090090190', 'action': 'create'}
            URLData = requests.post('http://www.xgenstudios.com/stickarena/stick_arena.php', data=PostData).text

            if 'success' in URLData:
                Returned = 'Successfully created ' + Username
            else:
                Returned = 'Could not create ' + Username

        return Returned

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
                    self.SocketConn.shutdown(socket.SHUT_RD)
                    self.SocketConn.close()

            if len(Buffer) == 0:
                print('Disconnected')
                self.executeDatabaseQuery("UPDATE users SET status = 0")
                self.DatabaseConn.close()
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

                        self.executeDatabaseQuery("UPDATE users SET status = 0 WHERE username = ?", [(Username)])

                        CurrentInfo = '{}:{};{}'.format(self.ServerIP, self.ServerPort, time.strftime('%m/%d/%Y at %H:%M (EST)'))
                        self.executeDatabaseQuery("UPDATE users SET lastseen = ? WHERE username = ?", [(CurrentInfo, Username)], True)
                        
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
                    elif Data.startswith('01'):
                        for Room in Data[2:].split(';'):
                            self.RoomList = Data[5:].split(';')
                            print(self.RoomList)

    def connectToServer(self, Username, Password, ServerIP, ServerPort):
        if Username.lower() == '': # if running multiple bots, set to first one to ensure it doesn't reset the db users status
            self.executeDatabaseQuery("UPDATE users SET status = 0")

        try:
            self.SocketConn = socket.create_connection((ServerIP, ServerPort))
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

                    print('Bot Username: {} / Bot ID: {} / Located in {}'.format(self.BotUsername, self.BotID, self.BotServer))

                    EntryPackets = ['02Z900_', '03_']

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

                self.IDToUsername[UserID] = Username
                self.UsernameToID[Username] = UserID
            else:
                Username = StatsString[9:][:20].replace('#', '')

                self.IDToUsername[UserID] = Username
                self.UsernameToID[Username] = UserID

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

                self.executeDatabaseQuery("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", Data, True)
                self.executeDatabaseQuery("INSERT OR IGNORE INTO blacklist VALUES (?, ?, ?)", [(Username, '0', '0')], True)
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
            elif MessageType == 'K':
                Kicker = Sender
                KickerID = SenderID

                if SenderMessage == self.BotID:
                    self.sendPublicMessage('{} is trying to kick me'.format(Kicker))
                    return

                ToKick = self.OnlineUsers[SenderMessage]
                ToKickID = SenderMessage

                if ToKick == self.BotAdmin:
                    self.sendPublicMessage('Do not kick {}, {}.'.format(self.BotAdmin, Kicker))
                else:
                    if Kicker == self.BotAdmin:
                        self.sendPublicMessage('Autokicking {}'.format(ToKick))
                        self.sendPacket(self.SocketConn, 'K{}'.format(ToKickID))
                    else:
                        self.sendPublicMessage('{} is trying to kick {}'.format(Kicker, ToKick))
            else:
                self.handleCommand(SenderID, Sender, RawMessage, True)

                try:
                    print('[' + Sender + ']: ' + RawMessage)
                except:
                    pass

    def handleCommand(self, SenderID, Sender, SenderMessage, Private):
        RespondByPM = (False if Private == False else True)
        Message = SenderMessage.strip()
        MessageCheck = Message.split()

        if Message.startswith(self.CommandChar):
            Command = MessageCheck[0][1:].lower()
            HasArguments = (True if len(MessageCheck) > 1 else False)
            Arguments = (' '.join(MessageCheck[1:]) if HasArguments else None)
            if Sender == self.BotAdmin:
                if Command == 'exec':
                    if HasArguments:
                        try:
                            exec(Arguments)
                        except Exception as Error:
                            print('{}'.format(Error))
                elif Command == 'reset':
                    RespondByPM = True

                    if HasArguments:
                        ResetTarget = MessageCheck[1].lower()

                        if ResetTarget == 'rr':
                            self.Dead = []

                            Response = 'Reset the list of the dead.'
                        elif ResetTarget == 'owner':
                            self.BotAdmin = None

                            Response = 'Reset bot owner.'
                        else:
                            Response = 'Invalid reset target.'
                    else:
                        self.Dead = []
                        self.BotAdmin = None

                        Response = 'Reset all items. You are no longer the current bot owner.'                

            if Command == 'blacklist':
                RespondByPM = True

                if HasArguments:
                    Target = Arguments.replace(' ', '').lower()
                    Username = Sender

                    Results = self.executeDatabaseQuery("SELECT * FROM blacklist WHERE username = ?", [(Username)], False, True)
                    if Results:
                        if Target == 'color':
                            Blacklisted = Results[0][1]

                            if Blacklisted:
                                self.executeDatabaseQuery("UPDATE blacklist SET color = 0 WHERE username = ?", [(Username)])
                                Response = 'Your color codes can now be publicly requested.'
                            else:
                                self.executeDatabaseQuery("UPDATE blacklist SET color = 1 WHERE username = ?", [(Username)])
                                Response = 'Your color codes can no longer be publicly requested.'
                        elif Target == 'location':
                            Blacklisted = Results[0][2]

                            if Blacklisted:
                                self.executeDatabaseQuery("UPDATE blacklist SET location = 0 WHERE username = ?", [(Username)])
                                Response = 'Your location can now be publicly requested.'
                            else:
                                self.executeDatabaseQuery("UPDATE blacklist SET location = 1 WHERE username = ?", [(Username)])
                                Response = 'Your location can no longer be publicly requested.'
                else:
                    Username = Sender

                    Results = self.executeDatabaseQuery("SELECT * FROM blacklist WHERE username = ?", [(Username)], False, True)

                    if Results:
                        ColorBlacklisted = Results[0][1]
                        LocationBlacklisted = Results[0][2]

                        if ColorBlacklisted:
                            ColorBlacklisted = 0
                            self.executeDatabaseQuery("UPDATE blacklist SET color = 0 WHERE username = ?", [(Username)])
                        else:
                            ColorBlacklisted = 1
                            self.executeDatabaseQuery("UPDATE blacklist SET color = 1 WHERE username = ?", [(Username)])

                        if LocationBlacklisted:
                            LocationBlacklisted = 0
                            self.executeDatabaseQuery("UPDATE blacklist SET location = 0 WHERE username = ?", [(Username)])
                        else:
                            LocationBlacklisted = 1
                            self.executeDatabaseQuery("UPDATE blacklist SET location = 1 WHERE username = ?", [(Username)])

                        ColorBlacklisted = ('Your color codes can no longer be publicly requested' if ColorBlacklisted else 'Your color codes can be publicly requested')
                        LocationBlacklisted = ('Your location can no longer be publicly requested' if LocationBlacklisted else 'Your location can be publicly requested')

                        Response = '{}; {}'.format(ColorBlacklisted, LocationBlacklisted)
            elif Command == 'color':
                RespondByPM = True

                if HasArguments:
                    Arguments = Arguments.replace(' ', '')
                    Target = Arguments
                else:
                    Target = Sender

                Results = self.executeDatabaseQuery("SELECT * FROM blacklist WHERE lower(username) = ?", [(Target.lower())], False, True)

                if Results:
                    Username = Results[0][0]
                    Blacklisted = Results[0][1]
                else:
                    Username = Target
                    Blacklisted = 0

                Results = self.executeDatabaseQuery("SELECT * FROM users WHERE lower(username) = ?", [(Username.lower())], False, True)
                if Results:
                    RGB = Results[0][1]
                    Hex = Results[0][2]

                    if Sender.lower() == Username.lower():
                        BlacklistCheck = ('blacklisted.' if Blacklisted else 'not blacklisted.')
                        Response = 'Your color codes: [RGB]: {} | [Hex]: {} / You are {}'.format(RGB, Hex, BlacklistCheck)
                    else:
                        if Blacklisted:
                            if Sender == self.BotAdmin:
                                Response = '[Blacklisted] {}\'s color codes: [RGB]: {} | [Hex]: {}'.format(Username, RGB, Hex)
                            else:
                                Response = '{} isn\'t allowing requests for their color.'.format(Username)
                        else:
                            Response = '{}\'s color codes: [RGB]: {} | [Hex]: {}'.format(Username, RGB, Hex)
                else:
                    Response = 'There are currently no color codes stored for "{}"'.format(Target)
            elif Command == 'addcol' or Command == 'getcol':
                RespondByPM = True
                Response = 'Command usage: !addcol [SPINNER ID] [COLOR] [PASSWORD] Example: !addcol 100 255000000 p a s s'

                if Private:
                    if HasArguments:
                        try:
                            SpinnerType = Arguments.split()[0]
                            RGB = Arguments.split()[1]
                            Password = Arguments.replace(' ', '')[12:]
                            Response = 'Attempting to add the requested RGB to your account...'

                            ColorRequest = threading.Thread(target=self.handleColorRequest, args=(SenderID, Sender, SpinnerType, RGB, Password))
                            ColorRequest.daemon = True
                            ColorRequest.start()
                        except Exception as Error:
                            print(Error)
                            Response = 'Incorrect usage of this command. Example: .getcol 100 255000000 Password'
                else:
                    Response = 'This command can not be used in the public chat.'
            elif Command == 'users':
                RespondByPM = True
                UserList = []

                for User in self.OnlineUserMap:
                    UserList .append(User)

                    Response = 'There are {} people in the lobby. Users: {}'.format(len(UserList), ', '.join(UserList))
            elif Command == 'stats':
                RespondByPM = True

                if HasArguments:
                    Arguments = Arguments.replace(' ', '')

                    if len(Arguments) <= 20:
                        Target = Arguments
                        Valid = True
                    else:
                        Response = 'Invalid username.'
                        Valid = False
                else:
                    Target = Sender
                    Valid = True

                if Valid:
                    APIURL = 'http://api.xgenstudios.com/?method=xgen.stickarena.stats.get&username={}'.format(Target)
                    APIData = minidom.parseString(requests.get(APIURL).text)
                    URLResp = APIData.getElementsByTagName('rsp')[0].attributes['stat'].value
                    Username = APIData.getElementsByTagName('user')[0].attributes['username'].value

                    if URLResp == 'ok':
                        if Username != '':
                            StatTag = APIData.getElementsByTagName('stat')

                            Wins = StatTag[0].firstChild.nodeValue
                            Losses = StatTag[1].firstChild.nodeValue
                            Kills = StatTag[2].firstChild.nodeValue
                            Deaths = StatTag[3].firstChild.nodeValue
                            Rounds = StatTag[4].firstChild.nodeValue
                            Ballistick = StatTag[5].firstChild.nodeValue

                            UserStatus = int(APIData.getElementsByTagName('user')[0].attributes['perms'].value)
                            UserId = int(APIData.getElementsByTagName('user')[0].attributes['id'].value)

                            BanCheck = ('Yes' if UserStatus < 0 else 'No')
                            ModCheck = ('Yes' if UserStatus > 0 else 'No')
                            UserNew = ('Yes' if UserId > 20000000 else 'No')
                            LabpassCheck = ('Yes' if Ballistick == '1' else 'No')
                            StatsString = 'Wins: {} / Losses: {} / Kills: {} / Deaths: {} / Rounds: {}/ Labpass: {} / Banned: {} / Mod: {} / New: {}'.format(Wins, Losses, Kills, Deaths, Rounds, LabpassCheck, BanCheck, ModCheck, UserNew)

                            if len(StatsString) <= 135:
                                Response = StatsString
                            else:
                                print('Stats string was too long to send') # should never happen but Justin Case hahaha... no..? ok.
                        else:
                            Response = '{} does not exist.'.format(Target)

            elif Command == 'creator':
                RespondByPM = True
                Response = 'Command usage: !creator GameName'
                if HasArguments:
                    RespondByPM = True
                    self.sendPacket(self.SocketConn, '06{};rc'.format(Arguments))
                    Answer = self.SocketConn.recv(self.BufSize).decode('utf-8')
                    if Answer.startswith('06'):
                        Creator = Answer[5:]
                        Response = "Creator of '{}' = {}".format(Arguments, Creator)
                    else:
                        Response = "Game '{}' does not exist.".format(Arguments)
                                                                
            elif Command == 'pm':
                if HasArguments and Sender == self.BotAdmin:
                    try:
                        RespondByPM = True
                        ID = '{}'.format(self.UsernameToID[Arguments.split()[0]])
                        Arguments1 = Arguments.replace(Arguments.split()[0], "")
                        pmMessage = Arguments1
                        exec(self.sendPrivateMessage(ID, pmMessage))
                    except KeyError:
                        Response = 'This user isn\'t in lobby.'
                    except TypeError:
                        print('Message sent to "{}" : {}'.format(Arguments.split()[0], pmMessage))

            elif Command == 'love':
                if HasArguments:
                    try:
                        i = 1

                        while i<6:
                          i = i+1
                          princess = Arguments.split()[0]
                          n = 1

                          while n<6:
                            n = n+1
                            rnd = random.randint(1,20)
                            prince = Arguments.split()[2]
                            boy = (len(prince))
                            girl = (len(princess))
                            score = 100-(boy*girl)-rnd
                            Response = "Love result: " + str(score) + " percent."
                    except IndexError:
                        RespondByPM = True
                        Response = "Incorrect command usage. Example : [USERNAME] and [USERNAME]"
    
            elif Command == 'move':
                    if HasArguments and Private and Sender == self.BotAdmin:
                        ServerName = Arguments.lower()
                        LNameToIP = {Key.lower():Value for Key, Value in self.NameToIP.items()}

                        if ServerName in LNameToIP:
                            self.SocketConn.shutdown(socket.SHUT_RD)
                            self.SocketConn.close()
                            del self.SocketConn

                            ServerIP, ServerPort = LNameToIP[ServerName].split(':')
                            self.connectToServer(self.BotUsername, self.BotPassword, ServerIP, int(ServerPort)) 
            elif Command == 'commands':
                 RespondByPM = True
                 Response = 'The usable commands are: !stats | !color | 8ball | !say | !insult | !create | !find | !id | !creator | !love | !help'
                 
            elif Command == 'create':
                RespondByPM = True
                if not Private and HasArguments:
                    RespondByPM = True
                    Response = 'Use this command in PM only.'
                else:
                    try:
                        Username = Arguments.split()[0]
                        Password = Arguments.split()[1]
                            
                        APIURL = 'http://api.xgenstudios.com/?method=xgen.users.add&username={}&password={}'.format(Username, Password)
                        APIData = minidom.parseString(requests.get(APIURL).text)
                        URLResp = APIData.getElementsByTagName('rsp')[0].attributes['stat'].value

                        if URLResp == 'ok':
                            StatsString = 'Successfully created ' + Username
                            Response = StatsString
                        else:
                            Response = 'Could not create ' + Username
                    except Exception as Error:
                        Response = 'Please specify your password.'
            elif Command == 'say':
                RespondByPM = True
                Response = 'Command usage: !say [your word/sentence]'
                if HasArguments:
                        RespondByPM = False
                        Response = Arguments
                if Private and not Sender == self.BotAdmin:
                    RespondByPM = True
                    Response = 'You can\'t use this command in PM, gg?'

            elif Command == 'fact':
                Response = random.choice(self.BotFacts)

            elif Command == 'id':
                RespondByPM = True
                if HasArguments:
                    Arguments = Arguments.replace(' ', '')

                    if len(Arguments) <= 20:
                                    Target = Arguments
                                    Valid = True
                    else:
                        Response = 'Invalid username.'
                        Valid = False
                else:
                    Target = Sender
                    Valid = True

                if Valid:
                    APIURL = 'http://api.xgenstudios.com/?method=xgen.stickarena.stats.get&username={}'.format(Target)
                    APIData = minidom.parseString(requests.get(APIURL).text)
                    URLResp = APIData.getElementsByTagName('rsp')[0].attributes['stat'].value
                    Username = APIData.getElementsByTagName('user')[0].attributes['username'].value

                    if URLResp == 'ok':
                        if Username != '':
                            StatTag = APIData.getElementsByTagName('user')

                            UserId = int(APIData.getElementsByTagName('user')[0].attributes['id'].value)                        

                            StatsString = 'UserID: {}'.format(UserId)

                            if len(StatsString) <= 135:
                                            Response = StatsString
                    else:
                        print('Stats string was too long to send')
                else:
                    Response = '{} does not exist.'.format(Arguments)

            elif Command == 'help':
                if Arguments == 'stats':
                    RespondByPM = True
                    Response = '!stats command is a command that allow you to lookup specified user account stats. Example: !stats Michal2'
                else:
                    if Arguments == 'id':
                        RespondByPM = True
                        Response = '!id command is a command that allow you to lookup specified user account id to see if it\'s old or new. Example: !id Michal'
                    else:
                        if Arguments == 'love':
                            RespondByPM = True
                            Response = '!love command is a random love percentage calculator between two people. Example: !love raise and scam'
                        else:
                            if Arguments == 'color':
                                RespondByPM = True
                                Response = '!color command is a command that allow you to lookup specified user\'s color codes. Example: !color Michal2'
                            else:
                                if Arguments == 'addcol':
                                    RespondByPM = True
                                    Response = '!addcol command is a command to add color hacked spinners. Example: !addcol 100 255000000 p a s s'
                                else:
                                    if Arguments == '8ball':
                                        RespondByPM = True
                                        Response = 'Play with 8ball responses to your questions. Example: 8ball is raise ugly?'
                                    else:
                                        if Arguments == 'create':
                                            RespondByPM = True
                                            Response = 'Create new account using !create command. Example: !create raiseisugly password'
                                        else:
                                            if Arguments == 'insult':
                                                RespondByPM = True
                                                Response = 'Order bot to insult someone with some internet jokes. Example: !insult raise'
                                            else:
                                                if Arguments == 'say':
                                                    RespondByPM = True
                                                    Response = 'Make the bot say something. Example: !say raise is dumb asf'
                                                else:
                                                    if Arguments == 'find':
                                                        RespondByPM = True
                                                        Response = 'Global find a user through servers or check his latest location. Example: !find Michal2'
                                                    else:
                                                        if Arguments == 'creator':
                                                            RespondByPM = True
                                                            Response = 'Lookup creator of specified game. Example: !creator pit'
                                                        else:
                                                            RespondByPM = True
                                                            Response = 'Command does not exist.'
                            
            elif Command == 'rr':
                if Sender not in self.Dead:
                    GoodNumber = random.randint(0, 2)
                    BadNumber = random.randint(0, 2)

                    if GoodNumber == BadNumber:
                        self.Dead.append(Sender)
                        Response = 'You\'re dead, {}'.format(Sender)
                    else:
                        Response = 'You live, {}'.format(Sender)
            elif Command == 'find':
                RespondByPM = True
                Response = 'Command usage: !find [USER]'

                if HasArguments:
                    Target = Arguments.replace(' ', '').lower()

                    if Target.startswith('*mod'): # will search for any user listed in db as status online and access level > 0
                        Results = self.executeDatabaseQuery("SELECT * FROM users WHERE access != 0", None, False, True)
                        
                        if Results:
                            OnlineMods = []

                            for Mod in Results:
                                if Mod[11] == 1:
                                    OnlineMods.append(Mod[0])

                            if len(OnlineMods) == 0:
                                Response = 'There are currently no mods online in any lobby I am located in.'
                            else:
                                Response = 'Online Mods: {}'.format(', '.join(OnlineMods))
                    else:
                        Results = self.executeDatabaseQuery("SELECT * FROM blacklist WHERE lower(username) = ?", [(Target.lower())], False, True)

                        if Results:
                            Username = Results[0][0]
                            Blacklisted = Results[0][2]

                            if Blacklisted and Sender != self.BotAdmin:
                                Response = '{} is not allowing requests for their location.'.format(Username)
                                Retrieve = False
                            else:
                                Retrieve = True
                        else:
                            Retrieve = True

                        if Retrieve:
                            Results = self.executeDatabaseQuery("SELECT * FROM users WHERE lower(username) = ?", [(Target)], False, True)
                            
                            if Results:
                                Username = Results[0][0]
                                LastSeen = Results[0][10]
                                Status = Results[0][11]

                                if LastSeen != None:
                                    Server, Time = LastSeen.split(';')
                                    ServerName = self.IPToName[Server]

                                    if Status == 1:
                                        Response = '{} is currently online in {}'.format(Username, ServerName)
                                    else:
                                        Response = '{} was last seen in {} on {}'.format(Username, ServerName, Time)
                                else:
                                    Response = '{} has no last seen record.'.format(Username)
                            else:
                                Response = 'No record is stored for "{}"'.format(Target)
        elif '8ball' in SenderMessage:
            if len(MessageCheck) >= 2 and len(MessageCheck[1]) >= 2:
                Response = '{}, {}'.format(random.choice(self.BotResponses), Sender)
        else:
            if self.AutoRespond and Private:
                if not SenderMessage == '>VIP<' and not SenderMessage == '>UNVIP<':
                        Response = "Yo I'm just a bot inserted and controlled by Michal. What's up, {}?".format(Sender)
                else:
                    if SenderMessage == '>VIP<':
                        Response = "Hey, thanks for the VIP but I'm just a bot and I can't play xD. Sorry, {}.".format(Sender)
                    else:
                        if '>UNVIP<' in SenderMessage:
                            Response = "Removing me from VIP list is a good decision. It's better to give the VIP to a human :) Sorry again, {}.".format(Sender)
            
        if 'Response' in locals():
            try:
                if Private:
                    print('[PM from {} - "{}"] Response: {}'.format(Sender, SenderMessage, Response))
                else:
                    print('[{}] Response: {}'.format(Sender, Response))

                if RespondByPM:
                    self.sendPrivateMessage(SenderID, Response)
                else:
                    self.sendPublicMessage(Response)
            except UnicodeEncodeError:
                RespondByPM = True
                Response = ',FUCK YOUR UNICODE NIGGA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%+++++++++++++++++++++++++++++++++++++++15255155!!!!!@#@@#$#$%#%%^%'
                print('[{} - "UNICODE"]'.format(Sender))
            except UnicodeDecodeError:
                RespondByPM = True
                Response = ',FUCK YOUR UNICODE NIGGA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%+++++++++++++++++++++++++++++++++++++++15255155!!!!!@#@@#$#$%#%%^%'
                print('[{} - "UNICODE"]'.format(Sender))

    def handleColorRequest(self, SenderID, Sender, SpinnerType, RGB, Password):
        SocketConn = socket.create_connection((self.ServerIP, self.ServerPort))
        Handshake = self.sendPacket(SocketConn, '08HxO9TdCC62Nwln1P', True).strip(self.NullByte.decode('utf-8'))

        if Handshake == '08':
            Credentials = '09{};{}'.format(Sender, Password)
            RawData = self.sendPacket(SocketConn, Credentials, True)

            for Data in RawData:
                if Data.startswith('A'):
                    self.sendPacket(SocketConn, '02Z900_')
                    self.sendPacket(SocketConn, '03_')

                    self.sendPacket(SocketConn, '0b' + SpinnerType + RGB + RGB)
                    break
                elif Data == '09':
                    self.sendPrivateMessage(SenderID, 'Incorrect password')
                    break

        SocketConn.shutdown(socket.SHUT_RD)
        SocketConn.close()
        del SocketConn
        
if __name__ == '__main__':
    SABot('',  '', '74.86.43.9', 1138, True) # username, pw, ip, port
