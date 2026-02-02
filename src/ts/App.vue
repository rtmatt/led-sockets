<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue';
import {
  type ErrorMessage,
  type HardwareStateAttributes,
  type InitClientMessage,
  isErrorMessage,
  isEventMessage,
  isHardwareState,
  isServerStatus,
  isTalkbackMessage,
  type PatchHardwareStateMessage,
  type ServerError,
  type SocketMessage,
  type TalkbackMessageMessage,
} from './types';

const {
  VITE_WEB_SOCKET_URL,
  VITE_PRODUCTION_WEB_SOCKET_URL,
  PROD,
} = import.meta.env;

let message: Ref<string> = ref('');
let socketStatus: Ref<string> = ref('Closed');
let connected: Ref<boolean> = ref(false);
let connecting: Ref<boolean> = ref(false);
let status: Ref<boolean> = ref(false);
let isHardwareConnected: Ref<boolean> = ref(false);

let abortController: AbortController | undefined;
let ws: WebSocket | null = null;

window.addEventListener('pagehide', () => {
  if (ws) {
    ws.close();
  }
  ws = null;
});
window.addEventListener('pageshow', (e: PageTransitionEvent) => {
  if (e.persisted) {
    if (ws && ws.readyState === WebSocket.OPEN || connecting.value) {
      return;
    }
    connect();
  }
});

function log(...args: any) {
  if (!PROD) {
    console.log(...args);
  }
}

function updateState(attributes: HardwareStateAttributes | null) {
  const payload = attributes || {
    on: false,
    message: '',
  };
  message.value = payload.message;
  status.value = payload.on;
}

function openConnection() {
  log('OPENING CONNECTION');
  const socket = new WebSocket(PROD ? VITE_PRODUCTION_WEB_SOCKET_URL : VITE_WEB_SOCKET_URL);
  const controller = new AbortController();

  socket.addEventListener('open', () => {
    log('OPEN');
    connecting.value = false;
    connected.value = true;
    socketStatus.value = 'Open';
    const payload: InitClientMessage = [
      'init_client',
      {
        data: {
          id: '',
          type: 'ui_client',
        },
      },
    ];
    socket.send(
      JSON.stringify(payload),
    );
  }, { signal: controller.signal });

  socket.addEventListener('error', () => {
    log('ERROR');
  }, { signal: controller.signal });

  socket.addEventListener('close', () => {
    log('CLOSE');
    connected.value = false;
    socketStatus.value = 'Closed';
    controller.abort();// shouldn't be necessary, but oh well
  }, { signal: controller.signal });

  socket.addEventListener('message', (event: MessageEvent) => {
    log('MESSAGE');
    const { data } = event;

    let event_type: string;
    let event_payload: { data: SocketMessage };
    let parsed: unknown;
    try {
      parsed = JSON.parse(data);
    } catch (error) {
      console.warn(data);
    }
    if (isErrorMessage(parsed)) {
      const parsedElement: ErrorMessage[1] = parsed[1];
      parsedElement.errors.forEach((e: ServerError) => {
        console.error(`Server Error: ${e.detail}`);
      });
      return;
    }

    if (!isEventMessage(parsed)) {
      console.warn('Ignoring non-event-message');
      return;
    }
    [event_type, event_payload] = parsed;
    const payload: SocketMessage = event_payload.data;
    switch (event_type) {
      case'client_init':
        if (isServerStatus(payload)) {
          updateState(payload.relationships.hardware_state.data.attributes);
          isHardwareConnected.value = payload.attributes.hardware_is_connected;
        }
        break;
      case 'hardware_disconnected':
        if (isServerStatus(payload)) {
          updateState(payload.relationships.hardware_state.data.attributes);
          isHardwareConnected.value = payload.attributes.hardware_is_connected;
        }
        break;
      case 'hardware_connected':
        if (isServerStatus(payload)) {
          updateState(payload.relationships.hardware_state.data.attributes);
          isHardwareConnected.value = payload.attributes.hardware_is_connected;
        }
        break;
      case 'hardware_updated':
        if (isHardwareState(payload)) {
          updateState(payload.attributes);
        }
        break;
      case 'client_joined':
        if (isServerStatus(payload)) {
          log(`Client join received and unprocessed`);
        }
        break;
      case 'talkback_message':
        if (isTalkbackMessage(payload)) {
          log(`Talkback received: ${payload.attributes.message}`);
        }
        break;
      default:
        console.warn('Unprocessed message received: ' + event_type);
        break;
    }

  }, { signal: controller.signal });

  return {
    websocket: socket,
    abortController: controller,
  };
}

function connect() {
  if (connecting.value) {
    return;
  }
  if (ws) {
    if (abortController) abortController.abort();
    ws.close();
  }
  connecting.value = true;
  const result = openConnection();
  ws = result.websocket;
  abortController = result.abortController;
}

function onButtonClick() {
  log('BUTTON CLICK');
  if (ws) {
    const payload: PatchHardwareStateMessage = [
      'patch_hardware_state',
      {
        data: {
          id: '',
          type: 'hardware_state',
          attributes: {
            on: !status.value,
          },
        },
      },
    ];

    ws.send(JSON.stringify(payload));
  } else {
    throw Error('No active connection');
  }
}

function reconnect() {
  log('RECONNECT');
  connect();
}

onMounted(() => {
  connect();
});
const hardwareStatus = computed(() => {
  return isHardwareConnected.value ? 'Connected' : 'Disconnected';
});
const buttonDisabled = computed(() => {
  return !isHardwareConnected.value;
});
const showReconnect = computed(() => {
  if (connected.value) {
    return false;
  }
  if (connecting.value) {
    return false;
  }
  return true;
});
const checkboxChecked = computed(() => {
  return status.value;
});
</script>

<template>
  <div>
    <button @click="onButtonClick" :disabled="buttonDisabled">Click Me</button>
    <input disabled :checked="checkboxChecked" readonly id="checkbox" type="checkbox" />
    <div v-if="message">{{ message }}</div>
    <div>
      <dl>
        <dt>Socket Status:</dt>
        <dd>
          <span>{{ socketStatus }}&nbsp;</span>
          <small>
            <a href="#" v-if="showReconnect" @click="reconnect">reconnect</a>
          </small>
        </dd>
        <dt>Hardware Status:</dt>
        <dd>{{ hardwareStatus }}</dd>
      </dl>
    </div>
  </div>
</template>
