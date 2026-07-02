"""
Application entrypoint.

Uses the app-factory pattern (`create_app()`) rather than a module-level
`app = FastAPI()` so tests can spin up isolated instances with overridden
settings/dependencies.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import get_settings
from backend.core.exceptions import register_exception_handlers
from backend.core.logging import setup_logging

# --- Stage 1.3+ will add module routers here, e.g.: ---
# from backend.modules.auth.router import router as auth_router
# from backend.modules.users.router import router as users_router


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings)

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # --- Stage 1.3+: include_router calls go here ---
    # app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
    # app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Liveness check — used by Docker healthcheck and uptime monitoring."""
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    logging.getLogger(__name__).info("%s started in %s mode", settings.APP_NAME, settings.ENVIRONMENT)
    return app


app = create_app()