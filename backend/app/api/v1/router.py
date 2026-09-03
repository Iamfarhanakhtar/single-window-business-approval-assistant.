"""Aggregated API Router for v1"""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.businesses import router as businesses_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.applications import router as applications_router
from app.api.v1.documents import router as documents_router
from app.api.v1.inspections import router as inspections_router
from app.api.v1.queries import router as queries_router
from app.api.v1.renewals import router as renewals_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.ai_routes import router as ai_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(businesses_router)
api_v1_router.include_router(approvals_router)
api_v1_router.include_router(applications_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(inspections_router)
api_v1_router.include_router(queries_router)
api_v1_router.include_router(renewals_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ai_router)
