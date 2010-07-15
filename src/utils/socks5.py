from twisted.internet.interfaces import ITransport
from twisted.internet.base      import BaseConnector
from twisted.internet           import reactor, tcp
from twisted.internet           import protocol, defer
from twisted.python             import log, failure
import struct, re, socket, sys

from sockserror import *

# Used to distinguish IP address from domain name
# TODO: should this be optimized somehow?
#
_ip_regex = re.compile ("\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?")


class ClientProtocol (protocol.Protocol):
    """ This protocol that talks to SOCKS5 server from client side.
    """
    __implements__ = ITransport,
    disconnecting = 0

    def __init__(self, sockshost, socksport, host, port, factory, otherProtocol,
        method="CONNECT", login=None, password=None):
        """ Initializes SOCKS session
        
        @type sockshost: string
        @param sockshost: Domain name or ip address of intermediate SOCKS 
server.

        @type socksport: int
        @param socksport: Port number of intermediate server.

        @type host: string
        @param host: Domain name or ip address where should connect or bind.

        @type port: int
        @param port: Port number where to connect or bind.

        @type otherProtocol: object
        @param otherProtocol: Initialised protocol instance, which will receive
            all I/O and events after SOCKS connected.

        @type login: string
        @param login: Sets user name if SOCKS server requires us to
            authenticate.

        @type password: string
        @param password: Sets user password if SOCKS server requires us
            to authenticate.

        @type method: string
        @param method: What to do: may be \"CONNECT\" only. Other
            methods are currently unsupported.
        """
        # login and password are limited to 256 chars
        #
        if login is not None and len (login) > 255:
            raise LoginTooLongError()

        if password is not None and len (password) > 255:
            raise PasswordTooLongError()

        # save information
        #
        self.method         = method
        self.host           = host
        self.port           = port
        self.login          = login
        self.password       = password
        self.state          = "mustNotReceiveData"
        self.otherProtocol  = otherProtocol
        self.factory        = factory
	    
    def connectionMade(self):
        # prepare connection string with available authentication methods
        #
	
        log.debug ("SOCKS5.connectionMade")
        methods = "\x00"
        if not self.login is None: methods += "\x02"

        connstring = struct.pack ("!BB", 5, len (methods))

        self.transport.write (connstring + methods)
        self.state = "gotHelloReply"

    def dataReceived (self, data):
        log.debug ("SOCKS state=" + self.state)
        method = getattr(self, 'socks_%s' % (self.state), 
            self.socks_thisMustNeverHappen)
        method (data)

    def socks_thisMustNeverHappen (self, data):
        self.transport.loseConnection()
        raise UnhandledStateError ("This SOCKS5 self.state (%s) "\
            "must never happen %s" % (self.state, self))

    def socks_mustNotReceiveData (self, data):
        """ This error might occur when server tells something into connection
        right after connection is established. Server in this case is
        certainly not SOCKS.
        """
        self.transport.loseConnection()
        self.factory.clientConnectionFailed (self, failure.Failure (
            UnexpectedDataError ("Server must not send data before client %s" % 
self)))

    def socks_gotHelloReply (self, data):
        """ Receive server greeting and send authentication or ask to
        execute requested method right now.
        """
        if data == "\x05\xFF":
            # No acceptable methods. We MUST close
            #
	    log.debug("No acceptable methods, closing connection")
            self.transport.loseConnection()
            return

        elif data == "\x05\x00":
            # Anonymous access allowed - let's issue connect
            #
            self.sendCurrentMethod()

        elif data == "\x05\x02":
            # Authentication required
            #
            self.sendAuth()

        else:
            self.transport.loseConnection()
            self.factory.clientConnectionFailed (self, failure.Failure (
                UnhandledData ("Server returned unknown reply in gotHelloReply")))

        # From now on SOCKS server considered alive - we've got reply
        #
        self.factory.status = "connected"

    def socks_gotAuthReply (self, data):
        """ Called when client received server authentication reply,
            we or close connection or issue "CONNECT" command
        """
        if data == "\x05\x00":
            self.sendCurrentMethod()

    def sendAuth (self):
        """ Prepare login/password pair and send it to the server
        """
        command = "\x05%s%s%s%s" % (chr (len (self.login)), self.login,
            chr (len (self.password)), self.password)
        self.transport.write (command)

        self.state = "gotAuthReply"

    def sendCurrentMethod (self):
        method = getattr(self, 'socks_method_%s' % (self.method), 
            self.socks_method_UNKNOWNMETHOD)
        method()

    def socks_method_UNKNOWNMETHOD (self):
        self.transport.loseConnection()
        self.factory.clientConnectionFailed (self, failure.Failure (
            UnknownMethod ("Method %s is unknown %s" % (self.method, self))))

    def socks_method_CONNECT (self):
        # Check if we have ip address or domain name
        #
	log.debug("socks_method_CONNECT host = " + self.host)

 	# The FaceTime SOCKS5 proxy treats IP addr the same way as hostname
       # if _ip_regex.match (self.host):
       #     # we have dotted quad IP address
       #     addressType = 1
       #     address = socket.inet_aton (self.host)
       # else:
       #     # we have host name
       #     address = self.host
       #     addressType = 3

	address = self.host
	addressType = 3
	addressLen = len(address)

        #Protocol version=5, Command=1 (CONNECT), Reserved=0
        #command = struct.pack ("!BBBB", 5, 1, 0, addressType)

	command = struct.pack ("!BBBBB", 5, 1, 0, addressType,addressLen)
        portstr = struct.pack ("!H", self.port)

        self.transport.write (command + address + portstr)
        self.state = "gotConnectReply"

    def socks_gotConnectReply (self, data):
        """ Called after server accepts or rejects CONNECT method.
        """
        if data[:2] == "\x05\x00":
            # No need to analyze other fields of reply, we are done
            #
            self.state = "done"
            self.factory.status = "established"

            self.otherProtocol.transport = self
            self.otherProtocol.connectionMade()
            return 

        errcode = ord (data[1])

        if errcode < len (SOCKS_errors):
            self.transport.loseConnection()
            self.factory.clientConnectionFailed (self, failure.Failure (
                ConnectError ("%s %s" % (SOCKS_errors[errcode], self))))
        else:
            self.transport.loseConnection()
            self.factory.clientConnectionFailed (self, failure.Failure (
                ConnectError ("Unknown SOCKS error after CONNECT request issued %s" % (self))))

    def socks_done (self, data):
        """ Proxy received data to other protocol.
        """
        self.otherProtocol.dataReceived (data)
    #
    # Transport relaying
    #
    def write(self, data):
        self.transport.write(data)

    def writeSequence(self, data):
        self.transport.writeSequence(data)

    def loseConnection(self):
        self.disconnecting = 1
        self.transport.loseConnection()

    def getPeer(self):
        return self.transport.getPeer()

    def getHost(self):
        return self.transport.getHost()
    
    def registerProducer(self, producer, streaming):
        self.transport.registerProducer(producer, streaming)

    def unregisterProducer(self):
        self.transport.unregisterProducer()

    def stopConsuming(self):
        self.transport.stopConsuming()

