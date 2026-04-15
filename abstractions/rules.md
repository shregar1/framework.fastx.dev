# Abstraction Rules

The `abstractions/` tree holds framework-level base classes. Changes here ripple into every controller, service, and repository — edit with caution.

## Do

- Keep abstractions **thin**. A base class earns its place by removing duplication that *already* exists in ≥3 subclasses — not by anticipating it.
- Every `__init__` takes `*args, **kwargs` and forwards to `super().__init__(...)` so the chain through `ContextMixin` stays intact.
- Type context fields consistently: `urn: str | None`, `user_urn: str | None`, `api_name: str | None`, `user_id: int | None`. Don't diverge.
- Keep the base class's public surface documented with a short docstring. Subclasses rely on this as the contract.
- When adding a method to `IController`, ask: does every subclass need it? If not, it belongs in a mixin or a nested interface (`IAuthController`, `IUserController`).

## Don't

- Don't put business logic in an abstraction. Ever. `handle_exception` is framework logic (error-to-envelope mapping). "Check if user is subscribed" is not.
- Don't make abstractions depend on concrete implementations — they should import from `core/`, `constants/`, `dtos/responses/base.py`, and typed errors. That's it.
- Don't re-declare properties that `ContextMixin` already provides (`urn`, `user_urn`, `api_name`, `user_id`, `logger`). Shadowing them causes subtle MRO bugs with `fast_platform.core.utils.context.ContextMixin`.
- Don't break signature compatibility silently. Adding a required param to `IController.__init__` is a breaking change for every subclass.
- Don't import `fastapi` into non-controller abstractions. `IService`, `IRepository`, `IUtility` must stay transport-agnostic.

## Inheritance Map

```
ContextMixin (core.utils.context / fast_platform.core.utils.context)
    │
    ├── IController (abstractions/controller.py)
    │       ├── IAuthController (controllers/auth/abstraction.py)
    │       │       └── IUserController (controllers/auth/user/abstraction.py)
    │       └── JSONAPIController (controllers/apis/json_api_controller.py)
    │
    ├── IService (abstractions/service.py)
    ├── IRepository (abstractions/repository.py)
    └── IUtility (abstractions/utility.py)
```

## The MRO Hazard

`core.utils.context.ContextMixin` and `fast_platform.core.utils.context.ContextMixin` both exist. Whichever one the type checker resolves first wins. If you change the typing of a ContextMixin property locally, update **both** — or the type checker will chase you through every caller.

## Adding a New Abstraction

1. Extend `ContextMixin` (directly or via `ABC, ContextMixin`).
2. Accept `*args, **kwargs` and forward to `super().__init__(...)`.
3. Add a matching dependency factory under `dependencies/.../abstraction.py` if the type will be injected.
4. Update this file's inheritance map.
