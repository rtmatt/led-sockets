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
  status_description: string;
}

export interface PatchHardwareState extends SocketMessage {
  attributes: Partial<HardwareStateAttributes>;
  type: 'hardware_state_partial';
}

export type HardwareState = SocketMessage & {
  attributes: HardwareStateAttributes
  type: 'hardware_state',
  relationships?: {
    change_detail?: {
      data: ChangeDetail
    }
  }
}

export function isHardwareState(obj: Record<string, any>): obj is HardwareState {
  const {
    type,
    attributes,
    relationships,
  } = obj;
  if (type !== 'hardware_state') {
    return false;
  }
  if (!attributes || typeof attributes !== 'object') {
    throw TypeError('"hardware_state" missing "attributes"');
  }
  if (!('on' in attributes && typeof attributes.on == 'boolean' && 'status_description' in attributes && typeof attributes.status_description == 'string')) {
    throw TypeError('"hardware_state" invalid "attributes"');
  }
  if (relationships) {
    const {
      change_detail,
    } = relationships;
    if (change_detail && !isChangeDetail(change_detail.data)) {
      throw TypeError('"hardware_state" invalid "change_detail" relationship');
    }
  }

  return true;
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

export type UiClient = SocketMessage & {
  type: 'ui_client'
  attributes: {
    name: string
  }
}

export function isUiClient(obj: Record<string, any>): obj is UiClient {
  const {
    type,
    attributes,
  } = obj;
  if (type !== 'ui_client') {
    return false;
  }
  if (!attributes || typeof attributes !== 'object') {
    throw TypeError('"ui_client" missing "attributes"');
  }
  if ('name' in attributes && typeof attributes.name == 'string') {
    return true;
  }
  throw TypeError('"ui_client" invalid "attributes"');
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
    ui_client?: {
      data: UiClient
    }
    change_detail?: {
      data: ChangeDetail
    }
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
    change_detail,
    ui_client,
  } = relationships;
  if (!isHardwareState(hardware_state.data)) {
    throw TypeError('"server_status" missing "hardware_state" relationship');
  }
  if (ui_client && !isUiClient(ui_client.data)) {
    throw TypeError('"server_status" invalid "ui_client" relationship');
  }
  if (change_detail && !isChangeDetail(change_detail.data)) {
    throw TypeError('"server_status" invalid "change_detail" relationship');
  }
  return true;
}

export type UiMessageAttributes = {
  message: string;
}

export type ChangeDetail = SocketMessage & {
  type: 'change_detail'
  attributes: {
    description: string
    source_name: string
    action_description: string
    source_type: string
    source_id: string
    old_value: any
    new_value: any
  }
}

export function isChangeDetail(message: unknown): message is ChangeDetail {
  if (!isSocketMessage(message)) {
    console.log(message);
    return false;
  }
  if (message.type !== 'change_detail') {
    return false;
  }
  const {
    attributes,
  } = message;
  if (!attributes) {
    throw TypeError('Change detail attributes missing');
  }
  [
    'description',
    'source_name',
    'action_description',
    'source_type',
    'source_id',
  ].forEach((key) => {
    if (!(key in attributes && typeof attributes[key] === 'string')) {
      throw TypeError(`Invalid key ${key}`);
    }
  });

  [
    'old_value',
    'new_value',
  ].forEach((key) => {
    if (!(key in attributes)) {
      throw TypeError(`Missing key ${key}`);
    }
  });


  return true;
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
