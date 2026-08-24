from fastapi import APIRouter
from app.api import (
    users, candidates, workers, partners, payments, tasks, 
    trainings, reports, notifications, messages, audit_logs, search, comments, materials, sources, files
)

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(trainings.router, prefix="/trainings", tags=["trainings"])
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
