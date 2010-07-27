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

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from webdb.hale.models import Botnet, Log, Module
from django.template import Context, loader

@login_required
def index(request):
    botnets = Botnet.objects.all()
    t = loader.get_template('index.html')
    c = Context({'botnets': botnets,})
    return HttpResponse(t.render(c))
    
@login_required
def botnets(request):
    botnets = Botnet.objects.all()
    t = loader.get_template('botnets.html')
    c = Context({'botnets': botnets,})
    return HttpResponse(t.render(c))

@login_required
def log(request, log_id):
    logs = Log.objects.filter(botnet=log_id)
    botnet = Botnet.objects.get(id=log_id)
    t = loader.get_template('logs.html')
    c = Context({'logs': logs, 'botnet': botnet,})
    return HttpResponse(t.render(c))

@login_required
def module(request, mod_id):
    return HttpResponse(mod_id)
    
@login_required
def modules(request):
    modules = Module.objects.all()
    t = loader.get_template('modules.html')
    c = Context({'modules': modules,})
    return HttpResponse(t.render(c))

    