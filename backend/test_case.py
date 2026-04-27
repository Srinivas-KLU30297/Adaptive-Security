import asyncio
from app.db.database import async_session
from sqlalchemy import text

async def test():
    async with async_session() as s:
        res = await s.execute(text('SELECT id, user_id FROM cases ORDER BY created_at DESC LIMIT 1'))
        row = res.fetchone()
        if row:
            print(f"CASE_ID: {row[0]}")

asyncio.run(test())
