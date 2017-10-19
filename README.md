About
================================

Hale is a botnet command & control monitor/spy with a modular design to easily develop new modules that monitor new protocols used by C&C servers. Hale comes with IRC and HTTP monitors developed with Twisted to handle scalability of a large amount of connections. Theses modules have configurable protocol grammar and bot settings but can also be modified to fit your needs. All captured logs and files are saved to a database and in case of IRC, tracked IP numbers too. 

To hide the location of the operator, connections can be made through SOCKSv5 proxies and this is configurable via the web interface where also all the logs are available to browse together with statistical charts and timelines. The interface was developed with Django and Google Visualization API. Some extras in the web ui are support for a RESTful API with OAuth support and a search engine.

The main idea with Hale is to help botnet hunting and research to collaborate by creating a network of sensors (Hale monitors). To improve this idea, a XMPP bot is available to connect to a centralized XMPP server where currently two different grouprooms are used for coordinating between sensors and a room for sharing logs and files. The coordination room makes use of botnet hashes that are made out of the unique keys in the botnet settings, in this way, two botnets dont have to be monitored simultaneously that have the same hash (identity) and improves utilization. To help 3rd parties to make use of this network, a bot can join the coordination room and ask a sensor to start tracking a botnet if its untracked by sending the configurations for it. Additionally, in the share room, 3rd party bots can get their hands on logs and files captured by the sensors in realtime. To assist with log history the web API can be used that support GET requests.  

Install
================================

Hale has the following dependencies:

	Python == 2.6
	Django == 1.2.1
	Twisted == 10.1.0
	GeoIP-Python == 1.2.4 (and GeoIP C lib)
	Whoosh == 0.3.18
	django-haystack == 1.0.1-final
	django-piston == 0.2.3rc1
	pefile == 1.2.10-63
	sleekxmpp == 0.9Rrc1
	wsgiref == 0.1.2
	zope.interface == 3.6.1
	oauth2 == 1.2.0
	httplib2 == 0.6.0

Additionally the monitor requires a database backend driver corresponding to the database used by django. When these libraries are installed download the source from here and extract it anywhere.

Setup
================================

1) First create a database that will be used by Hale, the database engine can be any of your choice. If you are using an existing database then skip this step.

2) Next step is to install python database backend drivers corresponding to the one used by the server engine.

3) Edit **`settings.py`** in **`hale/src/webdb/`** and edit the following configurations: ENGINE, NAME, USER, PASSWORD, HOST and PORT where the engine setting is for example **`django.db.backends.mysql`** if your server engine is MySQL. The name setting is the name of your database used when creating it.

4) If you dont want to start your own web ui then skip this step and go to 8). In **`settings.py`**, change PATH_TO_APP to point to the fullpath of the Django application, for example: **`'/home/..../Hale/src/webdb'`**. In the webdb directory run the following command: **`python manage.py syncdb`**. If you get any errors here its most likely that the database settings in **`settings.py`** are incorrect. Also, during the sync set the superuser that will be used when administrating the users.

5) To support searching in the web interface, run **`python manage.py rebuild_index`** to let the search engine index first time. This will create a directory named **`whoosh.index/`**, to let the web server write here, issue a **`chmod o+w whoosh.index/`**. After this you run **`python manage.py update_index`** instead and should put this as a cron job to update indexes in a regular interval of your choice. 

6) Run **`python manage.py runserver`** and head to http://127.0.0.1:8000 to check if setup was correctly done.

7) The runserver command deploys a development server that is not recommended for production use due to performance issues. Instead deploy the web ui by installing the **`mod_wsgi`** for Apache, assuming you're running Ubuntu, run **`apt-get install libapache2-mod-wsgi`**. In **`/etc/apache2/sites-available/default`** add the following:

    Alias /media /usr/local/lib/python2.6/dist-packages/django/contrib/admin/media/
    <Location /media>
      Order allow,deny
      Allow from all
    </Location>


    WSGIDaemonProcess username processes=2 maximum-requests=500 threads=10
    WSGIProcessGroup group

    WSGIScriptAlias / /home/..../webdb/django.wsgi

and edit the username and group for which the WSGI daemon should run as. **`WSGIScriptAlias`** should be set to the fullpath to the django.wsgi file located in the **`webdb`** directory. The Alias specified above is needed for the administration page to be rendered correctly. To be able to upload modules through the web interface, issue a **`chmod o+w webdb/modules`**.


8) Upload modules that will be used from **`hale/src/modules/`** or write your own (see Development section). Upload the desired module in the admin interface and edit for example the module name to **`irc`** and the filename to **`ircModule.py`**. Specifyc config rules for the module in the corresponding section located in **`hale/conf/modules.conf`** and put it in the textbox, also add the **`uniqueKeys`** sections for the module being uploaded.

