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

# Server Installation
## Base Installation
* clone repo `git clone git@github.com:rtmatt/led-sockets.git`
* within directory (`cd led-sockets`)...
* set env `cp .env.example .env` (modify as needed). It's recommended to set the `ECHO_SERVER_HOST` to `localhost`
  in production environments
* activate virtualenv `python -m venv .venv`
    * activate it `source .venv/bin/activate`
* install dependencies `pip install -r requirements.txt`
* load editable package `pip install -e .`
## Nginx setup
Assuming you already have a domain/site set up, all you need to do is drop in the `location` block of the
`resources/nginx/led-sockets.conf` file within the `server` block of your nginx config:
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
`source .venv/bin/activate && ledsockets-server`
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
    * `add led-sockets-server`
    * `status`
      * The process should have started automatically
          * if you ever need to restart or stop the process, use `restart led-sockets-server` or `stop led-sockets-server`. You'll need
            to restart the process following any updates to files in the `src/ledsockets` directory
    * `exit`

# Client Installation
## Base Installation
* clone repo `git clone git@github.com:rtmatt/led-sockets.git`
* set env `cp .env.example .env`. Set `HARDWARE_SOCKET_URL` to the URL of your websocket server (modify as needed)
* create virtualenv `python -m  venv .venv --system-site-packages`
    * activate it `source .venv/bin/activate`
* install dependencies `pip install -r requirements.txt`
* load editable package `pip install -e .`
## Run it and test
From the project root, run
`source .venv/bin/activate && ledsockets-client`

You should see some log outputs. If a compatible server is not running at the `HARDWARE_SOCKET_URL`, you should mostly
see connection errors.
## Supervisor
At this point, the script will stop running once the ssh session closes. By adding supervisor, the script can be run on
boot and restart if it crashes. Before proceeding, make sure the server is running as described above and ideally run by
supervisor.
* check if supervisor is installed `which supervisorctl`
* install supervisor if it's not installed already `sudo apt install supervisor`
* create a config file
  `sudo cp resources/supervisor/led-sockets-client.conf.example /etc/supervisor/conf.d/led-sockets-client.conf`
    * edit the file `sudo nano /etc/supervisor/conf.d/led-sockets-client.conf` to set the `command`, `directory` and 
      `stdout_logfile` values using the appropriate absolute paths
    * Note: `autostart` is set to false by default to prevent the program from starting every time the pi reboots.
      Change this if desired.
* run supervisor
    * `sudo supervisorctl`
    * `reread`
    * `add led-sockets-client`
    * `start led-sockets-client`
        * if you ever need to restart or stop the process, use `restart led-sockets-client` or `stop led-sockets-client`. You'll need
          to restart the process following any updates to files in the `src/ledsockets` directory
    * `status` to check the status of the process
    * `exit`

# Web Installation
* clone repo `git clone git@github.com:rtmatt/led-sockets.git`
    * conversely, you can just drop the `dist` directory into your file system
* configure your webserver to use the `dist` directory as the site root and make sure it loads index.html files


