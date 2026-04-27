import asyncio
import logging
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

logger = logging.getLogger(__name__)

async def seed_db():
    async with SessionLocal() as session:
        try:
            # Check if admin user already exists
            query = select(User).where(User.email == "admin@cybershield.ai")
            result = await session.execute(query)
            admin_user = result.scalars().first()

            if not admin_user:
                logger.info("Seeding initial users...")
                
                users_to_create = [
                    User(
                        email="admin@cybershield.ai",
                        hashed_password=hash_password("Admin@123"),
                        full_name="Admin User",
                        role="admin"
                    ),
                    User(
                        email="analyst@cybershield.ai",
                        hashed_password=hash_password("Analyst@123"),
                        full_name="System Analyst",
                        role="analyst"
                    ),
                    User(
                        email="viewer@cybershield.ai",
                        hashed_password=hash_password("Viewer@123"),
                        full_name="Audit Viewer",
                        role="viewer"
                    )
                ]
                
                session.add_all(users_to_create)
                await session.commit()
                logger.info("Seed data insterted successfully.")
            else:
                logger.info("Seed data already present.")
                
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed_db())
