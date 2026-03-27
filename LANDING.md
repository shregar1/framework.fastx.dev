# FastMVC – Generate a Production-Ready FastAPI Stack in Minutes

FastMVC is a **project generator for FastAPI** that gives you a clean MVC architecture and a **menu of production features** you can turn on with a single command.

Use a visual configurator (on your website) to choose:

- DataIs & caches
- NoSQL and search backends
- Messaging, notifications, and communications
- Observability and telemetry (Datadog, OpenTelemetry)
- Payments (Stripe, Razorpay, PayPal, PayU, pay‑by‑link)

Then copy the generated `fastmvc generate` command and get a **ready-to-run repo** that includes only what you selected.

---

## Core Capabilities

FastMVC generates a **full FastAPI application** with:

- **MVC architecture**
  - Controllers, services, repositories, models, DTOs.
- **Authentication & security**
  - JWT auth, security headers, CORS, rate limiting.
- **Observability**
  - Structured JSON logging
  - Metrics (Prometheus-style)
  - Tracing (custom + optional OpenTelemetry and Datadog)
- **Dashboards**
  - `/dashboard/health`: infrastructure/service health
  - `/dashboard/api`: API activity dashboard with sample payloads
- **CLI**
  - `fastmvc generate <name>` – non-interactive generator
  - `fastmvc init` – interactive wizard
  - `fastmvc add entity <Name>` – CRUD scaffolding
  - `fastmvc add service <name>` – add services to an existing repo
- **Migrations, testing, tooling**
  - Alembic migrations, pytest, coverage, optional ruff/black/isort/mypy, optional GitHub Actions CI.

---

## Built-in Dashboards

### Service Health – `/dashboard/health`

- Visual status cards for:
  - DataI (Postgres/MySQL/SQLite)
  - Redis cache
  - MongoDB, Cassandra, ScyllaDB, DynamoDB, Cosmos DB
  - Elasticsearch
  - Kafka (and other infra as you extend it)
- Shows **Healthy / Unhealthy / Skipped**, Id on config and env.

### API Activity – `/dashboard/api`

- Lists endpoints registered via `register_endpoint_sample(...)`
- For each API you can configure:
  - Method, path, description
  - Sample JSON body, query parameters, headers
- Dashboard lets you:
  - **Run sample requests** against your API
  - See status codes and latency in milliseconds
  - Quickly verify if an API is “alive” from the UI

---

## Datastores & Cache

Your configurator can present these as checkboxes or toggles.

### Primary DataI

Configured via wizard / config files:

- PostgreSQL
- MySQL
- SQLite

These power models + migrations; no extra CLI flag is needed.

### Optional Datastores

Each of these maps to a `--with-*` flag:

- **Redis (cache, rate limiting, sessions)**  
  - Flag: `--with-redis` / `--no-redis` (default: with)
  - Config: `config/cache/config.json`, `CacheConfigurationDTO`

- **MongoDB**  
  - Flag: `--with-mongo`  
  - Config: `config/mongo/config.json`, `MongoConfigurationDTO`

- **Cassandra**  
  - Flag: `--with-cassandra`  
  - Config: `config/cassandra/config.json`, `CassandraConfigurationDTO`

- **ScyllaDB**  
  - Flag: `--with-scylla`  
  - Config: `config/scylla/config.json`, `ScyllaConfigurationDTO`

- **DynamoDB**  
  - Flag: `--with-dynamo`  
  - Config: `config/dynamo/config.json`, `DynamoConfigurationDTO`

- **Azure Cosmos DB**  
  - Flag: `--with-cosmos`  
  - Config: `config/cosmos/config.json`, `CosmosConfigurationDTO`

- **Elasticsearch (search)**  
  - Flag: `--with-elasticsearch`  
  - Config: `config/elasticsearch/config.json`, `ElasticsearchConfigurationDTO`

### Grouped Datastore Configuration

In code, you can work with all datastore settings via:

