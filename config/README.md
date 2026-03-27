# Config override (main repo)

Config is loaded from this directory so you can **override package defaults** without changing package code.

## How it works

1. **`FASTMVC_CONFIG_I`** is set at startup (in `start_utils`) to this directory (`config/`).
2. Each package (e.g. `fast_platform`, `fast_kafka`, `fast_webrtc` from `fast-platform`, `fast_channels`) resolves config paths in this order:
   - **`FASTMVC_<NAME>_CONFIG_PATH`** – explicit path (e.g. `FASTMVC_DB_CONFIG_PATH=/etc/myapp/db.json`)
   - **`{FASTMVC_CONFIG_I}/{name}/config.json`** – this repo’s override (e.g. `config/db/config.json`)
   - **`config/{name}/config.json`** – cwd-relative default

So any JSON file you add or edit under `config/<name>/config.json` in the main repo **overrides** the package default for that feature.

## Layout

```
config/
├── README.md           ← this file
├── db/
│   └── config.json     ← DB (fast_platform)
├── cache/
│   └── config.json     ← Redis cache (fast_platform)
├── dynamo/
│   └── config.json     ← DynamoDB (fast_platform)
├── kafka/
│   └── config.json     ← Kafka (fast_kafka)
├── webrtc/
│   └── config.json     ← WebRTC (`fast_webrtc` module in `fast-platform`)
├── channels/
│   └── config.json     ← Channels (fast_channels)
└── ...                 ← other configs (configurations/* in main)
```

## Overriding a single config via env

To point one config to a different file (e.g. for tests or multiple envs):

```bash
export FASTMVC_DB_CONFIG_PATH=/etc/myapp/db.json
export FASTMVC_KAFKA_CONFIG_PATH=./config/kafka/prod.json
```

## Moving more config into packages

Configurations that still live in `fast_mvc_main/configurations/` can be moved to their respective packages (e.g. `fast_platform`) using the same pattern: loader in the package, path from `FASTMVC_<X>_CONFIG_PATH` or `FASTMVC_CONFIG_I/<name>/config.json`. This directory remains the place to override in the main repo.
