import pymysql
from pymysql import Error

host_name = "localhost"
user_name = "root" 
user_password = "abc123"
db_name = "army_mess"
timeout = 10

def set_database():
    try:
        print("Starting connection...")
        # First connect without specifying database
        connection = pymysql.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            port=3306,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to MySQL server")

        # Create database if not exists
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created/verified")
            cursor.execute(f"USE {db_name}")
            print(f"Using database '{db_name}'")

        # Now reconnect specifically to our database
        connection.close()
        connection = pymysql.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            db=db_name,
            port=3306,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"Reconnected to database '{db_name}'")

        # Create tables
        with connection.cursor() as cursor:
            # OFFICERS table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS OFFICERS (
                    UID VARCHAR(50) PRIMARY KEY NOT NULL,
                    NAME VARCHAR(100) NOT NULL,
                    OFFICER_RANK VARCHAR(100),
                    UNIT VARCHAR(100),
                    IS_MESS_MEMBER BOOLEAN,
                    IS_MARRIED BOOLEAN,
                    ACCOMODATION_AVAILED BOOLEAN,
                    IS_GUEST BOOLEAN
                )
            """)
            print("OFFICERS table created")

            # FIXED_CHARGES table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS FIXED_CHARGES (
                    SUB_NAME VARCHAR(50) PRIMARY KEY NOT NULL,
                    RANK_1 FLOAT NOT NULL,
                    RANK_2 FLOAT NOT NULL,
                    RANK_3 FLOAT NOT NULL,
                    RANK_4 FLOAT NOT NULL
                )
            """)
            print("FIXED_CHARGES table created")

            # Insert default charges
            fixed_charges = [
                ("Accomodation", 200, 200, 200, 200),
                ("Spouse Memento Fund", 200, 200, 200, 200)
            ]
            for charge in fixed_charges:
                cursor.execute(
                    "INSERT IGNORE INTO FIXED_CHARGES VALUES (%s, %s, %s, %s, %s)",
                    charge
                )
            print("Default charges inserted")

            # TOTAL_CHARGES table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TOTAL_CHARGES (
                    UID VARCHAR(50) NOT NULL,
                    DESCRIPTION VARCHAR(500),
                    AMOUNT FLOAT NOT NULL,
                    TYPE_OF_CHARGE VARCHAR(200),
                    DATE VARCHAR(20) NOT NULL,
                    REMARKS VARCHAR(200)
                )
            """)
            print("TOTAL_CHARGES table created")

            # CURRENT_SPLIT table
            cursor.execute("""
    CREATE TABLE IF NOT EXISTS CURRENT_SPLIT (
        UID VARCHAR(50) PRIMARY KEY,
        NAME VARCHAR(100),
        AMOUNT FLOAT NOT NULL
    )
""")
            print("CURRENT_SPLIT table created")

            # MESS_LEDGER table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS MESS_LEDGER (
                    TYPE VARCHAR(50),
                    DESCRIPTION VARCHAR(100),
                    REMARKS VARCHAR(200),
                    AMOUNT FLOAT NOT NULL,
                    OFFICER VARCHAR(100),
                    DATE VARCHAR(20) NOT NULL
                )
            """)
            print("MESS_LEDGER table created")

        connection.commit()
        print("All changes committed successfully")

    except Error as e:
        print(f"Database error: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    set_database()