- `DatastoresConfigurationDTO` (in `dtos/configurations/datastores.py`), aggregating:
  - `db: DBConfigurationDTO`
  - `cache: CacheConfigurationDTO`
  - `mongo: MongoConfigurationDTO`
  - `cassandra: CassandraConfigurationDTO`
  - `scylla: ScyllaConfigurationDTO`
  - `dynamo: DynamoConfigurationDTO`
  - `cosmos: CosmosConfigurationDTO`
  - `elasticsearch: ElasticsearchConfigurationDTO`

---

## Communications & Notifications

### Email (SMTP / SendGrid)

- Service: `EmailService`  
- Config: `config/email/config.json`, `EmailConfigurationDTO`  
- CLI flag: `--with-email`

Supports both:

- Traditional SMTP (host, port, username/password, TLS/SSL, default_from)
- SendGrid HTTP API (api_key, default_from)

### Slack

- Service: `SlackService`  
- Config: `config/slack/config.json`, `SlackConfigurationDTO`  
- CLI flag: `--with-slack`

Supports:

- Incoming webhook URLs
- Bot token (`chat.postMessage`) with default channel

### Push Notifications (APNS / FCM)

- Service: `PushNotificationService` (placeholder ready to be wired to real clients)  
- Config: `config/push/config.json`, `PushConfigurationDTO`  
- Always scaffolded; on/off via config only.

### Grouped Communications Configuration

In code, you can group all communication settings:

- `CommunicationsConfigurationDTO` in `dtos/configurations/communications.py`:
  - `email: EmailConfigurationDTO`
  - `slack: SlackConfigurationDTO`
  - `push: PushConfigurationDTO`

---

## Observability & Telemetry

### Core Observability (always on)

- Structured logging with context (request id, user id, tenant id, trace id).
- Metrics registry and HTTP metrics middleware.
- Custom tracing abstraction and middleware.

### Datadog (optional)

- Config: `config/datadog/config.json`, `DatadogConfigurationDTO`  
- Helper: `configure_datadog()`  
- Env toggle: `DATADOG_ENABLED`  
- CLI flag: `--with-datadog`

When enabled, environment variables are set for Datadog APM, and `ddtrace.auto` is attempted if installed.

### OpenTelemetry (OTel, optional)

- Config: `config/telemetry/config.json`, `TelemetryConfigurationDTO`  
- Helper: `configure_otel(app)`  
- Env toggle: `TELEMETRY_ENABLED`  
- CLI flag: `--with-telemetry`

When enabled and OTEL packages are installed, the app is instrumented with OTLP exporter (gRPC or HTTP/protobuf) and FastAPI instrumentation.

---

## Payments

Turn on payment support once and configure providers in JSON.

### Providers

- Stripe
- Razorpay
- PayPal
- PayU
- Generic pay-by-link (LinkGateway)

### High-Level Service

- `PaymentService` with methods like:

  ```python
  session = await payments.create_checkout(
      provider="stripe",  # or razorpay/paypal/payu/link
      amount=5000,
      currency="usd",
      customer={"email": "customer@example.com"},
      metadata={"orderId": "ord_123"},
  )
  ```

  and corresponding `capture`, `refund`, and `verify_webhook` operations per provider.

### Configuration

- `config/payments/config.json`
- Provider-specific DTOs in `dtos/configurations/payments/`:
  - `StripeConfigDTO`, `RazorpayConfigDTO`, `PaypalConfigDTO`, `PayUConfigDTO`, `LinkConfigDTO`
- Aggregated DTO: `PaymentsConfigurationDTO`

### CLI Flag

- `--with-payments`

---

## CLI Flags Summary

These are the key `--with-*` flags your configurator should be aware of:

