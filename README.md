# led-sockets

This project allows visitors of a website to turn a blue LED attached to a Raspberry Pi on and off.

# Structure
* Server: python websocket server that runs on a publicly-accessible webserver
* Client: python websocket client that runs on a raspberry pi connected to the internet
* Web: simple website accessible from the internet

# Requirements
* Client
    * Raspberry Pi with `gpiozero` library installed
* Server
    * Nginx
    * Python
* Web
    * A webserver that can serve html files

# Server Setup
## Base Installation
* clone repo `git clone git@github.com:rtmatt/led-sockets.git`
* set env `cp.env.example .env` (modify as needed)
* activate virtualenv `python -m venv .venv`
* install dependencies `pip install -r requirements.txt`
## Nginx setup
Assuming you already have a domain/site set up, all you need to do is drop in the `location`
block of the `resources/nginx.conf` file within the `server` block of your nginx config and restart the server
`sudo systemctl restart nginx`
## Run it and test
From the project root, run
`source .venv/bin/activate && python src/server.py`
Then, from another session:
```
source .venv/bin/activate 
websockets wss://your-domain.com/ws/
```
You should see a message
`Connected to wss://your-domain/ws/.`
If you type a message and press enter, you should see it output on the original session

Note: if your domain isn't served over https, you'll need to use a ws:// url instead of wss://

# Client Installation
## Base Installation
* clone repo `git clone git@github.com:rtmatt/led-sockets.git`
* set env `cp.env.example .env`. Set `WEBSOCKET_HOST_URL` to the URL of your websocket server (modify as needed)
* activate virtualenv `python -m  venv venv --system-site-packages`
* install dependencies `pip install -r requirements.txt`
* run the client `python src/server.py`
## Run it and test
From the project root, run
`source .venv/bin/activate && python src/client.py`
The green and red LEDs should turn on. Once the client connects to the server, the red LED should turn off.

# Web Installation
* drop the `public/index.html` file into your web root
* You'll need to modify the websocket URL in the script tag to point to your websocket server

# Raspberry Pi Setup
* Install `gpiozero` library `sudo apt install python3-gpiozero` if it's not already installed
* Wire up a green LED to pin 17, a blue LED to pin 12, and a red LED to pin 21.  Don't forget the resistors!
