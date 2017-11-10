from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Game, MoveLog


@login_required
def index(request):

    # Get a list of games
    games = Game.objects.all()
    output_game = None

    for game in games:
        if MoveLog.objects.filter(game=game).count() < 2:
            output_game = game

    if not output_game:
        output_game = Game.objects.create(title='start game')

    # Render that in the index template
    return render(request, "index.html", {
        'game': output_game,
        'username': request.user.username
    })
