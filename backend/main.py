from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from config import engine, async_session
from models.db_models import Base
from repositories.account_repo import AccountRepository
from api.endpoints import account, orders, price

app = FastAPI(title="Crypto Trading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(account.router)
app.include_router(orders.router)
app.include_router(price.router)

@app.on_event("startup")
async def startup():
    # Create PostgreSQL tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize account if it doesn't exist
    async with async_session() as session:
        account_repo = AccountRepository(session)
        account = await account_repo.get_account()
        if not account:
            await account_repo.create_account()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