9) Before running the monitor edit **`hale.conf`** in **`hale/src/conf/`** if you wish to use a XMPP server. To activate XMPP bot set use setting to True and either edit login info to an existing account and server or start your own XMPP server. An important step when starting up a XMPP server is to increase the max stanza size from the default value to something like 10Mb. Otherwise malware advertisement will not be possible. The channel settings in **`hale.conf`** are used for the share grouproom used by the bot and the coord setting is used for the grouproom where all coordination between sensors is taking place.

10) Edit **`hale.conf`** and set client and server settings.

Usage
================================

To start the monitor head to **`hale/src/`** and execute **`python server.py`**. If it fires up with errors then the django **`settings.py`** file is not correctly set or some libraries are missing. With the client it's possible to issue commands to the server but it requires the user to authenticate himself against the server, access is granted for users that are set as staff members through the web interface. When the client is running type **`help`** or **`?`** to get the available commands. Type help command to get more info about the specific command. Starting up a monitor bot is done by first editing the **`hale/src/conf/modules.conf`** file, for example using a irc configuration as follow:

	[uniqueKeys]
	irc = botnet, *grammar

	[ircConf] 
	module = irc 
	botnet = irc.freenode.net 
	port = 6667 
	password = None 
	nick = nickname
	username = agent007 
	realname = Spying 
	channel = #channelname 
	channel_pass = somepass 
	pass_grammar = PASS 
	nick_grammar = NICK 
	user_grammar = USER 
	join_grammar = JOIN 
	version_grammar = VERSION 
	time_grammar = TIME 
	privmsg_grammar = PRIVMSG 
	topic_grammar = TOPIC 
	currenttopic_grammar = 332 
	ping_grammar = PING 
	pong_grammar = PONG

Edit or create a new config by specifying a new uniquely named section (**`[ircConf]`** part). At the top of the config file there is a section called **`uniqueKeys`** where all unique fields for a module are specified and used to generate the botnet hash, this should usually not be changed to preserve correct botnet tracking. When this is done run **`useconf section`** to load the configuration and then fire up the bot with **`exec modulename id`** where id is set by you to identify the botnet.

The web interface provides access to all captured data in the database which is accessible from the index page. There is also a search function which enables the user to search for botnet and file hashes, related IP numbers, botnet IDs, botnet modules used and botnet hosts. If the user got access to edit proxies or modules then this can be done in the admin section, url to this is **`http://.../admin`**. The administrator can set user modes and also add consumers for the web API.

Development
================================

HOWTO add modules
------------------

1) Implement module, for example:

	import moduleManager
	from utils import moduleInterface
	
	@moduleManager.register("irc")
	def module_setup(config, hash):
	    """
	    Function to register modules, simply
	    implement this to pass along the config
	    and hash to the module object and return 
	    the it back.
	    """
	    
	    return IRC(config, hash)
	
	# must inherit from Module class
	class IRC(moduleInterface.Module):
	
	   def __init__(self, config, hash):
	       self.config = config
	       self.hash = hash
	   
	   # must be implemented
	   def stop(self):
	       # stop execution
	   
	   # must be implemented
	   def run(self):
	       # start execution
	   
	   # must be implemented    
	   def getConfig(self):
	       return self.config

Add decorator for the register function (in this case module_setup) which will be called with the current configuration as argument and the config hash made of the unique keys. This function can be named anything. Pass along the configurations to the module object, the configHandler catches KeyErrors so if wrong configurations are sent to this function configHandler will notify you about it. 

Also follow the naming convention **`nameModule.py`** and **`@moduleManager.register("name")`** and import the **`moduleManager`**, if not the moduleManager will notify you about any errors.

