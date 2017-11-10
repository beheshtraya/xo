import json
from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from xo_app.settings import NOTIFY_USERS_ON_ENTER_OR_LEAVE_GAMES
from xo_app.utils import get_game_and_user_or_error, catch_client_error
from .settings import MSG_TYPE_LEAVE, MSG_TYPE_ENTER, MSG_TYPE_REPLAY
from xo_app.models import Game, MoveLog
from .exceptions import ClientError
from django.contrib.auth.models import User
from time import sleep
import json


### WebSocket handling ###

# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    # Initialise their session
    message.channel_session['games'] = []
    # message.channel_session['games'] = []

# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("xo_app.receive").send(payload)


@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected games
    for game_id in message.channel_session.get("games", set()):
        try:
            game = Game.objects.get(pk=game_id)
            # Removes us from the game's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            game.websocket_group.discard(message.reply_channel)
        except Game.DoesNotExist:
            pass


### XO channel handling ###


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
@catch_client_error
def xo_join(message):
    # Find the game they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    game, user = get_game_and_user_or_error(message["game"], message.user)

    # Send a "enter message" to the game if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_GAMES:
        game.send_message(None, message.user, MSG_TYPE_ENTER)

    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the xo_app game gets them.
    game.websocket_group.add(message.reply_channel)
    message.channel_session['games'] = list(set(message.channel_session['games']).union([game.id]))
    # Send a message back that will prompt them to open the game
    # Done server-side so that we could, for example, make people
    # join games automatically.
    message.reply_channel.send({
        "text": json.dumps({
            "join": str(game.id),
            "title": game.title,
        }),
    })


@channel_session_user
@catch_client_error
def xo_leave(message):
    # Reverse of join - remove them from everything.
    game, user = get_game_and_user_or_error(message["game"], message.user)

    # Send a "leave message" to the game if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_GAMES:
        game.send_message(None, message.user, MSG_TYPE_LEAVE)

    game.websocket_group.discard(message.reply_channel)
    message.channel_session['games'] = list(set(message.channel_session['games']).difference([game.id]))
    # Send a message back that will prompt them to close the game
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(game.id),
        }),
    })


@channel_session_user
@catch_client_error
def xo_send(message):
    # Check that the user in the game

    if int(message['game']) not in message.channel_session['games']:
        raise ClientError("Game_ACCESS_DENIED")

    # Find the game they're sending to, check perms
    game, user = get_game_and_user_or_error(message["game"], message.user)
    # Send the message along

    if 'winner' in message['message']:
        game.winner = User.objects.get(username=message['message']['winner'])
        game.save()
    else:
        moves = MoveLog.objects.filter(game=game)
        order = moves.count()
        user = User.objects.get(id=user.id)

        # prevent user from cheating
        if moves:
            if moves.filter(order=order-1)[0].user == user:
                return

        MoveLog.objects.create(
            game=game,
            user=user,
            order=order,
            indicator=message['message']['indicator'],
            node_value=message['message']['nodeValue']
        )

    game.send_message(message["message"], message.user)


@channel_session_user
@catch_client_error
def xo_replay(message):
    # Check that the user in the game

    if int(message['game']) not in message.channel_session['games']:
        raise ClientError("Game_ACCESS_DENIED")

    # Find the game they're sending to, check perms
    game, user = get_game_and_user_or_error(message["game"], message.user)
    # Send the message along

    moves = MoveLog.objects.filter(game=game).order_by('order')

    for move in moves:
        output_msg = dict()
        output_msg['indicator'] = move.indicator
        output_msg['nodeValue'] = move.node_value

        game.send_message(json.loads(json.dumps(output_msg)), message.user, msg_type=MSG_TYPE_REPLAY)
        sleep(1)
