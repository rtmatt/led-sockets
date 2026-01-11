const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

type ChangeStatePayload = {
  type: 'change_state'
  id: string
  data: {
    is_on: boolean
  },
  blue: 'on' | 'off'
}

const temp: ChangeStatePayload = {
  type: 'change_state',
  id: '',
  data: {
    is_on: false,
  },
  blue: 'off',
};

console.log(JSON.stringify(temp));

export default class LedSockets {
  private button: HTMLButtonElement;

  private checkbox: HTMLInputElement;

  private messageContainer: HTMLElement;

  private state: { socket: string; status: boolean } = {
    socket: 'disconnected',
    status: false,
  };

  private statusContainer: HTMLElement;

  private websocket: WebSocket;

  constructor() {
    this.websocket = new WebSocket(PROD ? VITE_PRODUCTION_WEB_SOCKET_URL : VITE_WEB_SOCKET_URL);
    this.button = document.getElementById('button') as HTMLButtonElement;
    this.checkbox = document.getElementById('checkbox') as HTMLInputElement;
    this.messageContainer = document.getElementById('message-container') as HTMLElement;
    this.statusContainer = document.getElementById('status') as HTMLElement;
    this._addSocketListeners();
    this._addUiListeners();
  }

  private _addSocketListeners() {
    this.websocket.addEventListener('closed', this.onSocketClose.bind(this));
    this.websocket.addEventListener('error', this.onSocketError.bind(this));
    this.websocket.addEventListener('message', this.onSocketMessage.bind(this));
    this.websocket.addEventListener('open', this.onSocketOpen.bind(this));
  }

  private _addUiListeners() {
    this.button.addEventListener('click', () => {
      let is_on = !this.state.status;
      const payload: ChangeStatePayload = {
        blue: is_on ? 'on' : 'off',
        data: { is_on: is_on },
        id: '',
        type: 'change_state',
      };
      this.websocket.send(JSON.stringify(payload));
      this.updateState(is_on);
    });
  }

  private onSocketClose() {
    console.log('Service: socket close event');
    this.updateSocketStatus('closed');
  }

  private onSocketError() {
    console.log('Service: socket error event');
    this.updateSocketStatus('error');
  }

  private onSocketMessage(event: MessageEvent) {
    const { data } = event;
    console.log(`Service: Message received:${data}`);
    const message: unknown = JSON.parse(data);
    // @todo: more elegant type verification
    if (message && typeof message === 'object' && 'type' in message && message.type && message.type === 'change_state') {
      const payload = message as ChangeStatePayload;
      if (payload.data.is_on) {
        this.updateState(true);
      } else {
        this.updateState(false, this.state.status ? 'I turned it off' : '');
      }
    }
  }

  private onSocketOpen() {
    console.log('Service: socket open event');
    this.updateSocketStatus('open');
  }

  private updateSocketStatus(status: string) {
    this.state.socket = status;
    this.statusContainer.innerText = status;
  }

  private updateState(
    val: boolean,
    message?: string,
  ) {
    this.state.status = val;
    this.checkbox.checked = val;
    if (val) {
      this.messageContainer.innerText = message || 'The light and buzzer are on.  If I\'m around it\'s annoying me.';
    } else {
      this.messageContainer.innerText = message || '';
    }
  }
}