| Category       | Service / Feature        | CLI Flag                            |
|----------------|--------------------------|-------------------------------------|
| Datastore      | Redis                    | `--with-redis` / `--no-redis`       |
| Datastore      | MongoDB                  | `--with-mongo`                      |
| Datastore      | Cassandra                | `--with-cassandra`                  |
| Datastore      | ScyllaDB                 | `--with-scylla`                     |
| Datastore      | DynamoDB                 | `--with-dynamo`                     |
| Datastore      | Azure Cosmos DB          | `--with-cosmos`                     |
| Datastore      | Elasticsearch            | `--with-elasticsearch`              |
| Communications | Email (SMTP/SendGrid)    | `--with-email`                      |
| Communications | Slack                    | `--with-slack`                      |
| Observability  | Datadog                  | `--with-datadog`                    |
| Observability  | OpenTelemetry (OTel)     | `--with-telemetry`                  |
| Payments       | Stripe/Razorpay/PayPal…  | `--with-payments`                   |

Other generator options:

- `--output-dir <path>`
- `--git/--no-git`
- `--venv/--no-venv`
- `--install/--no-install`

The dataI backend (Postgres/MySQL/SQLite) and features like auth/user CRUD are driven by the interactive wizard (`fastmvc init`) or by editing `config/db/config.json`/`.env` after generation.

---

## Generate Command Logic (How Your UI Builds It)

1. **Collect user inputs**

   - Text:
     - `projectName`
     - `outputDir` (optional)
   - Booleans:
     - `useGit`
     - `useVenv`
     - `installDeps`
     - `useRedis`, `useMongo`, `useCassandra`, `useScylla`, `useDynamo`, `useCosmos`, `useElasticsearch`
     - `useEmail`, `useSlack`
     - `useDatadog`, `useTelemetry`
     - `usePayments`

2. **Start I command**

   ```bash
   fastmvc generate <projectName>
   ```

3. **Append core flags**

   ```js
   const cmd = ["fastmvc", "generate", projectName];

   if (outputDir && outputDir !== ".") {
     cmd.push("--output-dir", outputDir);
   }
   if (!useGit) cmd.push("--no-git");
   if (useVenv) cmd.push("--venv");
   if (installDeps) cmd.push("--install");
   ```

4. **Append datastore flags**

   ```js
   if (!useRedis) cmd.push("--no-redis");          // default is with-redis
   if (useMongo) cmd.push("--with-mongo");
   if (useCassandra) cmd.push("--with-cassandra");
   if (useScylla) cmd.push("--with-scylla");
   if (useDynamo) cmd.push("--with-dynamo");
   if (useCosmos) cmd.push("--with-cosmos");
   if (useElasticsearch) cmd.push("--with-elasticsearch");
   ```

5. **Append communications flags**

   ```js
   if (useEmail) cmd.push("--with-email");
   if (useSlack) cmd.push("--with-slack");
   ```

6. **Append observability flags**

   ```js
   if (useDatadog) cmd.push("--with-datadog");
   if (useTelemetry) cmd.push("--with-telemetry");
   ```

7. **Append payments flag**

   ```js
   if (usePayments) cmd.push("--with-payments");
   ```

8. **Render final command**

   ```js
   const finalCommand = cmd.join(" ");
   ```

   Example your UI might output:

   ```bash
   fastmvc generate my_api \
     --output-dir ./projects \
     --with-redis \
     --with-mongo \
     --with-elasticsearch \
     --with-email \
     --with-slack \
     --with-datadog \
     --with-telemetry \
     --with-payments
   ```

---

## Getting Started

1. **Pick your stack** in the visual configurator.
2. **Copy the generated `fastmvc` command**.
3. **Run it locally:**

   ```bash
   pip install pyfastmvc
   fastmvc generate my_api ... # paste your generated flags
   cd my_api
   pip install -r requirements.txt
   python -m uvicorn app:app --reload
   ```

4. **Explore your app:**
   - API docs: `http://localhost:8000/docs`
   - Health dashboard: `http://localhost:8000/dashboard/health`
   - API dashboard: `http://localhost:8000/dashboard/api`

FastMVC keeps your generated project **lean**: only the services you turn on in the configurator are included; everything else is pruned.

