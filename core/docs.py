"""FastMVC Custom API Documentation.

Provides branded Swagger UI and ReDoc with dark mode and custom styling.

Usage:
    from core.docs import setup_custom_docs
    setup_custom_docs(app)
"""

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

# FastMVC Brand Colors
FASTMVC_THEME = {
    "primary": "#0ea5e9",  # Cyan 500
    "secondary": "#d946ef",  # Fuchsia 500
    "accent": "#8b5cf6",  # Violet 500
    "dark": {
        "bg": "#0f0f1a",  # Dark background
        "surface": "#1a1a2e",  # Card/surface
        "text": "#e2e8f0",  # Primary text
        "muted": "#94a3b8",  # Secondary text
        "border": "#2d3748",  # Borders
    },
}

# Custom CSS for Swagger UI dark mode
SWAGGER_UI_CSS = f"""
<style>
    /* FastMVC Dark Theme for Swagger UI */
    
    :root {{
        --fastmvc-primary: {FASTMVC_THEME["primary"]};
        --fastmvc-secondary: {FASTMVC_THEME["secondary"]};
        --fastmvc-accent: {FASTMVC_THEME["accent"]};
        --fastmvc-bg: {FASTMVC_THEME["dark"]["bg"]};
        --fastmvc-surface: {FASTMVC_THEME["dark"]["surface"]};
        --fastmvc-text: {FASTMVC_THEME["dark"]["text"]};
        --fastmvc-muted: {FASTMVC_THEME["dark"]["muted"]};
        --fastmvc-border: {FASTMVC_THEME["dark"]["border"]};
    }}
    
    /* Body & Background */
    body {{
        background: var(--fastmvc-bg) !important;
        color: var(--fastmvc-text) !important;
    }}
    
    /* Top Bar */
    .swagger-ui .topbar {{
        background: linear-gradient(135deg, var(--fastmvc-primary), var(--fastmvc-accent)) !important;
        border-bottom: 1px solid var(--fastmvc-border);
    }}
    
    .swagger-ui .topbar .download-url-wrapper .select-label span {{
        color: var(--fastmvc-text) !important;
    }}
    
    /* Logo/Brand */
    .swagger-ui .topbar .topbar-wrapper {{
        display: flex;
        align-items: center;
    }}
    
    .swagger-ui .topbar .topbar-wrapper:before {{
        content: "⚡ FastMVC";
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        margin-right: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .swagger-ui .topbar img {{
        display: none;
    }}
    
    /* Info Section */
    .swagger-ui .info {{
        background: var(--fastmvc-surface) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        margin: 1rem 0 !important;
        border: 1px solid var(--fastmvc-border);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    }}
    
    .swagger-ui .info .title {{
        color: var(--fastmvc-text) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }}
    
    .swagger-ui .info .title small {{
        background: var(--fastmvc-primary) !important;
        color: white !important;
        border-radius: 4px !important;
        padding: 0.25rem 0.5rem !important;
    }}
    
    .swagger-ui .info p,
    .swagger-ui .info li {{
        color: var(--fastmvc-muted) !important;
    }}
    
    .swagger-ui .info a {{
        color: var(--fastmvc-primary) !important;
    }}
    
    .swagger-ui .info h2,
    .swagger-ui .info h3,
    .swagger-ui .info h4 {{
        color: var(--fastmvc-text) !important;
    }}
    
    /* Schemes */
    .swagger-ui .scheme-container {{
        background: var(--fastmvc-surface) !important;
        border-radius: 8px !important;
        border: 1px solid var(--fastmvc-border);
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.2);
    }}
    
    .swagger-ui .scheme-container .schemes > label span {{
        color: var(--fastmvc-muted) !important;
    }}
    
    /* Operations */
    .swagger-ui .opblock {{
        background: var(--fastmvc-surface) !important;
        border: 1px solid var(--fastmvc-border) !important;
        border-radius: 8px !important;
        margin: 0.75rem 0 !important;
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.2);
    }}
    
    .swagger-ui .opblock .opblock-summary {{
        border-bottom: 1px solid var(--fastmvc-border);
    }}
    
    .swagger-ui .opblock .opblock-summary-method {{
        border-radius: 4px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }}
    
    .swagger-ui .opblock .opblock-summary-path {{
        color: var(--fastmvc-text) !important;
    }}
    
    .swagger-ui .opblock .opblock-summary-description {{
        color: var(--fastmvc-muted) !important;
    }}
    
    /* HTTP Method Colors */
    .swagger-ui .opblock.opblock-get .opblock-summary-method {{
        background: #3b82f6 !important;
    }}
    
    .swagger-ui .opblock.opblock-post .opblock-summary-method {{
        background: #10b981 !important;
    }}
    
    .swagger-ui .opblock.opblock-put .opblock-summary-method {{
        background: #f59e0b !important;
    }}
    
    .swagger-ui .opblock.opblock-delete .opblock-summary-method {{
        background: #ef4444 !important;
    }}
    
    .swagger-ui .opblock.opblock-patch .opblock-summary-method {{
        background: #8b5cf6 !important;
    }}
    
    /* Operation Details */
    .swagger-ui .opblock-body {{
        background: var(--fastmvc-bg) !important;
    }}
    
    .swagger-ui .opblock-section-header {{
        background: var(--fastmvc-surface) !important;
        border-bottom: 1px solid var(--fastmvc-border);
    }}
    
    .swagger-ui .opblock-section-header h4 {{
        color: var(--fastmvc-text) !important;
    }}
    
    /* Parameters */
    .swagger-ui .parameters-col_name {{
        color: var(--fastmvc-primary) !important;
    }}
    
    .swagger-ui .parameter__name {{
        color: var(--fastmvc-text) !important;
    }}
    
    .swagger-ui .parameter__type {{
        color: var(--fastmvc-secondary) !important;
    }}
    
    .swagger-ui .parameter__in {{
        color: var(--fastmvc-muted) !important;
    }}
    
    /* Tables */
    .swagger-ui table {{
        background: var(--fastmvc-surface) !important;
        border: 1px solid var(--fastmvc-border) !important;
        border-radius: 8px;
    }}
    
    .swagger-ui table thead tr th {{
        background: var(--fastmvc-bg) !important;
        color: var(--fastmvc-text) !important;
        border-bottom: 1px solid var(--fastmvc-border);
    }}
    
    .swagger-ui table tbody tr td {{
        color: var(--fastmvc-muted) !important;
        border-bottom: 1px solid var(--fastmvc-border);
    }}
    
    /* Models */
    .swagger-ui .model-box {{
        background: var(--fastmvc-surface) !important;
        border: 1px solid var(--fastmvc-border) !important;
        border-radius: 8px;
    }}
    
    .swagger-ui .model-title {{
        color: var(--fastmvc-text) !important;
    }}
    
    .swagger-ui .prop-name {{
        color: var(--fastmvc-primary) !important;
    }}
    
    .swagger-ui .prop-type {{
        color: var(--fastmvc-secondary) !important;
    }}
    
    /* Code Samples */
    .swagger-ui .curl {{
        background: var(--fastmvc-bg) !important;
        border: 1px solid var(--fastmvc-border) !important;
        border-radius: 8px;
    }}
    
    .swagger-ui .curl command {{
        color: var(--fastmvc-text) !important;
    }}
    
    /* Response Section */
    .swagger-ui .responses-inner {{
        background: var(--fastmvc-surface) !important;
    }}
    
    .swagger-ui .responses-inner h4,
    .swagger-ui .responses-inner h5 {{
        color: var(--fastmvc-text) !important;
    }}
    
    /* Try It Out Button */
    .swagger-ui .btn {{
        background: var(--fastmvc-primary) !important;
        border-color: var(--fastmvc-primary) !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .swagger-ui .btn:hover {{
        background: var(--fastmvc-accent) !important;
        border-color: var(--fastmvc-accent) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
    }}
    
    .swagger-ui .btn.cancel {{
        background: transparent !important;
        border-color: var(--fastmvc-border) !important;
        color: var(--fastmvc-muted) !important;
    }}
    
    .swagger-ui .btn.execute {{
        background: linear-gradient(135deg, var(--fastmvc-primary), var(--fastmvc-accent)) !important;
    }}
    
    /* Input Fields */
    .swagger-ui input[type="text"],
    .swagger-ui textarea {{
        background: var(--fastmvc-bg) !important;
        border: 1px solid var(--fastmvc-border) !important;
        color: var(--fastmvc-text) !important;
        border-radius: 6px;
    }}
    
    .swagger-ui input[type="text"]:focus,
    .swagger-ui textarea:focus {{
        border-color: var(--fastmvc-primary) !important;
        outline: none;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2);
    }}
    
    /* Dropdown */
    .swagger-ui .select-wrapper select {{
        background: var(--fastmvc-bg) !important;
        border: 1px solid var(--fastmvc-border) !important;
        color: var(--fastmvc-text) !important;
    }}
    
    /* Response Codes */
    .swagger-ui .response-col_status {{
        color: var(--fastmvc-text) !important;
        font-weight: 600;
    }}
    
    .swagger-ui .response-col_description {{
        color: var(--fastmvc-muted) !important;
    }}
    
    /* Auth */
    .swagger-ui .auth-container {{
        background: var(--fastmvc-surface) !important;
        border: 1px solid var(--fastmvc-border);
        border-radius: 8px;
    }}
    
    .swagger-ui .auth-container h3,
    .swagger-ui .auth-container h4 {{
        color: var(--fastmvc-text) !important;
    }}
    
    .swagger-ui .auth-container p {{
        color: var(--fastmvc-muted) !important;
    }}
    
    /* Loading */
    .swagger-ui .loading-container .loading {{
        color: var(--fastmvc-primary) !important;
    }}
    
    /* Errors */
    .swagger-ui .errors-wrapper {{
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px;
    }}
    
    .swagger-ui .errors-wrapper .errors h4 {{
        color: #ef4444 !important;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--fastmvc-bg);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--fastmvc-border);
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--fastmvc-muted);
    }}
    
    /* Filter */
    .swagger-ui .filter .filter-input {{
        background: var(--fastmvc-surface) !important;
        border: 1px solid var(--fastmvc-border) !important;
        color: var(--fastmvc-text) !important;
    }}
    
    /* Servers */
    .swagger-ui .servers > label select {{
        background: var(--fastmvc-bg) !important;
        border: 1px solid var(--fastmvc-border) !important;
        color: var(--fastmvc-text) !important;
    }}
</style>
"""

