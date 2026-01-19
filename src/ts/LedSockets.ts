import {
  type HardwareStateAttributes,
  isClientConnectionInitMessage,
  isHardwareConnectionMessage,
  isHardwareStateMessage,
  isSocketMessage,
  type PatchHardwareState,
} from './types.ts';

const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

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
    socket: 'Closed',
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
    this.socket_status = 'Attempting to connect';
    this.hardware_state = false;
    this.message = '';
    this.status = false;
    this.checkbox_status = false;

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
    this.elements.button.disabled = !connected;
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
    if (isSocketMessage(message)) {
      if (isHardwareStateMessage(message)) {
        this.updateState(message.attributes);
      } else if (isHardwareConnectionMessage(message)) {
        this.updateState(message.relationships.hardware_state.data.attributes);
        this.hardware_state = message.attributes.is_connected;
      } else if (isClientConnectionInitMessage(message)) {
        this.updateState(message.relationships.hardware_state.data.attributes);
        this.hardware_state = message.attributes.hardware_is_connected;
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
