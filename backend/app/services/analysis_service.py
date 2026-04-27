from sqlalchemy.ext.asyncio import AsyncSession
from app.models.case import Case
from app.models.user import User

async def create_analysis_case(db: AsyncSession, user: User, case_type: str, input_summary: str = None) -> Case:
    new_case = Case(
        user_id=user.id,
        case_type=case_type,
        input_summary=input_summary,
        status="pending"
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    return new_case
