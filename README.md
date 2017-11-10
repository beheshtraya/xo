
> Channel module is used for implementing web sockets.
> Game moves are stored in MoveLog table in database and after finishing game can be replayed by 1 second interval

> Server side implementation is based on multichat example written by module author
    https://github.com/andrewgodwin/channels-examples/tree/master/multichat

> XO client side implementation is based on a code writen by Ray Toal
    https://jsfiddle.net/rtoal/5wKfF/

> Preventing user from cheating:
        - server-side: don't save move and stop sending message on websocket
        - client-side: add an overlay div which lock page elements

--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------

How to run:

    1- Install and run redis
        - This project uses Redis as message queue. Download page: http://redis.io/download
        - Redis server IP:PORT can be set in settings.py. The deafult values will be used if no value provided.
        - After running redis server this command should be executed successfully
            - (input)$: redis-cli PING
            - (output)  PONG


    2- Create virtual environment (optional)
        - It is highly recommneded using virtual environment for installing requirements and dependencies
          because there are lots of them.

        - Create new virtualenv
            - (input)$: virtualenv <optional env name>
        - Activate virtualenv
            --Windows:
                - (input)> <optional env name>/bin/activate.bat
            --Linux or Mac:
                - (input)$: source <optional env name>/bin/activate


    3- Install required modules
        - $: pip install -r requirements.txt


    4- Sync db
        - $: python manage.py makemigrations
        - $: python manage.py migrate


    5- Run development server
        - $: python manage.py runserver
        - Site can be viewed at http://127.0.0.1:8000


--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------


Additional Info:

	tested on:
		- OS: Windows 10
		- Interpreter: Python 3.5.2
		- Web framework: Django 1.10
		- Database: sqlite

--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------

Future works:

	- Add multiple game and championship
	- Handle possible exceptions
	- Add advanced UI