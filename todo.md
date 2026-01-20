- [x] Add status to web-ui (socket server connected, hardware connected)
- [x] Add web-UI reflection of hardware state
- [x] hide host information from UI codebase
- [ ] reconnect/timeout status
  - [ ] "server-side heartbeats (pings/pongs) to detect dead connections, implementing a smart client-side reconnect/rejoin logic with local data storage for missed messages, and potentially leveraging push notifications for critical alerts"
- [ ] security
- [ ] add output/display on pi showing how many people are connected to it
- [ ] have pi detect when connection breaks and add push button for attempt to reconnect
- [x] add noisemaker
- [x] Graceful shutdown when running under supervisor
- [ ] add server disconnect/unavailable handling in hardware-client and ui-client
  - [ ] hardware-client
  - [x] ui-client
- [x] create and document unified development environment

# Board
- [ ] consider extracting pins to env vars
- [ ] A "reset" button on the board would be neat; resets state and reconnects to server

# Server
- [ ] Pass simple messages as JSON.  Only do this if it becomes functionally prudent

# Client
- [ ] A "reset" button on the board would be neat; resets state and reconnects to server
- [ ] Following the previous, don't end process on a server connection break...sit and wait for button-based reconnect

## ClientEventHandler
- [ ] ::_on_board_button_press if homebase message fails, reset changes to board state; audit for similar cases
- [ ] ::_handle_message_exception - introduce talkback between server/client on message errors
 
# UI Client
- [ ] Add polling upon connection disconnect to restore connection or reconnect button
  - [x] Add reconnect button and functionality
  - [ ] Add interval-based auto-reconnect (try to reconnect every x seconds for x seconds, then relegate to manual button)
- [x] Disable checkbox/button when disconnected
- [x] proper type narrowing
- [ ] add ids to json:api objects across full suite

# Misc Python
- [ ] configure base/root logger
