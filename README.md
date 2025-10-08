## CVH Architecture Overview

```mermaid
flowchart TD

subgraph SYSTEM [SYSTEM Layer - Boot, Logs & Config]
  subgraph BOOT [Bootstrap]
    A1[index.js / init.js]
    A2[setup_heartbeat()]
    A3[handleKeyCode()]
  end

  subgraph LOG [Logging & Diagnostics]
    L1[logger.js]
    L2[LOG_LEVELS]
    L3[debug_console / ampt.api.sendLog()]
  end

  subgraph CONF [Configuration]
    C1[config.js]
    C2[Environment vars / feature flags]
  end

  A1 --> A2 --> A3
  L1 --> L3
  C1 --> A1
end

subgraph CORE [CORE Layer - Data, Logic & Hardware]
  subgraph API [API Layer]
    B1[apiClient.js]
    B2[movies.js / hotel.js / guest.js / messages.js]
    B3[endpoints legacy adapter]
  end

  subgraph LOGIC [Logic Layer]
    D1[adsManager.js]
    D2[cartManager.js]
    D3[languageManager.js]
    D4[messageService.js]
  end

  subgraph HARDWARE [Hardware Layer]
    E1[lgtv/player.js]
    E2[lgtv/volume.js]
    E3[lgtv/network.js]
    E4[lgtv/watchdog.js]
    E5[hcap_pretty.js (LG API)]
  end

  subgraph STATE [State & Utils]
    F1[globalState.js]
    F2[storage.js]
    F3[utils.js]
  end

  B1 --> B2
  F1 --> B1
  D1 --> B2
  D2 --> F2
  D3 --> F1
  D4 --> B2
  E1 --> B2
end

subgraph UI [UI Layer - Views & Modals]
  subgraph VIEWS [Views]
    V1[homeView.js]
    V2[entertainmentView.js]
    V3[liveTvView.js]
    V4[hotelView.js]
    V5[accountView.js]
    V6[messageView.js]
    V7[languageView.js]
  end

  subgraph MODALS [Modals]
    M1[cartModal.js]
    M2[adultModal.js]
  end

  subgraph COMPONENTS [Components]
    U1[loader.js]
    U2[banner.js]
    U3[navigation.js]
  end
end

A1 -->|init| F1
A1 -->|setup API| B1
A1 -->|bind events| V1
V1 --> D1
V2 --> D1
V3 --> E1
V4 --> B2
V5 --> D4
V6 --> D4
V7 --> D3
M1 --> D2
M2 --> D3
D1 --> B2
B2 --> F1
E1 --> L1
L1 --> L3
F2 --> L1
A3 --> V1
