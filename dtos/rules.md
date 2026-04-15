# DTO Rules

DTOs are Pydantic models at the edges of the app — they define the **exact** shape of what comes in and what goes out. They are the contract; treat them like one.

## Structure

```
dtos/
  requests/                # inbound payloads (validated by FastAPI)
    <domain>/<action>.py
  responses/
    base.py                # BaseResponseDTO envelope
    <domain>/<resource>_response.py
```

## Do

- **Requests**: declare types strictly. Use `EmailStr`, `constr(min_length=...)`, `Annotated[int, Field(gt=0)]`. Let Pydantic reject invalid input — don't re-validate in the service.
- **Responses**: subclass or compose `BaseResponseDTO` for the envelope; put the actual payload shape in `data`.
- **Field naming**: write snake_case in Python. The controller's `DictionaryUtility.convert_dict_keys_to_camel_case` handles the JSON output transform — don't put `alias="camelCase"` everywhere.
- **Use `model_dump()`** when converting to dict — never `.dict()` (deprecated).
- **Version via directory** — `dtos/requests/v1/...` when a breaking change ships. Don't mutate existing DTOs in place once published.
- Use `Literal[...]` or `Enum` for closed-set fields (`status`, `kind`).

## Don't

- Don't add methods to DTOs — they're data, not behavior. If you need a helper, put it in the service.
- Don't make DTOs inherit from SQLAlchemy models — serialization is the controller's job via the service, and ORM internals leak otherwise.
- Don't use `Any` unless you're carrying opaque forward-compat data — and document why.
- Don't default-coerce (`str | None = ""`). `None` means "missing"; `""` means "empty" — they are different.
- Don't set server-generated fields on request DTOs (`id`, `created_at`, `user_id`). Strip them at the edge.
- Don't reuse a request DTO as a response DTO — inputs and outputs evolve independently.

## BaseResponseDTO

Every controller returns a `BaseResponseDTO`:

```python
BaseResponseDTO(
    transactionUrn=self.urn,
    status=APIStatus.SUCCESS | APIStatus.FAILED,
    responseMessage="human readable",
    responseKey="machine_readable_i18n_key",
    data={...} or [...] or None,
)
```

- `responseKey` is the machine-readable key for i18n — keep it stable; treat renames as breaking.
- `data` is `dict | list | None` — narrow with `isinstance` before accessing keys.

## File Layout

Mirror the service layout so a reviewer can jump from controller → DTO → service without grep.
