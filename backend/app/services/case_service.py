from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.case import Case
from app.models.user import User

async def get_cases(db: AsyncSession, user: User, page: int = 1, size: int = 20):
    from sqlalchemy.orm import selectinload
    
    query = select(Case).options(selectinload(Case.modality_results)).order_by(desc(Case.created_at))
    
    if user.role != "admin":
        query = query.where(Case.user_id == user.id)
        
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    # Count total
    from sqlalchemy import func
    count_query = select(func.count()).select_from(Case)
    if user.role != "admin":
        count_query = count_query.where(Case.user_id == user.id)
    total = await db.scalar(count_query)
    
    return cases, total

async def get_case_by_id(db: AsyncSession, case_id: str):
    import uuid
    from sqlalchemy.orm import selectinload
    try:
        case_uuid = uuid.UUID(str(case_id))
    except ValueError:
        return None
        
    query = select(Case).options(selectinload(Case.modality_results)).where(Case.id == case_uuid)
    result = await db.execute(query)
    return result.scalars().first()
