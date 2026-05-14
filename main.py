from fastapi import FastAPI
from routes import auth, services, tenants, user, clientes, slots, agendamentos, workschedules


app = FastAPI(title="Barbearia API", version="0.1.0")

app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(user.router)
app.include_router(clientes.router)
app.include_router(services.router)
app.include_router(slots.router)
app.include_router(agendamentos.router)
app.include_router(workschedules.router)

@app.get("/")
def root():
    return {"status": "ok"}

# poetry run uvicorn main:app --reload