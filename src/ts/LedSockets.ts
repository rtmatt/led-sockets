/* TODO:
- [ ] Disable checkbox/button when disconnected
- [ ] proper type narrowing
- [ ] add ids to json:api objects across full suite
*/
const {

  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

interface SocketMessage {
  type: string;
  attributes?: Object | null;
}

type HardwareStateAttributes = {
  on: boolean;
  message: string;
}

interface HardwareStateMessage extends SocketMessage {
  type: 'hardware_state',
  attributes: HardwareStateAttributes | null
}

interface HardwareConnectionMessage extends SocketMessage {
  type: 'hardware_connection',
  attributes: {
    is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareStateMessage
    }
  }
}

interface ClientConnectionInitMessage extends SocketMessage {
  type: 'client_init',
  attributes: {
    hardware_is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareStateMessage
    }
  }
}

interface PatchHardwareState extends SocketMessage {
  type: 'patch_hardware_state';
  attributes: Partial<HardwareStateAttributes>;
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
      const payload: PatchHardwareState = {
        type: 'patch_hardware_state',
        attributes: { on: is_on },
      };
      this.websocket.send(JSON.stringify(payload));
    });
  }

  private onSocketClose(e: CloseEvent) {
    console.error("Socket Closed"+e.reason);
    this.updateHardwareStatus(false);
    this.updateSocketStatus('Closed');
  }

  private onSocketError(e: Event) {
    console.error("Socket Error",e);
    this.updateHardwareStatus(false);
    this.updateSocketStatus('Error');
  }

  private onSocketMessage(event: MessageEvent) {
    const { data } = event;
    const message: unknown = JSON.parse(data);
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
          this.updateHardwareStatus(payload.attributes.is_connected);
          break;
        case 'client_init':
          payload = message as ClientConnectionInitMessage;
          this.updateState(payload.relationships.hardware_state.data.attributes);
          this.updateHardwareStatus(payload.attributes.hardware_is_connected);
          break;
      }
    }
  }

  private onSocketOpen() {
    this.updateSocketStatus('Open');
    this.websocket.send(
      JSON.stringify({
        id: '',
        type: 'init_client',
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
    attributes: HardwareStateAttributes | null,
  ) {
    const {
      on,
      message,
    } = attributes ? attributes : {
      on: false,
      message: '',
    };
    this.state.status = on;
    this.checkbox.checked = on;
    this.messageContainer.innerText = message
  }
}
