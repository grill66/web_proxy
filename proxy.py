import socket
import os
import sys
import threading
import time
import ctypes

class PROXYSESSION(threading.Thread): #Inherit Thread Object

    SessionCount = 0
    # CPSocket : Client to Proxy Socket
    # PSSocket : Proxy to Web server Socket

    # C2PHTTPRequest    : Client to Proxy HTTP Request buffer
    # P2CHTTPResponse   : Proxy to Client HTTP Response buffer

    # P2SHTTPRequest    : Proxy to Web server HTTP Request buffer
    # S2PHTTPResponse   : Web server to Proxy HTTP Response buffer


    # Client INFO

    # ClientAddr : Client IPv4 address(str)
    # ClientPort : Client Port(int)

    ## P2SSocket : Proxy to WebServer Socket

    # DNSHost

    def __init__(self, connection, address): # Constructor, Server Listen Starts...
        threading.Thread.__init__(self)

        self.CPSocket = connection     # copy conn
        self.ClientAddr = address[0]   # copy IPv4 address
        self.ClientPort = address[1]   # copy client port

        self.HostName = ""
        self.PSSocket = 0

        self.start() ## start main PROXYSESSION thread.
        return


    def run(self):  ## Main of PROXYSESSION. begin with start() (threading module)
        print "\n   ******* [ NEW PROXYSESSION INFO ] *******"

        # Save ThreadObject INFO

        print "Active Thread Count : ", threading.activeCount()

        # starts C2SRoutine
        self.C2SThread = threading.Thread(target=self.C2SRoutine, args=())
        self.C2SThread.daemon = True
        self.C2SThread.start()

        return
    def CloseProxySocket(self):

        self.CPSocket.close()

        if self.PSSocket != 0:
            self.PSSocket.close()
        return
    def GetDNSInfo(self, host, port, index):   #return tuple
        return socket.getaddrinfo(host, port)[index][4]
    # Get host name from HTTP request (Host : "url")
    def GetHostNameFromRequest(self, request):

        strhostindex = request.find("Host:")

        if strhostindex != -1:

            i = strhostindex + 6

            while True:
                if request[i] == '\x0d':
                    break

                i = i + 1

            return request[strhostindex + 6:i]

        else: # Cannot find string "Host : "
            return ""

    # Set Destination Server with hostname
    def SetDstServerByHostName(self, host):
        # TODO : GetDNSInfo : if port is NOT 80..??
        self.ServerIPAddr, self.ServerPort = self.GetDNSInfo(host, 80, 0)  # GetDstServer addr and ServerPort
        return 0

    def S2CRoutine(self):
        print "[*] Web Server to Client Thread Name :", threading.currentThread()

        time.sleep(0.5)
        try:    # Socket is Alive
            while True:

                self.S2PHTTPResponse = self.PSSocket.recv(4096)

                if self.S2PHTTPResponse == "":
                    print "[*] Connection closed by Web Server :", self.HostName
                    raise Exception

                else:
                    print "\n           [HTTP RESPONSE]"
                    print self.S2PHTTPResponse
                    self.P2CHTTPResponse = self.S2PHTTPResponse
                    self.CPSocket.send(self.P2CHTTPResponse)

        except Exception:
            print "[*] Closing PROXYSESSION by", self.S2CThread.name
            self.ClosePROXYSESSION()
            sys.exit()

    def C2SRoutine(self):      # Server to Client Routine
        print "[*] Client to Web Server Thread Name", threading.currentThread()

        try:    # Socket is Alive
            while True:
                self.C2PHTTPRequest = self.CPSocket.recv(4096)

                if self.C2PHTTPRequest == "":       # Connection closed by Client
                    print "[*] Connection closed by client :", self.HostName
                    # TODO : How to raise exception...????
                    raise Exception

                # something received...
                print "\n         [ HTTP REQUEST ]"
                print self.C2PHTTPRequest
                temphostname = self.GetHostNameFromRequest(self.C2PHTTPRequest)

                # HostName is changed...
                if self.HostName != temphostname and temphostname != "":
                    print "[*] Host Name Changed..."
                    self.HostName = temphostname
                    print "[*] New Host Name :", self.HostName
                    print "[*] Setting new destination server..."

                    self.SetDstServerByHostName(self.HostName)

                    print "[*] Opening Proxy to Web Server socket..."

                    if self.PSSocket != 0:  # made first time
                        self.PSSocket.close()
                    else:
                        pass # TODO : Terminate existing S2CThread...

                    self.PSSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.PSSocket.connect((self.ServerIPAddr, self.ServerPort))
                    print "[*] Conneted to Web Server :", self.HostName

                    print "[*] Creating Web Server to Client thread..."

                    self.S2CThread = threading.Thread(target=self.S2CRoutine, args=())
                    self.S2CThread.daemon = True    # To exit this thread when Main-Thread is dead
                    self.S2CThread.start()

                # if hostname is not changed...

                self.P2SHTTPRequest = self.C2PHTTPRequest
                self.PSSocket.send(self.P2SHTTPRequest)

        except Exception: # Exception Occured
            print "[!] Socket Connection Error :", self.C2SThread.name
            self.ClosePROXYSESSION()
            print "[!] Thread out... Remaining Threads :", threading.activeCount()
            #res = ctypes.pythonapi.PyThreadState_SetAsyncExc(self.S2CThread.ident(), ctypes.py_object(exctype))

            return

    def ClosePROXYSESSION(self):              # Class Destructor.
        print "[!] Closing PROXYSESSION :", self.HostName
        self.CloseProxySocket()     # close sockets...
        try:
            prxylist.remove(self)       # remove current class from prxylist
        except:
            pass

        self.__del__()

    def __del__(self):
        return

##################### MAIN ######################

host = "127.0.0.1"
port = 8080

prxylist = []

print "\n             [ PROXY Program ]\n"
print "*** Press Ctrl-C to shut down this program. ***"

print "[ Main Thread ] : Thread Name - ", threading.currentThread().name
print "[ Main Thread ] : Openning Socket..."



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # To block [ "Address already in use" ] error when s.bind()
s.bind((host, port))

while True:
    try:
        s.listen(1)
        conn, addr = s.accept()

        print "\n[ Main Thread ] : NEWLY connected by", addr
        print "[ Main Thread ] : Localhost connection established..."
        print "[ Main Thread ] : Starting New PROXYSESSION...!"

        prxylist = prxylist + [ PROXYSESSION(conn, addr) ]


    except KeyboardInterrupt:
        print "\n[*] Closing Proxy System..."
        s.close()

        print prxylist

        for i in range(0, prxylist.__len__()):
            prxylist[0].ClosePROXYSESSION()

        print "[*] Remained thread count :", threading.activeCount()
        print "[*] Proxy Program Exit ..."
        quit()