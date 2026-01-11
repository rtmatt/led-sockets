const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

const WEB_SOCKET_URL = PROD ? VITE_PRODUCTION_WEB_SOCKET_URL : VITE_WEB_SOCKET_URL;

let state: boolean = false;

function updateState(
  val: boolean,
  checkbox: HTMLInputElement,
  messageContainer: HTMLElement,
  message?: string,
) {
  state = val;
  checkbox.checked = state;
  if (state) {
    messageContainer.innerText = message || 'The light and buzzer are on.  If I\'m around it\'s annoying me.';
  } else {
    messageContainer.innerText = message || '';
  }
}

function handleButton(
  button: HTMLButtonElement,
  websocket: WebSocket,
  checkbox: HTMLInputElement,
  messageContainer: HTMLElement,
) {
  button.addEventListener('click', () => {
    const data = JSON.stringify({
      blue: state ? 'off' : 'on',
    });
    websocket.send(data);
    updateState(
      !state,
      checkbox,
      messageContainer,
    );
  });
}

function handleSocketMessages(
  websocket: WebSocket,
  checkbox: HTMLInputElement,
  messageContainer: HTMLElement,
) {
  websocket.addEventListener('message', ({ data }) => {
    const message = JSON.parse(data);
    console.log(`Message received:${data}`);
    if (message && 'blue' in message) {
      if (message.blue === 'on') {
        updateState(
          true,
          checkbox,
          messageContainer,
        );
      } else if (message.blue === 'off') {
        updateState(
          false,
          checkbox,
          messageContainer,
          state ? 'I turned it off' : '');
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const websocket = new WebSocket(WEB_SOCKET_URL);
  const button: HTMLButtonElement = document.getElementById('button') as HTMLButtonElement;
  const checkbox: HTMLInputElement = document.getElementById('checkbox') as HTMLInputElement;
  const messageContainer: HTMLElement = document.getElementById('message-container') as HTMLElement;
  handleButton(button, websocket, checkbox, messageContainer);
  handleSocketMessages(websocket, checkbox, messageContainer);
});
