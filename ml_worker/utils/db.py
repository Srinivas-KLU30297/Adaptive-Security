from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path)

db_url = os.getenv("DATABASE_URL", "postgresql://cybershield:cybershield_secret_2024@postgres:5432/cybershield_db")
if "asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "")
if "aiomysql" in db_url:
    db_url = db_url.replace("+aiomysql", "+pymysql")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_case_status(case_id: str, status: str, verdict: str = None, confidence: float = None, risk_level: str = None):
    # Execute raw sql for simplicity in worker context
    from sqlalchemy import text
    with SessionLocal() as session:
        updates = []
        if status: updates.append(f"status = '{status}'")
        if verdict: updates.append(f"verdict = '{verdict}'")
        if confidence is not None: updates.append(f"confidence = {confidence}")
        if risk_level: updates.append(f"risk_level = '{risk_level}'")
        
        if updates:
            sql = f"UPDATE cases SET {', '.join(updates)} WHERE id = '{case_id}'"
            session.execute(text(sql))
            session.commit()

def insert_modality_result(case_id: str, modality: str, verdict: str, confidence: float, xai_data: dict, ms: int):
    from sqlalchemy import text
    with SessionLocal() as session:
        xai_json = json.dumps(xai_data).replace("'", "''")
        sql = f"""
            INSERT INTO modality_results (id, case_id, modality, verdict, confidence, xai_data, processing_time_ms, created_at)
            VALUES (gen_random_uuid(), '{case_id}', '{modality}', '{verdict}', {confidence}, '{xai_json}', {ms}, now())
        """
        session.execute(text(sql))
        session.commit()

def get_case(case_id: str):
    from sqlalchemy import text
    with SessionLocal() as session:
        result = session.execute(text(f"SELECT * FROM cases WHERE id = '{case_id}'")).fetchone()
        if result:
             return dict(result._mapping)
        return None
