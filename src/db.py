# Функция для инициализации базы данных
async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS CARS (
                CAR_ID SERIAL PRIMARY KEY,
                BRAND TEXT NOT NULL,
                MODEL TEXT NOT NULL,
                YEAR_RELEASED INT not null,
                COLOR TEXT NOT NULL,
                LICENSE_PLATE TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS USERS (                
	            USER_ID BIGINT UNIQUE PRIMARY KEY,
	            USER_NAME text,
 	            CAR_ID BIGINT NULL,
                CONSTRAINT FK_CARS FOREIGN KEY (CAR_ID) REFERENCES CARS (CAR_ID) ON DELETE SET NULL
            );
        """
        )
        print("Database tables created (if not exist).")
