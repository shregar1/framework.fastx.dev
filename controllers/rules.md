# Controller Rules

Controllers are thin HTTP adapters. Keep business logic out of them.

## Structure

1. **Extend the right abstraction** — user routes extend `IUserController`, auth routes `IAuthController`, v1 APIs `IExampleAPIController` (or similar), everything ultimately chains to `abstractions.controller.IController`.
2. **`__init__` only sets `api_name`** — forward everything else to `super().__init__(..., *args, **kwargs)`. Never shadow `_urn`, `_user_id`, etc. — the parent setters already handle it.
3. **One handler per file** — `post` / `get` / `put` / `delete`. No private helpers that contain business rules — push those into a service.

## Handler Body (mandatory order)

```python
async def post(self, request: Request, request_payload: XxxDTO,
               session: Session = Depends(DBDependency.derive),
               service_factory: Callable = Depends(XxxServiceDependency.derive),
               dictionary_utility: DictionaryUtility = Depends(DictionaryUtilityDependency.derive),
               ...):
    try:
        self.bind_request_context(request, dictionary_utility_factory=dictionary_utility)
        # instantiate repos with session
        # await self.validate_request(...)
        response_dto = await service_factory(
            urn=self.urn, user_urn=self.user_urn, api_name=self.api_name,
            user_id=self.user_id, ...,
        ).run(request_dto=request_payload)
        http_status = HTTPStatus.OK
    except Exception as err:
        response_dto, http_status = self.handle_exception(
            err, request, event_name="x.y", session=session,
            force_http_ok=False, fallback_message="...",
        )

    content = (
        self.dictionary_utility.convert_dict_keys_to_camel_case(response_dto.model_dump())
        if self.dictionary_utility is not None
        else response_dto.model_dump()
    )
    return JSONResponse(content=content, status_code=http_status)
```

## Do

- Use `bind_request_context(request, ...)` at the top of every handler — don't re-implement the URN/user_id/logger lifting.
- Use `handle_exception(...)` for the `except Exception` branch — never format error envelopes inline.
- Get services and repositories via `Depends(XxxDependency.derive)` factories — never instantiate directly.
- Apply `convert_dict_keys_to_camel_case` to the response body before returning.
- Pass `force_http_ok=False` on new-style endpoints; legacy auth endpoints may set `True` for contract compatibility.
- Wrap side-effects (audit, webhook, welcome email) in `try/except` with a warning log — they must never break the success path.

## Don't

- Don't do SQLAlchemy queries in a controller — go through a repository.
- Don't raise `HTTPException` — raise typed errors from `fast_platform.errors` and let `handle_exception` translate them.
- Don't construct `BaseResponseDTO` in the happy path — that's the service's job.
- Don't create private methods on the controller that touch the DB session.
- Don't pass `self.user_id or ""` — `user_id` is `int | None`; let `None` flow through.
- Don't add response-field renaming logic — if the DTO key is wrong, fix the DTO.
- Don't catch narrow exceptions to return inline envelopes — one `except Exception` + `handle_exception` is the pattern.

## File Layout Convention

```
controllers/
  <domain>/               # e.g. auth, apis/v1
    abstraction.py        # IXxxController, extends parent abstraction
    <resource>/
      abstraction.py      # optional nested base
      <action>.py         # one handler class per file
```
