from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.v1.router import api_router
from app.application.exceptions import ApplicationError
from app.core.config.settings import settings
from app.core.database.base import Base
from app.core.database.session import SessionLocal, engine
from app.core.exceptions.handlers import application_error_handler, domain_error_handler
from app.core.middlewares.request_id import RequestIdMiddleware
from app.core.middlewares.tenant import TenantMiddleware
from app.domain.shared.exceptions import DomainError
from app.infra.models.models import TenantModel
from app.infra.repositories.tenant_repository import seed_default_tenant
from app.infra.repositories.user_repository import seed_default_roles


async def resolve_tenant(slug: str) -> tuple | None:
    async with SessionLocal() as session:
        result = await session.execute(select(TenantModel).where(TenantModel.slug == slug.lower()))
        model = result.scalar_one_or_none()
        if model:
            return model.id, model.slug
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        await seed_default_roles(session)
        await seed_default_tenant(session)
        await session.commit()
    app.state.tenant_resolver = resolve_tenant
    yield
    await engine.dispose()


app = FastAPI(
    title="E-commerce Whitelabel API",
    description="API REST — Clean Architecture + DDD — Fase 2",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(TenantMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(ApplicationError, application_error_handler)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "phase": "2"}