The rest of the module code is omitted but should create a twisted factory object and start this with the reactor in the run method, see the existing modules for an example. For tutorials on programming with Twisted, please see [here](http://twistedmatrix.com/trac/wiki/Documentation). There are also some utils to make use of when developing modules, this is done as following:
	
Socksify:

	# import all utils
	from utils import *
	
	# in the constructor create a new proxy object
	self.prox = proxySelector.ProxySelector()
	
	# in the run method add the following after having created the factory method.
	proxyInfo = self.prox.getRandomProxy()
	    if proxyInfo == None:
	        self.connector = reactor.connectTCP(host, port, factory)
	    else:
	        proxyHost = proxyInfo['HOST']
	        proxyPort = proxyInfo['PORT']
	        proxyUser = proxyInfo['USER']
	        proxyPass = proxyInfo['PASS']
	        socksify = socks5.ProxyClientCreator(reactor, factory)
	        if len(proxyUser) == 0:
	            self.connector = socksify.connectSocks5Proxy(host, port, proxyHost, proxyPort, "HALE")
	        else:
	            self.connector = socksify.connectSocks5Proxy(host, port, proxyHost, proxyPort, "HALE", proxyUser, proxyPass)

Connection errors handling in the factory object:

	def clientConnectionFailed(self, connector, reason):
	    """
	    Called on failed connection to server
	    """

	    moduleCoordinator.ModuleCoordinator().putError("Error connecting to " + self.config['botnet'], self.module)

	def clientConnectionLost(self, connector, reason):
	    """
	    Called on lost connection to server
	    """

	    moduleCoordinator.ModuleCoordinator().putError("Connection lost to " + self.config['botnet'], self.module)

This will send the errors to the error bucket which is accessible by issuing a **`showlog`** in the CLI.
            
            
Logging:

	# in the factory create the following method to handle logs (note that the hash and config must be sent to the factory)
	# and call it in the protocol class with: self.factory.putLog(data)
	def putLog(self, log):
	    """
	    Put log to the event handler
	    """
	        
	    moduleCoordinator.ModuleCoordinator().addEvent(moduleCoordinator.LOG_EVENT, log, self.hash, self.config)
    
	# apply reg expression to look for URLs containing possible malware
	# and call it in the protocol class with: self.factory.checkForURL(data)
	def checkForURL(self, data):
	    """
	    Check for URL in the event handler
	    """
	    
	    moduleCoordinator.ModuleCoordinator().addEvent(moduleCoordinator.URL_EVENT, data, self.hash)
    
	# if you module should detect IP numbers of other bots and herders implement the following method in the factory
	def addRelIP(self, data):
	    """
	    Put possible ip related to the botnet being monitored
	    in the event handler.
	    """
	        
	    moduleCoordinator.ModuleCoordinator().addEvent(moduleCoordinator.RELIP_EVENT, data, self.hash)
    
handling related IPs is done by applying a regular expression to be used for the protocol that the module is going to support, in case of irc module, the code looks like this:

	checkHost = data.split(':')[1].split(' ')[0].strip()
	match = self.factory.expr.findall(checkHost)
	if match:
	    self.factory.addRelIP(data.split('@')[1].split(' ')[0].strip())
    
where the regular expression is as follow:

	self.expr = re.compile('!~.*?@')



2) Drag the file to the modules directory. The moduleManager will then automatically import it and check for errors.

3) In modules.conf edit the configuration

4) Upload the module to the web ui by setting the module name to for example irc, filename ircModule.py and then add a config example for this module.

XMPP bot HOWTO
-----------------

When sending a request for a botnet to track the request is made as follow
to the groupchat coordination room 

	sensorLoadReq

where all sensors reply with their id and queue length (number of monitored botnets)

	sensorLoadAck id=353f6650859547ed06597dbfa1dcfd88 queue=0

The feeder then choose one sensor based on this info like lowest queue length
and if these are equal for several sensors, then the sensor id sorted alphabetically
with lowest value is chosen.

When the feeder has chosen a sensor it sends a private chat message to the sensor

	startTrackReq config

where config is a string representation of the configuration, for example

	module=irc botnet=irc.freenode.net etc..

The sensor then replies with with an acknowledgement together with the config hash
which can be used to distinguish the botnet logs from the other logs in the share channel.
Example of acknowledgment:

	startTrackAck hash

if no one else is monitoring this botnet, otherwise a startTrackNack is received if the 
botnet is already monitored or the sensor does not have the module installed for this botnet.
Malware share is done by sensors sending a message like:

	fileCaptured hash=353f6650... file content

where the content is Base64 encoded and comes directly after the file hash value.

RESTful Web API
----------------

To get access to the api you need a consumer key and secret key, this can be created by the admin and are used with OAuth to authenticate. The following URLs are available to fetch data in JSON format:

    http://.../api/botnet will reply with all botnets monitored
    http://.../api/botnet/botnethash will reply with the botnet with hash equal to botnethash
    http://.../api/host/hostname will reply with all botnets monitored with host equal to hostname
    http://.../api/type/module will reply with all botnets monitored with the module
    http://.../api/botips/hash will reply with all ips captured by botnet with the value hash
    http://.../api/bologs/hash will reply with all logs for botnet with value hash
    http://.../api/bofiles/hash will reply with file hashes captured by botnet with value hash
    http://.../api/file/hash returns botnet(s) info for those that have captured file with the hash specified
    http://.../api/ip/addr will reply with botnet(s) info for those that have detected an IP with number addr
    
Note that currently only GET requests are possible.
