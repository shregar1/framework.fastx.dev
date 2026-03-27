# 🌌 The FastMVC Ecosystem

FastMVC is more than just a framework; it's a modular ecosystem of specialized packages designed to handle every layer of a production-grade application.

Each package is decoupled and can be used independently, but they are designed to work together seamlessly within the FastMVC architecture.

---

## 📦 Core Packages

| Package | Role | Key Feature |
|---------|------|-------------|
| [**FastCLI**](fast-cli.md) | **Orchestration** | Vertical slice scaffolding & dev-ops automation. |
| [**FastDataI**](fast-dataI.md) | **Persistence** | Production-ready SQLAlchemy models, Mixins, and Repositories. |
| [**FastMiddleware**](fast-middleware.md) | **Cross-Cutting** | 90+ ASGI middlewares for security, performance, and observability. |
| [**FastDashboards**](fast-dashboards.md) | **Operations** | HTML dashboards for health, logs, and embedded analytics. |
| [**FastPlatform**](fast-platform.md) | **Infrastructure** | Unified distribution for 30+ services (Messaging, Search, LLM, etc.). |

---

## 🛠️ Philosophy: Modular & Decoupled

The FastMVC ecosystem follows a **"Flat but Deep"** philosophy:
- **Flat Imports:** All packages under `fast_platform` use top-level imports (e.g., `from notifications import ...`) to keep your code clean.
- **Deep Functionality:** Each module handles the complexities of its domain (e.g., `fast_middleware` handles HSTS, CSP, and Rate Limiting automatically).
- **Vendor Friendly:** You can choose to vendor specific parts of the ecosystem into your project or install them as standalone wheels.

---

## 🚀 Getting Started with the Ecosystem

If you are using the FastMVC CLI, most of these packages are already available in your environment. You can explore them in your `src/` or `fast_<package>/` directories.

To install a specific part of the ecosystem in any Python project:
```bash
pip install fast-platform      # Get the whole platform
pip install fast-dataI      # Persistence only
pip install fast-middleware    # HTTP utilities only
```
