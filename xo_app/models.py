import json
from django.db import models
from channels import Group
from xo_app.settings import MSG_TYPE_MESSAGE
from django.contrib.auth.models import User


class Game(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    winner = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("game-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'game': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )


class MoveLog(models.Model):
    game = models.ForeignKey(Game, null=False, blank=False)
    user = models.ForeignKey(User, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    indicator = models.IntegerField(null=False, blank=False)
    NODE_VALUE_CHOICES = (
        ('X', 'X'),
        ('O', 'O')
    )
    node_value = models.CharField(max_length=1, choices=NODE_VALUE_CHOICES)

    def __str__(self):
        return self.game.title + ' ' + str(self.order) + ' ' + self.node_value
