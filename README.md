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
Assuming you already have a domain/site set up, all you need to do is drop in the `location` block of the
`resources/nginx.conf` file within the `server` block of your nginx config:
```
location /ws/ { # this will be the url of your websocket server
    proxy_pass http://localhost:8765; # Your internal WebSocket server.  Make sure the ports line up
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $host;
}
```
and restart the server
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

## Supervisor
At this point, the script will stop running once the ssh session closes. By adding supervisor, the script can be run on
boot and restart if it crashes.
* check if supervisor is installed `which supervisorctl`
* install supervisor if it's not installed already `sudo apt install supervisor`
* create a config file
  `sudo cp resources/supervisor/led-sockets-server.conf.example /etc/supervisor/conf.d/led-sockets-server.conf`
    * edit the file `/etc/supervisor/conf.d/led-sockets-server.conf` to set the `directory` and `stdout_logfile` values
      using the proper absolute paths
* run supervisor
    * `sudo supervisorctl`
    * `reread`
    * `start processname` where `processname` is the name of the process output from status call
        * if you ever need to restart or stop the process, use `restart processname` or `stop processname`. You'll need
          to restart the process following any updates to `server.py`
    * `status` to check the status of the process
    * `exit`

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
## Supervisor
At this point, the script will stop running once the ssh session closes. By adding supervisor, the script can be run on
boot and restart if it crashes. Before proceeding, make sure the server is running as described above and ideally run by
supervisor.
* check if supervisor is installed `which supervisorctl`
* install supervisor if it's not installed already `sudo apt install supervisor`
* create a config file
  `sudo cp resources/supervisor/led-sockets-client.conf.example /etc/supervisor/conf.d/led-sockets-client.conf`
    * edit the file `/etc/supervisor/conf.d/led-sockets-client.conf` to set the `directory` and `stdout_logfile` values
      using the proper absolute paths
    * Note: `autostart` is set to false by default to prevent the program from starting every time the pi reboots.
      Change this if desired.
* run supervisor
    * `sudo supervisorctl`
    * `reread`
    * `start processname:*` where `processname` is the name of the process output from status call
        * if you ever need to restart or stop the process, use `restart processname` or `stop processname`. You'll need
          to restart the process following any updates to `server.py`
    * `status` to check the status of the process
    * `exit`

# Web Installation
* drop the `public/index.html` file into your web root
* You'll need to modify the websocket URL in the script tag to point to your websocket server

# Raspberry Pi Setup
* Install `gpiozero` library `sudo apt install python3-gpiozero` if it's not already installed
* Wire up:
  * a green [LED](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_1.1.1_blinking_led_python.html) to pin 17 ...Don't forget the resistors!
  * a blue LED to pin 12
  * a red LED to pin 21
  * a [passive buzzer](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_1.2.2_passive_buzzer_python.html) to pin 26
  * a [button](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_2.1.1_button_python.html) to pin 20
