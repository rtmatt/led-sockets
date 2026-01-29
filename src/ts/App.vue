<script setup lang="ts">
import { computed, onMounted, ref, type Ref } from 'vue';
import {
  type HardwareStateAttributes,
  isClientConnectionInitMessage,
  isHardwareConnectionMessage,
  isHardwareState,
  isSocketMessage,
  type PatchHardwareState,
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
    socket.send(
      JSON.stringify({
        id: '',
        type: 'init_client',
      }),
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
    let payload: unknown;
    try {
      payload = JSON.parse(data);
    } catch (error) {
      console.warn(data);
    }
    if (isSocketMessage(payload)) {
      if (isHardwareState(payload)) {
        updateState(payload.attributes);
      } else if (isHardwareConnectionMessage(payload)) {
        updateState(payload.relationships.hardware_state.data.attributes);
        isHardwareConnected.value = payload.attributes.is_connected;
      } else if (isClientConnectionInitMessage(payload)) {
        updateState(payload.relationships.hardware_state.data.attributes);
        isHardwareConnected.value = payload.attributes.hardware_is_connected;
      }
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
    const payload: PatchHardwareState = {
      type: 'patch_hardware_state',
      attributes: { on: !status.value },
    };
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