# Custom JS for Swagger UI enhancements
SWAGGER_UI_JS = """
<script>
    // FastMVC Swagger UI Enhancements
    (function() {
        'use strict';
        
        // Wait for Swagger UI to load
        function waitForSwaggerUI() {
            if (document.querySelector('.swagger-ui .info')) {
                enhanceSwaggerUI();
            } else {
                setTimeout(waitForSwaggerUI, 100);
            }
        }
        
        function enhanceSwaggerUI() {
            // Add FastMVC badge
            const info = document.querySelector('.swagger-ui .info');
            if (info) {
                const badge = document.createElement('div');
                badge.innerHTML = `
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 0.5rem;
                        background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
                        color: white;
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-size: 0.875rem;
                        font-weight: 500;
                        margin-bottom: 1rem;
                    ">
                        <span>⚡</span>
                        <span>FastMVC API</span>
                    </div>
                `;
                info.insertBefore(badge.firstElementChild, info.firstChild);
            }
            
            // Add copy buttons to code blocks
            document.querySelectorAll('.swagger-ui .curl command').forEach(block => {
                const copyBtn = document.createElement('button');
                copyBtn.textContent = 'Copy';
                copyBtn.style.cssText = `
                    position: absolute;
                    right: 10px;
                    top: 10px;
                    background: #0ea5e9;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                `;
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(block.textContent);
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => copyBtn.textContent = 'Copy', 2000);
                };
                block.style.position = 'relative';
                block.parentElement.appendChild(copyBtn);
            });
        }
        
        // Start waiting
        waitForSwaggerUI();
    })();
</script>
"""


