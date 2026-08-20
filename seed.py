# Generates sample products for each category with realistic dynamic attributes. 

import asyncio
from database import AsyncSessionFactory
from models import User, Item, Payment, ItemCondition, ItemCategory, PaymentMode
from faker import Faker
from sqlalchemy import select
import random

fake = Faker()

def generate_sample_specs(category: ItemCategory):
    if category == ItemCategory.BOOK:
        return {
            "author": fake.name(),
            "genre": random.choice(["Fiction", "Sci-Fi", "Biography", "Technology"]),
            "pages": random.randint(150, 900),
            "isbn": fake.isbn13()
        }
    elif category == ItemCategory.PHONE:
        return {
            "brand": random.choice(["Apple", "Samsung", "Google", "OnePlus"]),
            "ram": random.choice(["8GB", "12GB", "16GB"]),
            "storage": random.choice(["128GB", "256GB", "512GB"]),
            "screen_size": f"{random.uniform(6.1, 6.8):.1f} inches"
        }
    elif category == ItemCategory.TOY:
        return {
            "age_group": random.choice(["3-5 yrs", "6-8 yrs", "9-12 yrs", "13+ yrs"]),
            "material": random.choice(["Plastic", "Wood", "Fabric"]),
            "battery_required": random.choice([True, False])
        }
    elif category == ItemCategory.COSMETIC:
        return {
            "brand": random.choice(["L'Oreal", "Sephora", "Nivea", "MAC"]),
            "skin_type": random.choice(["All", "Oily", "Dry", "Sensitive"]),
            "volume_ml": random.choice([50, 100, 200, 250]),
            "cruelty_free": True
        }

async def seed_data():
    """Idempotent seeding: checks for existing records before inserting.

    This function uses deterministic, repeatable keys so re-running will not
    create duplicate users/items/payments.
    """
    async with AsyncSessionFactory() as db:
        users = []
        # deterministic users so repeated runs are idempotent
        for i in range(12):
            email = f"seed_user_{i}@example.com"
            res = await db.execute(select(User).filter_by(email=email))
            user = res.scalars().first()
            if not user:
                user = User(
                    username=f"Seed User {i}",
                    email=email,
                    contact_no=f"10000000{i:03}"[:15],
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=65),
                    company_name=fake.company(),
                    department=fake.job(),
                    city=fake.city(),
                    state=fake.state(),
                    pincode=fake.postcode()
                )
                db.add(user)
                await db.flush()
            users.append(user)

        categories = list(ItemCategory)
        items = []
        # deterministic item names to avoid duplicates across runs
        for i in range(16):
            cat = categories[i % len(categories)]
            item_name = f"{cat.value.capitalize()} - seed_item_{i}"
            res = await db.execute(select(Item).filter_by(item_name=item_name, category=cat))
            item = res.scalars().first()
            if not item:
                item = Item(
                    item_name=item_name,
                    category=cat,
                    price=round(random.uniform(15, 1200), 2),
                    loan_available=(cat == ItemCategory.PHONE and random.choice([True, False])),
                    condition=random.choice([ItemCondition.NEW, ItemCondition.RESALE]),
                    specifications=generate_sample_specs(cat)
                )
                db.add(item)
                await db.flush()
            items.append(item)

        # create one payment per user if it doesn't already exist
        for idx, user in enumerate(users):
            selected_item = items[idx % len(items)]
            res = await db.execute(select(Payment).filter_by(user_id=user.id, item_id=selected_item.id))
            existing_payment = res.scalars().first()
            if not existing_payment:
                payment = Payment(
                    user_id=user.id,
                    item_id=selected_item.id,
                    mode_of_payment=random.choice(list(PaymentMode)),
                    total_paid=float(selected_item.price)
                )
                db.add(payment)
                await db.flush()

        await db.commit()
        print("Database seeded (idempotent run).")

if __name__ == "__main__":
    asyncio.run(seed_data())