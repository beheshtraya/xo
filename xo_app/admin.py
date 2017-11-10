from django.contrib import admin

from xo_app.models import MoveLog
from .models import Game


admin.site.register(Game)
admin.site.register(MoveLog)
