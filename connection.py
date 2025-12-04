import asyncpg
import os
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector

load_dotenv()

# قراءة بيانات الاتصال من env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "ai_agent")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

_pool = None


async def get_pool():
    """
    إرجاع singleton pool واحد بس لكل المشروع.
    """
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            min_size=1,
            max_size=5,
        )
        print("🟢 PostgreSQL pool initialized")
        async with _pool.acquire() as conn:
            await register_vector(conn)

    return _pool




async def get_connection():
    """
    لو محتاج تستخدم conn مباشرة بدون pool (نادرًا).
    """
    pool = await get_pool()
    return await pool.acquire()
