#!/usr/bin/env python3
"""
Script to set up the database tables for Restaurant Orders.
Run this script to create the necessary tables in PostgreSQL.
"""

import asyncio
import asyncpg
import bcrypt
from app.config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def setup_database():
    """Create database tables and test user"""
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user="postgres",
            password="Giu72656770",
            database="quebarbaro",
            host="192.168.18.91",
            port=5432
        )

        # Read and execute schema
        with open("database/auth_schema.sql", "r") as f:
            schema_sql = f.read()

        # Execute schema
        await conn.execute(schema_sql)

        # Add role column to existing users table if it doesn't exist
        try:
            # Check if role column exists
            result = await conn.fetchval("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            """)

            if not result:
                print("Adding role column to users table...")
                await conn.execute("""
                    ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'ventas'
                """)
                print("✅ Role column added to users table")
            else:
                print("✅ Role column already exists in users table")

        except Exception as e:
            print(f"Warning checking/adding role column: {e}")

        print("✅ Database tables created successfully!")

        # Create test users with different roles
        users_to_create = [
            {
                "username": "admin",
                "password": "admin123",
                "email": "admin@restaurant.com",
                "role": "admin"
            },
            {
                "username": "repartidor1",
                "password": "repartidor123",
                "email": "repartidor@restaurant.com",
                "role": "repartidor"
            },
            {
                "username": "ventas1",
                "password": "ventas123",
                "email": "ventas@restaurant.com",
                "role": "ventas"
            },
            {
                "username": "quebarbaro",
                "password": "20614301172",
                "email": "quebarbaro@restaurant.com",
                "role": "admin"
            }
        ]

        for user_data in users_to_create:
            password_hash = hash_password(user_data["password"])

            # Insert or update user
            await conn.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, is_verified)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (username) DO UPDATE SET
                    email = EXCLUDED.email,
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role,
                    is_active = EXCLUDED.is_active,
                    is_verified = EXCLUDED.is_verified
            """, user_data["username"], user_data["email"], password_hash, user_data["role"], True, True)

            print("✅ User created/updated successfully!")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print()

        # Close connection
        await conn.close()

    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Setting up Restaurant Orders database...")
    success = asyncio.run(setup_database())
    if success:
        print("Database setup complete!")
    else:
        print("Database setup failed!")