export interface SocketMessage {
  attributes?: Record<string, any> | null;
  relationships?: Record<string, any>;
  type: string;
  id: string;
}

export function isSocketMessage(message: unknown): message is SocketMessage {
  return !!message && typeof message === 'object' && 'type' in message && !!message.type;
}

export type HardwareStateAttributes = {
  on: boolean;
  message: string; // @todo: remove
}

export interface PatchHardwareState extends SocketMessage {
  attributes: Partial<HardwareStateAttributes>;
  type: 'hardware_state';
}

export type HardwareState = SocketMessage & {
  attributes: HardwareStateAttributes
  type: 'hardware_state',
}

export function isHardwareState(obj: Record<string, any>): obj is HardwareState {
  const {
    type,
    attributes,
  } = obj;
  if (type !== 'hardware_state') {
    return false;
  }
  if (!attributes || typeof attributes !== 'object') {
    throw TypeError('"hardware_state" missing "attributes"');
  }
  return 'on' in attributes && typeof attributes.on == 'boolean' && 'message' in attributes && typeof attributes.message == 'string';
}

type TalkbackMessage = SocketMessage & {
  type: 'talkback_message'
  attributes: {
    message: string
  }
}

export function isTalkbackMessage(obj: Record<string, any>): obj is TalkbackMessage {
  const {
    type,
    attributes,
  } = obj;
  if (type !== 'talkback_message') {
    return false;
  }
  if (!attributes || typeof attributes !== 'object') {
    throw TypeError('"talkback_message" missing "attributes"');
  }
  return 'message' in attributes && typeof attributes.message == 'string';
}

type ServerStatus = SocketMessage & {
  type: 'server_status',
  attributes: {
    hardware_is_connected: boolean
  },
  relationships: {
    hardware_state: {
      data: HardwareState
    },
  }
}

export function isServerStatus(obj: Record<string, any>): obj is ServerStatus {
  const {
    type,
    attributes,
    relationships,
  } = obj;
  if (type !== 'server_status') {
    return false;
  }
  if (!attributes || typeof attributes !== 'object') {
    throw TypeError('"server_status" missing "attributes"');
  }
  if (!('hardware_is_connected' in attributes) || typeof attributes.hardware_is_connected !== 'boolean') {
    throw TypeError('"server_status" invalid attributes');
  }
  if (!relationships || typeof relationships !== 'object') {
    throw TypeError('"server_status" missing "relationships"');
  }
  const {
    hardware_state,
    // @todo: add predicates for these if they ever end up in use
    // ui_clients,
    // hardware_client,
  } = relationships;
  if (!isHardwareState(hardware_state.data)) {
    throw TypeError('"server_status" missing "hardware_state" relationship');
  }

  return true;
}

export type UiMessageAttributes = {
  message: string;
}

export interface UIMessage extends SocketMessage {
  attributes: UiMessageAttributes
  type: 'ui_message',
}

export function isUiMessage(message: SocketMessage): message is UIMessage {
  if (message.type !== 'ui_message') {
    return false;
  }
  const {
    attributes,
  } = message;
  if (!attributes) {
    return true;
  }
  if (!('message' in attributes && typeof attributes.message == 'string')) {
    return false;
  }
  return true;
}

export function getUiMessageRelation(message: SocketMessage): UIMessage | null {
  const {
    relationships,
  } = message;
  if (!relationships) {
    return null;
  }
  if (!relationships.ui_message) {
    return null;
  }
  if (isUiMessage(relationships.ui_message.data)) {
    return relationships.ui_message.data;
  }
  return null;
}

type EventMessage<E extends string, T extends SocketMessage> = [E, { data: T }]

export function isEventMessage(event: unknown): event is EventMessage<any, any> {
  if (!Array.isArray(event)) {
    return false;
  }
  const event_name = event[0];
  if (typeof event_name !== 'string') {
    return false;
  }
  const payload = event[1];
  if (!(payload && typeof payload === 'object')) {
    return false;
  }

  return 'data' in payload && payload.data && isSocketMessage(payload.data);
}

type InitClient = SocketMessage & {
  type: 'ui_client',
}
export type ServerError = {
  detail: string
}

function isServerError(obj: unknown): obj is ServerError {
  return !!obj && typeof obj === 'object' && 'detail' in obj && typeof obj.detail === 'string';
}

export function isErrorMessage(event: unknown): event is ErrorMessage {
  if (!Array.isArray(event)) {
    return false
  }
  const event_name = event[0];
  if (event_name !== 'error') {
    return false
  }
  const payload = event[1];
  if (!(payload && typeof payload === 'object'))   {
    throw TypeError('Payload is not an object')
  }
  const { errors } = payload;
  if (!errors) {
    throw TypeError('Errors key not present')
  }
  if (!Array.isArray(errors)) {
    throw TypeError('Errors is not an array')
  }

  for (let i = 0; i < errors.length; i++) {
    const datum = errors[i];
    if (!isServerError(datum)) {
      throw TypeError('Datum is not an Error')
    }
  }

  return true;
}

export type InitClientMessage = EventMessage<'init_client', InitClient>
export type ClientInitMessage = EventMessage<'client_init', ServerStatus>
export type HardwareDisconnectedMessage = EventMessage<'hardware_disconnected', ServerStatus>
export type HardwareConnectedMessage = EventMessage<'hardware_connected', ServerStatus>
export type HardwareUpdatedMessage = EventMessage<'hardware_updated', HardwareState>
export type TalkbackMessageMessage = EventMessage<'talkback_message', TalkbackMessage>
export type PatchHardwareStateMessage = EventMessage<'patch_hardware_state', PatchHardwareState>
export type ErrorMessage = ['error', { errors: ServerError[] }]
