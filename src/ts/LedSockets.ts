const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

type SocketMessage = {
  type: string;
  id: string;
}

type ChangeStatePayload = SocketMessage & {
  type: 'change_state'
  data: {
    is_on: boolean
  }
}
type ClientConnectionInitMessage = SocketMessage & {
  type: 'client_connection_init'
  data: {
    hardware_is_connected: boolean
  }
}
type HardwareConnectionMessage = SocketMessage & {
  type: 'hardware_connected'
  data: {
    is_connected: boolean
  }
}

export default class LedSockets {
  private button: HTMLButtonElement;

  private checkbox: HTMLInputElement;

  private messageContainer: HTMLElement;

  private state: {
    socket: string;
    status: boolean;
    hardware: boolean
  } = {
    socket: 'disconnected',
    status: false,
    hardware: false,
  };

  private statusContainer: HTMLElement;

  private hardwareStatusContainer: HTMLElement;

  private websocket: WebSocket;

  constructor() {
    this.websocket = new WebSocket(PROD ? VITE_PRODUCTION_WEB_SOCKET_URL : VITE_WEB_SOCKET_URL);
    this.button = document.getElementById('button') as HTMLButtonElement;
    this.checkbox = document.getElementById('checkbox') as HTMLInputElement;
    this.messageContainer = document.getElementById('message-container') as HTMLElement;
    this.statusContainer = document.getElementById('status') as HTMLElement;
    this.hardwareStatusContainer = document.getElementById('hStatus') as HTMLElement;
    this._addSocketListeners();
    this._addUiListeners();
  }

  private _addSocketListeners() {
    this.websocket.addEventListener('close', this.onSocketClose.bind(this));
    this.websocket.addEventListener('error', this.onSocketError.bind(this));
    this.websocket.addEventListener('message', this.onSocketMessage.bind(this));
    this.websocket.addEventListener('open', this.onSocketOpen.bind(this));
  }

  private _addUiListeners() {
    this.button.addEventListener('click', () => {
      let is_on = !this.state.status;
      const payload: ChangeStatePayload = {
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
    if (message && typeof message === 'object' && 'type' in message && message.type) {
      let messageC = message as SocketMessage;
      if (messageC.type === 'change_state') {
        const payload = message as ChangeStatePayload;
        if (payload.data.is_on) {
          this.updateState(true);
        } else {
          this.updateState(false, this.state.status ? 'I turned it off' : '');
        }
      }
      if (messageC.type === 'hardware_connection') {
        const payload = message as HardwareConnectionMessage;
        this.updateHardwareStatus(payload.data.is_connected);
      }
      if (messageC.type === 'client_connection_init') {
        const payload = message as ClientConnectionInitMessage;
        this.updateHardwareStatus(payload.data.hardware_is_connected);
      }
    }
  }

  private onSocketOpen() {
    console.log('Service: socket open event');
    this.updateSocketStatus('open');
    this.websocket.send(
      JSON.stringify({
        id: '',
        type: 'init',
        data: {
          entity_type: 'client',
        },
      }),
    );
  }

  private updateSocketStatus(status: string) {
    this.state.socket = status;
    this.statusContainer.innerText = status;
  }

  private updateHardwareStatus(connected: boolean) {
    this.state.hardware = connected;
    this.hardwareStatusContainer.innerText = connected ? 'Connected' : 'Disconnected';
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
