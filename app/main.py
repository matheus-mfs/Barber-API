from fastapi import FastAPI

from app.routes import (
    appointment,
    auth,
    clientes,
    services,
    slots,
    tenants,
    user,
    user_service,
    workschedules,
)
from app.services.slot_service import close_expired_slots, generate_daily_slots
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

from app.services.whatsapp_service import send_reminders

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        generate_daily_slots,
        "cron",
        hour=4,
        minute=5
    )
    scheduler.add_job(
        close_expired_slots,
        "interval",
        minutes=5
    )
    scheduler.add_job(
        send_reminders,
        "interval",
        minutes=1
    )

    scheduler.start()
    
    yield
    
    scheduler.shutdown()

app: FastAPI = FastAPI(title="Barbearia API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(user.router)
app.include_router(workschedules.router)
app.include_router(clientes.router)
app.include_router(services.router)
app.include_router(user_service.router)
app.include_router(slots.router)
app.include_router(appointment.router)


@app.get("/")
def home() -> dict:
    """Endpoint de health check."""
    return {"status": "ok"}