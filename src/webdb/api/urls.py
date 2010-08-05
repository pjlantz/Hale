################################################################################
#   (c) 2010, The Honeynet Project
#   Author: Patrik Lantz  patrik@pjlantz.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################

from django.conf.urls.defaults import *
from piston.resource import Resource
from webdb.api.handlers import *
from piston.authentication import *
import piston

auth = piston.authentication.OAuthAuthentication(realm="Hale API")

botnet_resource = Resource(BotnetHandler, authentication=auth)
botnethost_resource = Resource(BotnetHostHandler, authentication=auth)
botnettype_resource = Resource(BotnetTypeHandler, authentication=auth)
botips_resource = Resource(BotnetIPsHandler, authentication=auth)
bologs_resource = Resource(BotnetLogsHandler, authentication=auth)
bofiles_resource = Resource(BotnetFilesHandler, authentication=auth)
file_resource = Resource(FilesHandler, authentication=auth)
ip_resource = Resource(IPHandler, authentication=auth)

urlpatterns = patterns('',
   url(r'^botnet/(?P<hash>.*)$', botnet_resource),
   url(r'^host/(?P<hostname>.*)$', botnethost_resource),
   url(r'^type/(?P<module>.*)$', botnettype_resource),
   url(r'^botips/(?P<hash>.*)$', botips_resource),
   url(r'^bologs/(?P<hash>.*)$', bologs_resource),
   url(r'^bofiles/(?P<hash>.*)$', bofiles_resource),
   url(r'^file/(?P<hash>.*)$', file_resource),
   url(r'^ip/(?P<ip>.*)$', ip_resource),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$', oauth_request_token),
    url(r'^oauth/authorize/$', oauth_user_auth),
    url(r'^oauth/access_token/$', oauth_access_token),
)

