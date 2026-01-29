# TODO
- [ ] reconnect/timeout status
    - [ ] "server-side heartbeats (pings/pongs) to detect dead connections, implementing a smart client-side
      reconnect/rejoin logic with local data storage for missed messages, and potentially leveraging push notifications
      for critical alerts"
- [ ] security
- [ ] add output/display on pi showing how many people are connected to it

## Board

## Server

## Client

### ClientEventHandler
- [ ] ::_on_board_button_press if homebase message fails, reset changes to board state; audit for similar cases
- [ ] ::_handle_message_exception - introduce talkback between server/client on message errors

## UI Client

## Misc Python
- [ ] configure base/root logger
