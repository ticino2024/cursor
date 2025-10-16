"""Initialize database with sample data."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.user import User, UserRole


async def init_database():
    """Initialize database with tables and sample data."""
    print("Initializing database...")

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin user exists
        from sqlalchemy import select

        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        existing_admin = result.scalar_one_or_none()

        if not existing_admin:
            # Create admin user
            admin_user = User(
                email="admin@example.com",
                name="Admin User",
                password_hash=get_password_hash("Admin123!@#"),
                role=UserRole.ADMIN,
                email_verified=True,
            )
            session.add(admin_user)

            # Create sample regular user
            regular_user = User(
                email="user@example.com",
                name="Regular User",
                password_hash=get_password_hash("User123!@#"),
                role=UserRole.USER,
                email_verified=True,
            )
            session.add(regular_user)

            # Create sample moderator
            moderator_user = User(
                email="moderator@example.com",
                name="Moderator User",
                password_hash=get_password_hash("Mod123!@#"),
                role=UserRole.MODERATOR,
                email_verified=True,
            )
            session.add(moderator_user)

            await session.commit()

            print("\nSample users created:")
            print("  Admin:     admin@example.com / Admin123!@#")
            print("  User:      user@example.com / User123!@#")
            print("  Moderator: moderator@example.com / Mod123!@#")
        else:
            print("\nAdmin user already exists, skipping sample data creation.")

    await engine.dispose()
    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
