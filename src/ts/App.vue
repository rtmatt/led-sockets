<script setup lang="ts">
import { computed, nextTick, onMounted, type Ref, ref, useTemplateRef } from 'vue';
import {
  getUiMessageRelation,
  type HardwareStateAttributes,
  isClientConnectionInitMessage,
  isHardwareConnectionMessage,
  isHardwareState,
  isSocketMessage,
  isUiMessage,
  type PatchHardwareState,
  type UiMessageAttributes,
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
const uiMessages: Ref<UiMessageAttributes[]> = ref([]);
const messageContainer = useTemplateRef('scrollParent');

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
    const initPayload = {
      id: '',
      type: 'init_client',
    };
    socket.send(
      JSON.stringify({
        data: initPayload,
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
      const parse = JSON.parse(data);
      payload = parse['data'];
      error = parse['error'];
    } catch (e) {
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
      } else if (isUiMessage(payload)) {
        addMessage(payload.attributes);
      } else {
        console.warn('Unprocessed message received');
      }

      const uiMessageRelation = getUiMessageRelation(payload);
      if (uiMessageRelation) {
        addMessage(uiMessageRelation.attributes);
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
      id: '',
      attributes: { on: !status.value },
    };
    ws.send(JSON.stringify({ data: payload }));
  } else {
    throw Error('No active connection');
  }
}

function reconnect() {
  log('RECONNECT');
  connect();
}

function addMessage(message: UiMessageAttributes) {
  uiMessages.value.push(message);
  nextTick(() => {
    const messagesScrollContainer: HTMLElement | null = messageContainer.value;
    if (messagesScrollContainer) {
      messagesScrollContainer.scrollTop = messagesScrollContainer.scrollHeight - messagesScrollContainer.offsetHeight;
    }
  });
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
const displayMessages = computed(() => {
  return uiMessages.value.slice();
});
const checkboxChecked = computed(() => {
  return status.value;
});
</script>
<style>
.messages-container {
  border: solid 1px #efefef;
  height: 250px;
  position: relative;
  overflow-y: auto;
}

.messages-container__content {
  box-sizing: border-box;
  min-height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 8px;
}

p {
  margin: 0
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    padding: 0;
    margin: 0;
  }
}
</style>
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
    <div class="messages-container" ref="scrollParent">
      <div class="messages-container__content">
        <ul>
          <li v-for="uiMessage in displayMessages">
            <p>{{ uiMessage.message }}
            </p>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
