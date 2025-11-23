import aiosqlite

class Database:
    def __init__(self, db_file: str = 'auvk6_bot.db'):
        self.db_file = db_file


    async def init_db(self):
        async with aiosqlite.connect(self.db_file) as db:      # создаем бд
            await db.execute('''
            CREATE TABLE IF NOT EXISTS MESSAGES (               
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NULL,
            username TEXT NULL,
            message TEXT NOT NULL,
            is_anon BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            await db.execute('''
            CREATE TABLE IF NOT EXISTS USERS (
            user_id INTEGER PRIMARY KEY NULL,
            username TEXT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            await db.commit()
        print('db initialized')


    async def add_user(self, user_id: int, username: str):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute('''
            INSERT INTO users(user_id, username) VALUES(?, ?)
            ON CONFLICT(user_id)DO UPDATE SET
            username = excluded.username;
            ''', (user_id, username))

            await db.commit()


    async def add_message(self, user_id: int, username: str,
                          message: str, is_anon: bool):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute('''
                INSERT INTO MESSAGES (user_id, username, message, is_anon)
                VALUES (?, ?, ?, ?)''',
                (user_id, username, message, is_anon))
            await db.commit()
        return cursor.lastrowid


    async def get_all_messages(self, limit: int = 100):
        async with aiosqlite.connect(self.db_file) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
            SELECT * FROM MESSAGES
            ORDER BY created_at DESC
            LIMIT ?''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


    async def get_users(self, limit: int = 100):
        async with aiosqlite.connect(self.db_file) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
            SELECT * FROM USERS
            ORDER BY user_id
            LIMIT ?''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


    async def get_stats(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT COUNT(*) FROM MESSAGES") as cursor:
                total_messages = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM MESSAGES WHERE is_anon=1") as cursor:
                anon_messages = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM USERS") as cursor:
                total_users = (await cursor.fetchone())[0]

            return dict(total_messages=total_messages,
                        anon_messages=anon_messages,
                        total_users=total_users)












