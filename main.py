from fastapi import FastAPI, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database import engine, Base, get_db_session
import models, schema

app = FastAPI(title="Enterprise E-Commerce Backend")

# comment: The code defines a FastAPI application with endpoints for creating users, items, and payments, as well as an analytics summary endpoint. It uses SQLAlchemy for database interactions and includes asynchronous session management. The analytics endpoint retrieves payment data along with related user and item information, returning it in a structured format for dashboard visualization.
@app.get("/")
async def home():
    return {"message": "hello"}


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- INSERT ENDPOINTS ---
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db_session)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    return {"message": "User created", "id": db_user.id}

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: schema.ItemCreate, db: AsyncSession = Depends(get_db_session)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    return {"message": "Item created", "id": db_item.id}

@app.post("/payments/", status_code=status.HTTP_201_CREATED)
async def create_payment(payment: schema.PaymentCreate, db: AsyncSession = Depends(get_db_session)):
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    return {"message": "Payment recorded", "id": db_payment.id}

# --- READ ENDPOINTS FOR DASHBOARD ---
@app.get("/analytics/summary")
async def get_analytics(db: AsyncSession = Depends(get_db_session)):
    stmt = select(models.Payment).options(
        joinedload(models.Payment.user),
        joinedload(models.Payment.item)
    )
    result = await db.execute(stmt)
    payments = result.scalars().all()
    
    return [
        {
            "payment_id": p.id,
            "user_name": p.user.username,
            "city": p.user.city,
            "item_name": p.item.item_name,
            "category": p.item.category.value,
            "specifications": p.item.specifications,
            "item_price": float(p.item.price),
            "payment_mode": p.mode_of_payment.value,
            "total_paid": float(p.total_paid),
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for p in payments
    ]