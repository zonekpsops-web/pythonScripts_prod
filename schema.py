from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, Dict, Any
from models import ItemCondition, ItemCategory, PaymentMode

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    contact_no: str
    date_of_birth: date
    company_name: Optional[str] = None
    department: Optional[str] = None
    city: str
    state: str
    pincode: str

class ItemCreate(BaseModel):
    item_name: str
    category: ItemCategory
    price: float
    loan_available: bool
    condition: ItemCondition
    specifications: Dict[str, Any] = Field(
        default_factory=dict, 
        example={"ram": "16GB", "storage": "512GB"}
    )

class PaymentCreate(BaseModel):
    user_id: str
    item_id: str
    mode_of_payment: PaymentMode
    down_payment: float = 0.0
    loan_amount: float = 0.0
    total_paid: float