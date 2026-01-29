
export interface SocketMessage {
  attributes?: Record<string, any> | null;
  relationships?: Record<string, any>;
  type: string;
  id: string
}

export type HardwareStateAttributes = {
  on: boolean;
  message: string;
}

export interface ErrorMessage extends SocketMessage {
  attributes: {
      message: string
  }
  type: 'error',
}

export interface HardwareState extends SocketMessage {
  attributes: HardwareStateAttributes
  type: 'hardware_state',
}

export interface HardwareConnectionMessage extends SocketMessage {
  attributes: {
    is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareState
    }
  }
  type: 'hardware_connection',
}

export interface ClientConnectionInitMessage extends SocketMessage {
  attributes: {
    hardware_is_connected: boolean
  }
  relationships: {
    hardware_state: {
      data: HardwareState
    }
  }
  type: 'client_init',
}

export interface PatchHardwareState extends SocketMessage {
  attributes: Partial<HardwareStateAttributes>;
  type: 'patch_hardware_state';
}

export function isSocketMessage(message: unknown): message is SocketMessage {
  return !!message && typeof message === 'object' && 'type' in message && !!message.type;
}

export function isHardwareState(message: SocketMessage): message is HardwareState {
  if (message.type !== 'hardware_state') {
    return false;
  }
  const { attributes } = message;
  if (!attributes) {
    return true;
  }
  return 'on' in attributes && typeof attributes.on == 'boolean' && 'message' in attributes && typeof attributes.message == 'string';
}

export function isClientConnectionInitMessage(message: SocketMessage): message is ClientConnectionInitMessage {
  if (message.type !== 'client_init') {
    return false;
  }
  const {
    attributes,
    relationships,
  } = message;
  if (!attributes || !relationships) {
    return true;
  }
  if (!('hardware_is_connected' in attributes && typeof attributes.hardware_is_connected == 'boolean')) {
    return false;
  }
  const { hardware_state } = relationships;
  if (!hardware_state) {
    return false;
  }
  const { data } = hardware_state;
  return isHardwareState(data);
}

export function isHardwareConnectionMessage(message: SocketMessage): message is HardwareConnectionMessage {
  if (message.type !== 'hardware_connection') {
    return false;
  }
  const {
    attributes,
    relationships,
  } = message;
  if (!attributes || !relationships) {
    return true;
  }
  if (!('is_connected' in attributes && typeof attributes.is_connected == 'boolean')) {
    return false;
  }
  const { hardware_state } = relationships;
  if (!hardware_state) {
    return false;
  }
  const { data } = hardware_state;
  return isHardwareState(data);
}
