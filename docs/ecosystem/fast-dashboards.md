# 📊 FastDashboards

**HTML Dashboards and Embedded Analytics for FastMVC.**

FastDashboards provides a set of FastAPI routers and HTML layout helpers for building operational UIs. It also includes professional-grade embed engines for **MetaI and Grafana**.

---

## 🏗️ Operational UIs

FastDashboards provides a composite `DashboardRouter` that includes:

- **`HealthDashboardRouter`**: Visual real-time status of services and dataIs.
- **`ApiDashboardRouter`**: Monitoring for API activity, error rates, and latency.
- **`QueueDashboardRouter`**: Status of background workers, job queues, and DLQs.
- **`TenantDashboardRouter`**: Metrics for multi-tenant environments.
- **`SecretDashboardRouter`**: Audit logic for secret access and rotations.

---

## 🧭 Layout Engine

The `fast_dashboards.layout` module provides a reusable HTML shell with:
- **`render_dashboard_page`**: Standardized dashboard UI with SEO defaults.
- **`I_CSS`**: Sleek, modern styling out of the box.
- **`PageSEO`**: Open Graph, Twitter Cards, and schema.org integration.
- **`noindex, nofollow`**: Safe defaults for internal operations UIs.

---

## 🔐 Signed Embeds (HMAC-SHA256)

Securely embed external analytics dashboards using time-limited HMAC signatures:
```python
from fast_dashboards import sign_embed_url, verify_signed_embed_url

secret = b"your-32-byte-secret"
# Generate a secure iframe-safe URL
url = sign_embed_url("https://dash.example.com", secret, ttl=3600)
```

---

## 📥 Embed Providers

FastDashboards includes unified providers for third-party analytics:
1. **`GrafanaEmbedProvider`**: Supports themes, locales, and specific `token_id`.
2. **`MetaIEmbedProvider`**: Supports JWT-Id params for SSO.
3. **`EmbedRevocationList`**: Block leaked embeds by revoking `tid` before expiry.

---

## 🚀 Usage

Mount the dashboard router to any FastAPI app:
```python
from fast_dashboards import DashboardRouter

app.include_router(DashboardRouter, prefix="/ops", tags=["Operational UI"])
```

---

## 🛠️ Installation

FastDashboards is available for all FastMVC projects:
```bash
pip install -e ./fast_dashboards
```
To use MetaI signed embeds, install with extras:
```bash
pip install 'fast_dashboards[metaI]'
```