# Raspberry Pi Setup
* Install `gpiozero` library `sudo apt install python3-gpiozero` if it's not already installed
* Wire up:
    * a green LED to pin 17 ...Don't forget the resistors!
        * [LED](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_1.1.1_blinking_led_python.html)
    * a blue LED to pin 12
    * a red LED to pin 21
    * a passive buzzer to pin 26
        * [passive buzzer](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_1.2.2_passive_buzzer_python.html)
    * a button to pin 20
        * [button](https://docs.sunfounder.com/projects/davinci-kit/en/latest/python_pi5/pi5_2.1.1_button_python.html)

# Contributing
## Development Setup
Development requires two environments:

### 1. Raspberry Pi (Echo Server, Hardware Client)
This machine is used to run the hardware client app (for board integration) as well as the echo server app.  
The echo server could be ran elsewhere, but running it on the same machine as the hardware client makes networking
simple.
* I'm using a Pi 5 with Raspberry Pi OS (Debian 12)
* Python 3.11.2
* Network-accessible via `raspberrypi.local` (this should be in place from default pi setup)
### 2. Primary Machine (UI Client)
This machine is used for develoment of the ui client, as well as optional development of remaining assets to be
copied/synced to Pi. If you have an IDE you like on your Pi, you could run this on the Pi as well. I don't, so I don't.
* NVM with Node 24.11.1

## 1. Raspberry Pi Setup
On your Pi, pull in the codebase to your directory of choice:
```
git clone git@github.com:rtmatt/led-sockets.git
```
Within the directory, create the python venv, activate it, and install dependencies:
```
cd led-sockets
python -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.
pip install -e .
```
The `system-site-packages` flag gives the venv access to system-wide packages. In our case, we want access to the system
gpiozero package to enable the app to modify the state of the board.

`pip install -e .` installs the source as an editable package; it will essentially add the `src` directory to the python `sys.
path` (by way of the `site` module) so module references within the source code will work (Should you ever need to 
undo this for any reason, you can run `pip uninstall led-sockets`)

Verify everything is in working order:
```
.venv/bin/python src/ledsockets/verify.py
```
You should see an info log saying it's working. If you see a `ModuleNotFoundError`, the editable installation isn't
correct.

### Running
First, run the echo server script:
```
source .venv/bin/activate
ledsockets-server
```
This needs to be run before the client.

Second, in another ssh session, run the hardware client script. Don't forget to activate the venv first:
```
source .venv/bin/activate
ledsockets-client
```

Alternatively, the preceding commands can be run via the following without activating the venv:
```
.venv/bin/ledsockets-server
.venv/bin/ledsockets-client
```

Ultimately, you can run both the server and the client at the same time if needed
```
.venv/bin/ledsockets
```

### Verify
While the client and server are runnning, in a third session in the Pi:
```
.venv/bin/websockets ws://localhost:8765
```
In the prompt, send:
```
{"id":"","type":"init_client"}
{"type":"patch_hardware_state","attributes":{"on":true}}
```
The light and buzzer on the Pi should activate. You can leave it in this state if you like. Some people enjoy the sound.
If you don't, you can turn it off:
```
{"type":"patch_hardware_state","attributes":{"on":false}}
```
### Environment Configuration
The environment can be configured by setting `.env` vars. First, copy the example file:
```
cp.env.example .env
```
You shouldn't need to change any of these values, but you can if you want.

### Development
The client and server scripts will need to be manually stopped and restarted whenever you make changes to them. Always
remember to start the server first, then the client.

## 2. Primary Machine Setup
I prefer not to use the Pi for actual development, so I set up my primary develpment for development of the UI client.
First, clone the repo:
```
git clone git@github.com:rtmatt/led-sockets.git
```
Within the project directory, create the environment file, activate the proper node version and install dependencies:
```
cp .env.example .env
nvm use
npm install
```
### Running
The client app uses [vite](https://vite.dev/)
To run the development server
```
npm run dev
```
### Contributing
Vite builds files to the `public` directory. These files should not be modified manually, and they should not be
committed to source control alongside source code changes. However, the final commit before submitting a PR should be
the resulting build files with the message `CHORE: build`

To run a production build, use the following. Make sure the `.env` `VITE_PRODUCTION_WEB_SOCKET_URL` is set to the
websocket URL used in your production environment.
```
npm run build
```
You can verify the build via:
```
npm run preview
```

## Deployment
### Web
Update dist files to latest version
```
cd <project_root>
git pull
```
Or simply ftp the latest `dist` directory
### Server
Get the latest files
```
cd <project_root>
git pull
```
Sometimes you may need to reinstall the project package.  You should only need to do this after changes to 
`pyproject.toml`
```
cd <project_root>
pip install -e .
```
If you're using supervisor, restart the queue
```
sudo supervisorctl restart led-sockets-server
```
### Client
Get the latest files
```
cd <project_root>
git pull
```
Sometimes you may need to reinstall the project package.  You should only need to do this after changes to 
`pyproject.toml`
```
cd <project_root>
pip install -e .
```
If you're using supervisor, restart the queue
```
sudo supervisorctl restart led-sockets-client
```