def _merge_html_response(base: HTMLResponse, *extra_parts: str) -> HTMLResponse:
    """Append HTML fragments to a Starlette HTMLResponse (get_*_html now returns Response, not str)."""
    body = base.body
    text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
    for part in extra_parts:
        text += part
    return HTMLResponse(
        content=text,
        status_code=base.status_code,
        media_type=base.media_type,
        headers=dict(base.headers),
    )


def setup_custom_docs(app: FastAPI) -> None:
    """Set up custom FastMVC branded documentation for FastAPI.

    Args:
        app: FastAPI application instance

    """
    # Store original openapi schema
    original_openapi = app.openapi

    def custom_openapi():
        """Generate custom OpenAPI schema with FastMVC branding."""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = original_openapi()

        # Add FastMVC branding
        openapi_schema["info"]["x-logo"] = {
            "url": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E⚡%3C/text%3E%3C/svg%3E",
            "altText": "FastMVC Logo",
        }

        # Add example servers
        openapi_schema["servers"] = [
            {"url": "http://localhost:8000", "description": "Local Development"},
            {"url": "https://api.example.com", "description": "Production"},
        ]

        # Add example requests/responses to paths
        for path_data in openapi_schema.get("paths", {}).values():
            for method_data in path_data.values():
                if isinstance(method_data, dict):
                    # Add x-codeSamples
                    method_data["x-codeSamples"] = [
                        {
                            "lang": "curl",
                            "label": "cURL",
                            "source": f"curl -X {{method}} {{url}}",
                        },
                        {
                            "lang": "Python",
                            "label": "Python (httpx)",
                            "source": "import httpx\n\nasync with httpx.AsyncClient() as client:\n    response = await client.{method}(url)\n    print(response.json())",
                        },
                    ]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Try to serve standalone swagger.html if it exists
    swagger_html_path = Path("static/swagger.html")

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Custom Swagger UI with FastMVC branding."""
        # Use standalone HTML file if available
        if swagger_html_path.exists():
            return HTMLResponse(content=swagger_html_path.read_text())

        # Fallback to embedded Swagger UI
        openapi_url = app.openapi_url or "/openapi.json"
        return _merge_html_response(
            get_swagger_ui_html(
                openapi_url=openapi_url,
                title=f"{app.title} - API Documentation",
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
                swagger_favicon_url="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E⚡%3C/text%3E%3C/svg%3E",
                init_oauth={
                    "clientId": "your-client-id",
                    "clientSecret": "your-client-secret-if-required",
                    "realm": "your-realms",
                    "appName": app.title,
                    "scopeSeparator": " ",
                    "additionalQueryStringParams": {},
                },
            ),
            SWAGGER_UI_CSS,
            SWAGGER_UI_JS,
        )

    # Override ReDoc endpoint
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        """Custom ReDoc with FastMVC branding."""
        openapi_url = app.openapi_url or "/openapi.json"
        return _merge_html_response(
            get_redoc_html(
                openapi_url=openapi_url,
                title=f"{app.title} - ReDoc",
                redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js",
                redoc_favicon_url="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E⚡%3C/text%3E%3C/svg%3E",
            ),
            """
        <style>
            body { background: #0f0f1a !important; }
            .menu-content { background: #1a1a2e !important; }
            .api-content { background: #0f0f1a !important; }
        </style>
        """,
        )

    print("✅ Custom FastMVC API documentation configured")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc:      http://localhost:8000/redoc")


def add_examples_to_schema(
    app: FastAPI,
    path: str,
    method: str,
    request_example: Optional[dict[str, Any]] = None,
    response_examples: Optional[dict[str, Any]] = None,
) -> None:
    """Add example requests/responses to OpenAPI schema.

    Args:
        app: FastAPI application
        path: API path (e.g., "/items")
        method: HTTP method (e.g., "post")
        request_example: Example request body
        response_examples: Dict of status code -> example

    """
    if not hasattr(app, "openapi_schema") or app.openapi_schema is None:
        app.openapi()

    schema = app.openapi_schema
    if schema is None:
        return
    path_data = schema.get("paths", {}).get(path, {})
    method_data = path_data.get(method.lower(), {})

    # Add request example
    if request_example and "requestBody" in method_data:
        method_data["requestBody"]["content"]["application/json"]["example"] = (
            request_example
        )

    # Add response examples
    if response_examples and "responses" in method_data:
        for status_code, example in response_examples.items():
            if status_code in method_data["responses"]:
                method_data["responses"][status_code]["content"]["application/json"][
                    "example"
                ] = example

    app.openapi_schema = schema


# Example usage documentation
EXAMPLE_REQUESTS = {
    "create_item": {
        "curl": """curl -X POST http://localhost:8000/items \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "name": "Buy milk",
    "description": "Get from store",
    "completed": false
  }'""",
        "python": """import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/items",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "name": "Buy milk",
            "description": "Get from store",
            "completed": False
        }
    )
    print(response.json())
""",
        "javascript": """fetch('http://localhost:8000/items', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    name: 'Buy milk',
    description: 'Get from store',
    completed: false
  })
})
.then(response => response.json())
.then(data => console.log(data));
""",
    },
    "get_items": {
        "curl": "curl http://localhost:8000/items",
        "python": """import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/items")
    print(response.json())
""",
        "javascript": """fetch('http://localhost:8000/items')
  .then(response => response.json())
  .then(data => console.log(data));
""",
    },
}