class ClientConnector (tcp.Connector):
    """Object used to connect to some host using intermediate server
    supporting SOCKS5 protocol.

    This IConnector manages one connection.
    """
    def __init__(self, sockshost, socksport, host, port, otherFactory,
        reactor=None, method="CONNECT", login=None, password=None,
        timeout=None, readableID=None):
        """ Creates IConnector to connect through SOCKS

        @type sockshost: string
        @param sockshost: SOCKS5 compliant server address.

        @type socksport: int
        @param socksport: Port to use when connecting to SOCKS.

        @type timeout: float
        @param timeout: Time to wait until client connects, then fail.

        @type readableID: string
        @param readableID: Some human readable ID for this connection.

        See ClientProtocol constructor for details on other params.
        """
        factory = ClientFactory (method=method, sockshost=sockshost,
            socksport=socksport, host=host, port=port, login=login,
            password=password, otherFactory=otherFactory, timeout=timeout,
            readableID=readableID)

        tcp.Connector.__init__ (self, host=sockshost, port=socksport,
            factory=factory, timeout=timeout, bindAddress=None,
            reactor=reactor)

class ClientFactory (protocol.ClientFactory):
    def __init__(self, sockshost, socksport, host, port, otherFactory,
        method="CONNECT", login=None, password=None, timeout=60,
        readableID=None):
        """ Factory creates SOCKS5 client protocol to connect through it.
        See ClientProtocol constructor for details on params.
        
        @type globalTimeout: int
        @param globalTimeout: Seconds before connection is completely and
            unconditionally closed as is.

        @type readableID: string
        @param readableID: Some human readable ID for this connection.
        """
        self.sockshost      = sockshost
        self.socksport      = socksport
        self.host           = host
        self.port           = port
        self.method         = method
        self.login          = login
        self.password       = password
        self.otherFactory   = otherFactory
        self.timeout        = timeout
        self.readableID     = readableID

        # This variable contains current status of SOCKS connection,
        # useful for diagnosting connection, without knowing SOCKS
        # internal states. One of: "unconnected", "connected" (SOCKS
        # server replied and is alive), "established"
        #
        self.status = "unconnected"

    def startedConnecting (self, connector):
        # Set global timeout
        #
	if self.timeout is not None:
           log.msg ("Set timeout %d sec" % self.timeout)
           delayedcall = reactor.callLater (self.timeout, self.onTimeout,
           				    connector)
           setattr (self, "delayed_timeout_call", delayedcall)

        # inherited
        #
        protocol.ClientFactory.startedConnecting (self, connector)

    def onTimeout (self, connector):
        """ Timeout occured, can't continue and should stop immediately
        and unconditionally in the whatever state I am.
        """
        connector.disconnect()
        log.msg ("%s timeout %d sec" % (self, self.timeout))
        self.clientConnectionFailed (self, failure.Failure (
            GlobalTimeoutError ("Timeout %s" % self)))

    def stopFactory(self):
        """ Do cleanups such as cancelling timeout
        """
        try:
	    if self.timeout is not None:
               self.delayed_timeout_call.cancel()
        except:
            pass

        protocol.ClientFactory.stopFactory (self)

    def buildProtocol (self, a):
        """ Connection is successful, create protocol and let it talk to peer.
        """
        proto = ClientProtocol (sockshost=self.sockshost,
            socksport=self.socksport, host=self.host, port=self.port,
            method=self.method, login=self.login, password=self.password,
            otherProtocol=self.otherFactory.buildProtocol (self.sockshost),
            factory=self)

        proto.factory = self
        return proto

    def __repr__ (self):
        return "<SOCKS %s>" % self.readableID

    def clientConnectionLost(self, connector, reason):
        # If flag indicates that connection may not be lost
        #
        rmap = {"reason": reason, "socks": self.status}

        try:
            if self.status != "established":
                # Tell about error
                #
                log.msg ("Connection LOST before SOCKS established %s" % self)
                self.otherFactory.clientConnectionFailed (connector, rmap)
            else:
                self.otherFactory.clientConnectionLost (connector, rmap)
        except:
            ei = sys.exc_info()
            if not str (ei[0]).count ("AlreadyCalled"):
                raise
    
    def clientConnectionFailed(self, connector, reason):
        # I can't know where to get deferred, let factory do this itself
        #
        rmap = {"reason": reason, "socks": self.status}

        try:
            if self.status != "established":
                log.msg ("Connection FAILED before SOCKS established %s" % self)
                self.otherFactory.clientConnectionFailed (connector, rmap)
            else:
                self.otherFactory.clientConnectionFailed (connector, rmap)
        except:
            ei = sys.exc_info()
            if not str (ei[0]).count ("AlreadyCalled"):
                raise


class ProxyClientCreator(protocol.ClientCreator):

	def connectSocks5Proxy(self,remotehost,remoteport,proxy,proxyport,id):
	   d = defer.Deferred()
	   f = protocol._InstanceFactory(self.reactor,
	                                self.protocolClass(*self.args, **self.kwargs),d)
	   self.reactor.connectWith(ClientConnector,
			            host=remotehost,port=remoteport,
				    sockshost=proxy,socksport=proxyport,
				    otherFactory=f,
				    readableID=id)
	   return d




