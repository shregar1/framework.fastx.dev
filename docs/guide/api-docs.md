# API Documentation

FastMVC provides beautiful, branded API documentation with a dark theme by default.

## Swagger UI

FastMVC includes a custom Swagger UI with FastMVC branding:

### Dark Theme

The Swagger UI uses a custom dark theme with the following color scheme:

- **Primary Color**: Cyan (`#0ea5e9`)
- **Accent Color**: Fuchsia (`#d946ef`)
- **Background**: Dark slate (`#0f0f1a`)

### Features

- 🎨 FastMVC-branded dark theme
- 🔍 Code syntax highlighting
- 📋 Copy buttons for code samples
- 🌍 Example requests in multiple languages
- 🔧 Interactive "Try It Out" feature

### Accessing Swagger UI

Once your server is running, visit:

```
http://localhost:8000/docs
```

## ReDoc

FastMVC also provides a ReDoc interface for API documentation:

```
http://localhost:8000/redoc
```

ReDoc offers:
- Clean, three-pane layout
- Search functionality
- Grouped endpoints
- Schema exploration

## Customization

### Modifying the Theme

Edit `static/swagger.html` to customize:

```html
<style>
  :root {
    --fastmvc-primary: #your-primary-color;
    --fastmvc-accent: #your-accent-color;
  }
</style>
```

### Adding Examples

Add example responses to your endpoints:

```python
from fastapi import FastAPI
from pydantic import IModel

class Item(IModel):
    name: str
    price: float

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """
    Get an item by ID.
    
    Example response:
    ```json
    {
        "name": "Sample Item",
        "price": 29.99
    }
    ```
    """
    return Item(name="Sample Item", price=29.99)
```

## OpenAPI Schema

The raw OpenAPI schema is available at:

```
http://localhost:8000/openapi.json
```

Use this schema to:
- Generate client SDKs
- Import into API testing tools
- Create custom documentation

## MkDocs Documentation

For comprehensive documentation, FastMVC includes MkDocs with Material theme:

### Commands

```bash
# Install documentation dependencies
make docs-install

# Serve documentation locally
make docs-serve

# Build static documentation
make docs-build

# Deploy to GitHub Pages
make docs-deploy
```

### Features

- Dark mode by default
- Automatic API reference generation
- Search functionality
- Code copy buttons
- Responsive design
