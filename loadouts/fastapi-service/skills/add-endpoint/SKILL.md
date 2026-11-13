---
name: add-endpoint
description: Add a FastAPI endpoint with typed request and response models, an Annotated dependency and tests for success and failure. Use when adding or changing a route.
---

# Add an endpoint

1. Read `app/main.py` and the router for the resource. If there is no router yet, start from `references/items.py`.
2. Define models: a `Create` model for input and a `Public` model for output. Output models never include secrets or
   internal fields.
3. Write the route with a return annotation, the right status code (`status_code=201` for creation) and dependencies via
   `Annotated[..., Depends(...)]`. Plain `def` if it calls blocking code.
4. Raise `HTTPException(status_code=404, ...)` for missing items. Let FastAPI return 422 for invalid input.
5. Include the router in `app/main.py` if new: `app.include_router(items.router)`.
6. Tests, following `references/test_items.py`: success, 404, 422, and a dependency override instead of real storage.
7. Run `uv run pytest -q`, `uv run ruff check .` and `uv run ruff format --check .`. Report the results.
