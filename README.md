## Social Media Scrap API

A FastAPI service that fetches the latest posts and channel info from multiple social media platforms (YouTube, Twitter/X, Instagram-ready). The project uses `uv` to manage Python versions and dependencies.

### Requirements
- **Python**: >= 3.10 (managed via `uv`)
- **uv**: modern Python package and environment manager

Install `uv` (pick one):

```bash
# via curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# via pipx
pipx install uv

# or via pip (user install)
python -m pip install --user uv
```

### Quick start
```bash
# Install dependencies from pyproject.toml
uv sync

# Run the API (hot-reload if developing)
uv run main.py
```

Then open:
- Swagger UI: `http://localhost:8000/docs`
- API info: `http://localhost:8000/api`
- Health: `http://localhost:8000/api/v1/health`

### Configuration
All configuration is read from environment variables (loaded from `.env` if present).

Create a `.env` file in the project root as needed:

```bash
# App
DEBUG=false

# CORS
# Example: ["http://localhost:3000"] or ["*"]
CORS_ORIGINS=["*"]

# YouTube API
YOUTUBE_API_KEY=

# Twitter/X API (use either bearer-only or full user context)
TWITTER_BEARER_TOKEN=
```

Defaults and more details are in `config/settings.py`.

### Available endpoints
- **Root**: `/` → redirects to docs
- **API info**: `/api`
- **Health**: `/api/v1/health`
- **Channel info**: `/api/v1/channels/{platform}/{channel_identifier}`
- **Latest post**: `/api/v1/posts/{platform}/{channel_identifier}/latest`
- **Latest posts (batch)**: `/api/v1/posts/latest/batch`

Supported platforms depend on configured services. See `services/` and `adapters/` for current support.

#### Examples
```bash
# Health
curl http://localhost:8000/api/v1/health

# Channel info (examples)
curl http://localhost:8000/api/v1/channels/youtube/UC_x5XG1OV2P6uZZ5FSM9Ttw
curl http://localhost:8000/api/v1/channels/twitter/elonmusk

# Latest post (single)
curl http://localhost:8000/api/v1/posts/youtube/UC_x5XG1OV2P6uZZ5FSM9Ttw/latest
```

### Development
- Run locally: `uv run main.py`
- Lint/type-check: add your preferred tools to `pyproject.toml` and run via `uv run <tool>`

### Deployment
- This project uses `uv` for dependency and Python management during development.
- For Vercel, `requirements.txt` exists **only** for deployment because Vercel does not yet support `uv` directly.
- Vercel configuration lives in `vercel.json`, which points to `main.py`.

If deploying elsewhere, prefer building from `pyproject.toml` using `uv` or a modern PEP 621/PEP 517 workflow.

### Project structure (high-level)
```
api/            # FastAPI routers, dependencies, middleware, response models
adapters/       # Platform-specific adapters (YouTube, Twitter, etc.)
services/       # Business logic/services per platform
core/           # Domain models and base abstractions
config/         # Settings via pydantic-settings
utils/          # Helpers (e.g., HTTP client)
main.py         # FastAPI app entrypoint
pyproject.toml  # Project metadata and dependencies (authoritative)
requirements.txt# For Vercel deployment only
```

### Architecture overview
- **Domain models (`core/`)**: Shared abstractions and models.
  - `core/base.py`: `BaseSocialMediaService` defines the contract: `get_latest_post`, `get_channel_info`, `validate_credentials`, and `_get_platform_name` returning a `Platform`.
  - `core/models.py`: `Platform` enum and Pydantic models `SocialMediaPost`, `ChannelInfo` (unified response shapes).
- **Services (`services/`)**: Concrete platform implementations that extend `BaseSocialMediaService` (e.g., `YouTubeService`, `TwitterService`). They translate platform APIs into unified models.
- **Adapters (`adapters/`)**: Thin wrappers to construct and expose a `.service` instance for registration.
- **Orchestrator (`services/fetcher_service.py`)**: `SocialMediaFetcher` registers available services and exposes async APIs to fetch posts/channel info. It runs service calls in a thread pool and aggregates results for batch requests.
- **API layer (`api/`)**: FastAPI routers (`/health`, `/channels`, `/posts`), dependencies (`FetcherDep`, `validate_platform`), response models, and middleware.
- **Settings (`config/settings.py`)**: Centralized configuration using environment variables and `.env`.

This split keeps platform-specific concerns isolated in services while exposing a stable, unified API surface.

### Add a new platform service
1) **Create the service** in `services/`, extending `BaseSocialMediaService`:

```python
# services/instagram_service.py
from core.base import BaseSocialMediaService
from core.models import Platform, SocialMediaPost, ChannelInfo

class InstagramService(BaseSocialMediaService):
    def _get_platform_name(self) -> Platform:
        return Platform.INSTAGRAM

    def validate_credentials(self) -> bool:
        # perform a lightweight API call or token check
        return True

    def get_channel_info(self, channel_identifier: str) -> ChannelInfo:
        # call platform API, map to ChannelInfo
        ...

    def get_latest_post(self, channel_identifier: str) -> SocialMediaPost | None:
        # call platform API, map to SocialMediaPost
        ...
```

2) **Add an adapter** in `adapters/` that instantiates your service:

```python
# adapters/instagram_adapter.py
from services.instagram_service import InstagramService
from core.base import BaseSocialMediaService

class InstagramAdapter:
    def __init__(self):
        self._service = InstagramService()

    @property
    def service(self) -> BaseSocialMediaService:
        return self._service
```

3) **Register it** in `services/fetcher_service.py` inside `_register_services`:

```python
from adapters.instagram_adapter import InstagramAdapter
# ...
try:
    instagram_adapter = InstagramAdapter()
    self._services["instagram"] = instagram_adapter.service
except Exception as e:
    print(f"Warning: Instagram service not available: {e}")
```

4) **Expose configuration** in `config/settings.py` (e.g., tokens/keys) and document env vars in this README.

5) If the platform is not already in `core/models.py` → `Platform`, **add a new enum value** and ensure routes accept it via `validate_platform`.

Once registered, the platform automatically works with existing endpoints:
- `/api/v1/channels/{platform}/{channel_identifier}`
- `/api/v1/posts/{platform}/{channel_identifier}/latest`
- `/api/v1/posts/latest/batch`

### Add new API endpoints
1) **Create a router** under `api/routes/`:

```python
# api/routes/example.py
from fastapi import APIRouter, Path
from api.dependencies import FetcherDep, validate_platform

router = APIRouter(prefix="/example", tags=["Example"])

@router.get("/{platform}/{channel}")
async def example(fetcher: FetcherDep, platform: str = Path(...), channel: str = Path(...)):
    p = validate_platform(platform)
    info = await fetcher.get_channel_info(p, channel)
    return {"id": info.id, "name": info.name}
```

2) **Include the router** in `main.py`:

```python
from api.routes import example
app.include_router(example.router, prefix=settings.API_V1_PREFIX)
```

3) If you need custom response models, add them under `api/response_models/` and reference via `response_model=...` in route decorators.

4) For validation of inputs beyond `validate_platform`, prefer Pydantic models in request bodies and `Path/Query` params with `fastapi` validators.

### Testing your additions
- Call `/api/v1/health` to verify your new platform appears in `available_platforms`.
- Use `/docs` to interactively try your new endpoints.

### Notes
- Python version is enforced by `pyproject.toml` (`requires-python >=3.10`). Use `uv python install/pin` to control the runtime.
- When adding dependencies, update `pyproject.toml` and run `uv sync`. Do not manually edit `requirements.txt`; it is a deployment artifact.

