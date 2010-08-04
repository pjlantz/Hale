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

import os, mimetypes, base64, datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from webdb.hale.models import Botnet, Log, Module, File, RelatedIPs
from django.template import Context, loader
from django.contrib.auth import logout

@login_required
def index(request):
    botnets = Botnet.objects.all()
    logs = Log.objects.all()
    ips = RelatedIPs.objects.all()
    files = File.objects.all()
    t = loader.get_template('index.html')
    c = Context({'botnets': botnets, 'logs': logs, 'ips': ips, 'files':files,})
    return HttpResponse(t.render(c))

def logoff(request):
    logout(request)
    t = loader.get_template('logout.html')
    c = Context({})
    return HttpResponse(t.render(c))
    
@login_required
def download(request, filename):
    filePath = os.getcwd() + "/modules/" + filename
    if os.name == "nt":
        filePath = filePath.replace("/", "\\")
    file = open(filePath)
    ctype, encoding = mimetypes.guess_type(filePath)
    response = HttpResponse(file, mimetype=ctype)
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

@login_required
def file(request, hashvalue):
    file = File.objects.get(hash=hashvalue)
    content = file.content
    content = base64.b64decode(content)
    ctype, encoding = mimetypes.guess_type(file.filename)
    response = HttpResponse(content, mimetype=ctype)
    response['Content-Disposition'] = 'attachment; filename='+file.filename
    return response

@login_required
def log(request, log_id):
    botnet = Botnet.objects.get(id=log_id)
    logs = Log.objects.filter(botnet=botnet.id)
    diff = botnet.lastseen - botnet.firstseen
    uptime = diff.days
    diff = datetime.datetime.now() - botnet.lastseen
    lastActivity = diff.days
    files = File.objects.filter(botnet=log_id)
    ips = RelatedIPs.objects.filter(botnet=log_id)
    t = loader.get_template('logs.html')
    c = Context({'logs': logs, 'botnet': botnet, 'files':files, 'ips':ips, 'uptime':uptime, 'lastActivity': lastActivity,})
    return HttpResponse(t.render(c))
    
@login_required
def modules(request):
    modules = Module.objects.all()
    botnets = Botnet.objects.all()
    t = loader.get_template('modules.html')
    c = Context({'modules':modules, 'botnets':botnets,})
    return HttpResponse(t.render(c))

    