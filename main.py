from fastapi import FastAPI
from routes import (
    appointment, 
    auth, 
    services, 
    user_service,
    tenants, 
    user, 
    clientes, 
    slots, 
    workschedules
    )


app = FastAPI(title="Barbearia API", version="0.1.0")

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
def root():
    return {"status": "ok"}

# poetry run uvicorn main:app --reload