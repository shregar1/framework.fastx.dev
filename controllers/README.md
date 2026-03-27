# Controllers

## What this module does

The **`controllers`** package is the **HTTP / presentation layer** of the FastMVC application. It receives validated requests, coordinates work by calling **services** and **repositories**, and returns standardized **response DTOs**. Controllers should stay thin: no business rules that belong in the domain, and no raw SQL or persistence details.

This tree mirrors how you organize features—by area (`apis`, `auth`, …) and optional versioning—so that each controller class maps clearly to a use case or route family.

## Responsibilities

| Concern | Handled here |
|--------|----------------|
| Request context | URN, user identity, API name (via framework `IController` / app bases) |
| Orchestration | Call services, pass DTOs, map results to responses |
| Validation entrypoint | Often `validate_request` or equivalent before handler logic |
| HTTP semantics | Status codes and response shapes delegated to DTOs / helpers |

## Layout (conceptual)

```
controllers/
├── abstraction.py          # App-level controller base (extends framework IController)
├── apis/                   # REST-style API controllers (nested by version / area)
│   └── v1/
│       ├── item/           # Sample Item CRUD (item_controller.py)
│       └── example/        # Thin DTO demo (abstraction.py, create.py, …)
├── auth/                   # Authentication-related controllers
└── router.py               # Example router wiring (if present)
```

## How it fits in the stack

```
HTTP → Middleware → Router → Controller → Service → Repository → Database
```

Controllers depend on **abstractions** (`IController`) and **DTOs** for input/output. They obtain **services** and **dependencies** via FastAPI `Depends()` from the **`dependencies`** package.

## Related documentation

- `abstractions/README.md` — `IController` and patterns  
- `dependencies/README.md` — injecting DB, services, utilities  
- `dtos/README.md` — request/response models  

## Practices

1. Keep controllers **stateless** per request except for context set during validation.  
2. **Delegate** business logic to `services/`.  
3. **Return** typed response DTOs (or `JSONResponse` helpers) consistently.  
4. Use **layered abstractions** under `controllers/apis/...` to match API versioning and domains.
