const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

interface SocketMessage {
  attributes?: Object | null;
  type: string;
}

type HardwareStateAttributes = {
  on: boolean;
  message: string;
}

interface HardwareStateMessage extends SocketMessage {
  attributes: HardwareStateAttributes | null
  type: 'hardware_state',
}

interface HardwareConnectionMessage extends SocketMessage {
  attributes: {
    is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareStateMessage
    }
  }
  type: 'hardware_connection',
}

interface ClientConnectionInitMessage extends SocketMessage {
  attributes: {
    hardware_is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareStateMessage
    }
  }
  type: 'client_init',
}

interface PatchHardwareState extends SocketMessage {
  attributes: Partial<HardwareStateAttributes>;
  type: 'patch_hardware_state';
}

export default class LedSockets {
  private elements: {
    button: HTMLButtonElement;
    checkbox: HTMLInputElement;
    messageContainer: HTMLElement;
    socketStatusContainer: HTMLElement;
    hardwareStatusContainer: HTMLElement;
  };

  private state: {
    socket: string;
    status: boolean;
    hardware: boolean;
    message: string
    checkbox: boolean
  } = {
    socket: 'disconnected',
    status: false,
    hardware: false,
    message: '',
    checkbox: false,
  };

  private websocket: WebSocket;

  constructor() {
    this.websocket = new WebSocket(PROD ? VITE_PRODUCTION_WEB_SOCKET_URL : VITE_WEB_SOCKET_URL);
    this.elements = {
      button: document.getElementById('button') as HTMLButtonElement,
      checkbox: document.getElementById('checkbox') as HTMLInputElement,
      messageContainer: document.getElementById('message-container') as HTMLElement,
      socketStatusContainer: document.getElementById('status') as HTMLElement,
      hardwareStatusContainer: document.getElementById('hStatus') as HTMLElement,
    };
    this._addSocketListeners();
    this._addUiListeners();
  }

  get checkbox_status(): boolean {
    return this.state.checkbox;
  }

  set checkbox_status(status: boolean) {
    this.state.checkbox = status;
    this.elements.checkbox.checked = status;
  }

  get hardware_state() {
    return this.state.hardware;
  }

  set hardware_state(connected: boolean) {
    this.state.hardware = connected;
    this.elements.hardwareStatusContainer.innerText = connected ? 'Connected' : 'Disconnected';
  }

  get message(): string {
    return this.state.socket;
  }

  set message(message: string) {
    this.state.message = message;
    this.elements.messageContainer.innerText = message;
  }

  get socket_status(): string {
    return this.state.socket;
  }

  set socket_status(status: string) {
    this.state.socket = status;
    this.elements.socketStatusContainer.innerText = status;
  }

  get status(): boolean {
    return this.state.status;
  }

  set status(status: boolean) {
    this.state.status = status;
  }

  private _addSocketListeners() {
    // @todo: revise attachment of these to prevent close on page load
    this.websocket.addEventListener('close', this.onSocketClose.bind(this));
    this.websocket.addEventListener('error', this.onSocketError.bind(this));
    this.websocket.addEventListener('message', this.onSocketMessage.bind(this));
    this.websocket.addEventListener('open', this.onSocketOpen.bind(this));
  }

  private _addUiListeners() {
    this.elements.button.addEventListener('click', () => {
      const payload: PatchHardwareState = {
        type: 'patch_hardware_state',
        attributes: { on: !this.state.status },
      };
      this.websocket.send(JSON.stringify(payload));
    });
  }

  private onSocketClose(e: CloseEvent) {
    console.error('Socket Closed' + e.reason);
    this.hardware_state = false;
    this.socket_status = 'Closed';
  }

  private onSocketError(e: Event) {
    console.error('Socket Error', e);
    this.hardware_state = false;
    this.socket_status = 'Error';
  }

  private onSocketMessage(event: MessageEvent) {
    const { data } = event;
    let message: unknown;
    try {
      message = JSON.parse(data);
    } catch (error) {
      console.warn(data);
    }
    // @todo: proper narrowing
    if (message && typeof message === 'object' && 'type' in message && message.type) {
      let messageC = message as SocketMessage;
      let payload;
      switch (messageC.type) {
        case 'hardware_state':
          payload = message as HardwareStateMessage;
          this.updateState(payload.attributes);
          break;
        case 'hardware_connection':
          payload = message as HardwareConnectionMessage;
          this.updateState(payload.relationships.hardware_state.data.attributes);
          this.hardware_state = payload.attributes.is_connected;
          break;
        case 'client_init':
          payload = message as ClientConnectionInitMessage;
          this.updateState(payload.relationships.hardware_state.data.attributes);
          this.hardware_state = payload.attributes.hardware_is_connected;
          break;
      }
    }
  }

  private onSocketOpen() {
    this.socket_status = 'Open';
    this.websocket.send(
      JSON.stringify({
        id: '',
        type: 'init_client',
      }),
    );
  }

  private updateState(
    attributes: HardwareStateAttributes | null,
  ) {
    const {
      on,
      message,
    } = attributes ? attributes : {
      on: false,
      message: '',
    };
    this.status = on;
    this.checkbox_status = on;
    this.message = message;
  }
}
