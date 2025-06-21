import pymysql
import random
from pymysql import Error
from datetime import datetime

# Central Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'abc123',
    'db': 'army_mess',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 10,
    'read_timeout': 10,
    'write_timeout': 10
}

def get_db_connection():
    """Establish and return a database connection"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Error as e:
        print(f"Connection Error: {e}")
        raise

# ===================== OFFICER MANAGEMENT =====================
# Add these to your existing functions.py file
def get_name_uid_mess_member():
    """Get list of mess members with (uid, name) pairs"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT UID, NAME FROM OFFICERS 
            WHERE IS_MESS_MEMBER = TRUE
            ORDER BY NAME
        """)
        return [list(row.values()) for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching mess members: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_mess_entry():
    """Get all mess ledger entries with proper formatting"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                TYPE as 'Charge Type',
                DESCRIPTION as 'Description',
                AMOUNT as 'Amount',
                DATE as 'Date'
            FROM MESS_LEDGER
            ORDER BY DATE DESC
        """)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries for better handling
        return [dict(row) for row in results]
        
    except Error as err:
        print(f"Error fetching mess entries: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            
def get_total_bill(officer, arrears, month, year):
    """
    Calculate total bill for an officer
    Args:
        officer: Either officer UID or [uid, name] list
        arrears: Arrears amount
        month: Month as string (e.g., "01" for January)
        year: Year as string
    Returns:
        List of bill items with description and amount
    """
    try:
        # Handle both string and list inputs for officer
        if isinstance(officer, list):
            uid = officer[0]
        else:
            uid = officer.split(':')[0].strip() if ':' in officer else officer
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get fixed charges
        cursor.execute("""
            SELECT SUB_NAME, RANK_1, RANK_2, RANK_3, RANK_4 
            FROM FIXED_CHARGES
        """)
        fixed_charges = cursor.fetchall()
        
        # Get officer's rank
        cursor.execute("SELECT OFFICER_RANK FROM OFFICERS WHERE UID = %s", (uid,))
        officer_rank = cursor.fetchone()['OFFICER_RANK'] if cursor.rowcount > 0 else None
        
        # Get monthly charges
        cursor.execute("""
            SELECT DESCRIPTION, AMOUNT 
            FROM TOTAL_CHARGES 
            WHERE UID = %s 
            AND DATE LIKE %s
        """, (uid, f"{year}-{month}-%"))
        monthly_charges = cursor.fetchall()
        
        bill_items = []
        
        # Add fixed charges based on rank
        rank_column = f"RANK_{officer_rank[-1]}" if officer_rank else "RANK_1"
        for item in fixed_charges:
            bill_items.append([
                f"Fixed: {item['SUB_NAME']}",
                float(getattr(item, rank_column, item['RANK_1']))
            ])
        
        # Add monthly charges
        for item in monthly_charges:
            bill_items.append([
                item['DESCRIPTION'],
                float(item['AMOUNT'])
            ])
        
        # Add arrears if applicable
        if float(arrears) > 0:
            bill_items.append([
                "Arrears from previous month",
                float(arrears)
            ])
        
        # Add serial numbers
        for i, item in enumerate(bill_items, 1):
            item.insert(0, str(i))
        
        return bill_items
        
    except Error as err:
        print(f"Error generating bill: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_unit(uid):
    """Get the unit for a given officer UID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT UNIT FROM OFFICERS WHERE UID = %s", (uid,))
        result = cursor.fetchone()
        return result['UNIT'] if result else "Unknown Unit"
    except Error as err:
        print(f"Error fetching unit: {err}")
        return "Unknown Unit"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_name_uid():
    """Get list of officers with (uid, name) pairs"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT UID, NAME 
            FROM OFFICERS 
            WHERE IS_GUEST = FALSE
            ORDER BY NAME
        """)
        return [list(row.values()) for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching name and UID data: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_current_split():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT UID, NAME, AMOUNT FROM CURRENT_SPLIT")
        return [[row['UID'], row['NAME'], row['AMOUNT']] for row in cursor.fetchall()]
    except Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if connection and connection.open:
            connection.close()

def addto_current_split(officer_id, amount):
    """Add an officer to the current split"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get officer name
        cursor.execute("SELECT NAME FROM OFFICERS WHERE UID = %s", (officer_id,))
        result = cursor.fetchone()
        if not result:
            return "Officer not found"
            
        officer_name = result['NAME']
        
        # Add to split
        cursor.execute("""
            INSERT INTO CURRENT_SPLIT (UID, NAME, AMOUNT)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE AMOUNT = %s
        """, (officer_id, officer_name, amount, amount))
        
        connection.commit()
        return f"Added {officer_name} to split with amount {amount}"
    except Error as err:
        connection.rollback()
        return f"Error adding to split: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def empty_current_split():
    """Clear the current split"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE CURRENT_SPLIT")
        connection.commit()
        return "Split cleared successfully"
    except Error as err:
        connection.rollback()
        return f"Error clearing split: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()


def add_officer(uid, officer_name, officer_rank, officer_unit, married, accomodation, mess_member, guest):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if guest:
            uid = "Guest" + str(random.randint(1, 10000))
            query = """INSERT INTO OFFICERS (UID, NAME, IS_GUEST)
                       VALUES (%s, %s, %s)"""
            cursor.execute(query, (uid, officer_name, guest))
        else:
            query = """INSERT INTO OFFICERS (UID, NAME, OFFICER_RANK, UNIT, 
                       IS_MESS_MEMBER, IS_MARRIED, ACCOMODATION_AVAILED, IS_GUEST)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (uid, officer_name, officer_rank, officer_unit, 
                          mess_member, married, accomodation, guest))
            
        connection.commit()
        return "Officer added successfully."
    except Error as err:
        connection.rollback()
        return f"Error adding officer: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_name_rank():
    """Get list of officers with names and ranks"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT NAME, OFFICER_RANK 
            FROM OFFICERS 
            ORDER BY NAME
            LIMIT 50
        """)
        return [list(row.values()) for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching name and rank data: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_all_officer_data():
    """Get complete data for all officers"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM OFFICERS")
        return cursor.fetchall()
    except Error as err:
        print(f"Error fetching all officer data: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_officer_data(uid=None, name=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if uid:
            query = "SELECT * FROM OFFICERS WHERE UID = %s"
            cursor.execute(query, (uid,))
        elif name:
            query = "SELECT * FROM OFFICERS WHERE NAME = %s"
            cursor.execute(query, (name,))
        else:
            return []
        
        return cursor.fetchall()
    except Error as err:
        print(f"Error fetching officer data: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===================== CHARGE MANAGEMENT =====================
def add_charge(charge_type, uid, description, amount, charge_date, officers_split=None):
    """Add a charge to the database"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Convert date to string format (YYYY-MM-DD)
        date_str = charge_date.strftime("%Y-%m-%d") if hasattr(charge_date, 'strftime') else str(charge_date)

        if charge_type == "Individual":
            if not uid:
                return "Invalid UID for individual charge"
            
            query = """
                INSERT INTO TOTAL_CHARGES 
                (UID, DESCRIPTION, AMOUNT, TYPE_OF_CHARGE, DATE, REMARKS)
                VALUES (%s, %s, %s, %s, %s, NULL)
            """
            cursor.execute(query, (
                uid,
                description,
                float(amount),
                charge_type,
                date_str
            ))
        
        elif charge_type == "Split":
            if not officers_split:
                return "Please add at least one officer to split"
            
            total_amount = float(amount)
            total_share = sum(float(split[2]) for split in officers_split)
            
            if total_share <= 0:
                return "Total share must be greater than zero"
            
            for officer in officers_split:
                officer_id = officer[0]
                share_amount = float(officer[2])
                individual_amount = total_amount * (share_amount / total_share)
                
                query = """
                    INSERT INTO TOTAL_CHARGES 
                    (UID, DESCRIPTION, AMOUNT, TYPE_OF_CHARGE, DATE, REMARKS)
                    VALUES (%s, %s, %s, %s, %s, NULL)
                """
                cursor.execute(query, (
                    officer_id,
                    f"Split: {description}",
                    individual_amount,
                    charge_type,
                    date_str
                ))
        else:
            return "Invalid charge type"

        connection.commit()
        return "Charge added successfully"

    except Error as err:
        connection.rollback()
        return f"Error adding charge: {err}"
    except ValueError as ve:
        return f"Invalid amount: {ve}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_charges():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT UID, DESCRIPTION, AMOUNT, DATE 
            FROM TOTAL_CHARGES
            ORDER BY DATE DESC
        """)
        return [list(row.values()) for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching charges: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===================== FIXED CHARGES =====================
def get_fixed_charges():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUB_NAME, RANK_1, RANK_2, RANK_3, RANK_4 
            FROM FIXED_CHARGES 
            LIMIT 15
        """)
        return [list(row.values()) for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching fixed charges: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def modify_fixed_charge(name, rank, amount):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        rank = rank.upper().replace(" ", "_")
        query = f"UPDATE FIXED_CHARGES SET {rank} = %s WHERE SUB_NAME = %s"
        cursor.execute(query, (amount, name))

        connection.commit()
        return "Fixed charge updated successfully."
    except Error as err:
        connection.rollback()
        return f"Error updating fixed charge: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
def addto_fixed_charges(rank, name, amount):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Ensure proper rank column
        rank_col = rank.upper().replace(" ", "_")
        if rank_col not in ["RANK_1", "RANK_2", "RANK_3", "RANK_4"]:
            return "Invalid rank"

        # Check if entry exists
        cursor.execute("SELECT * FROM FIXED_CHARGES WHERE SUB_NAME = %s", (name,))
        if cursor.fetchone():
            # Update if exists
            cursor.execute(f"UPDATE FIXED_CHARGES SET {rank_col} = %s WHERE SUB_NAME = %s", (amount, name))
        else:
            # Insert new entry with all ranks, defaulting others to 0
            values = {"RANK_1": 0, "RANK_2": 0, "RANK_3": 0, "RANK_4": 0}
            values[rank_col] = amount
            cursor.execute("""
                INSERT INTO FIXED_CHARGES (SUB_NAME, RANK_1, RANK_2, RANK_3, RANK_4)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, values["RANK_1"], values["RANK_2"], values["RANK_3"], values["RANK_4"]))

        connection.commit()
        return "Fixed charge added/updated successfully."
    except Error as err:
        connection.rollback()
        return f"Error updating fixed charge: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===================== MESS MANAGEMENT =====================
def add_mess_entry(charge_type, description, remarks, amount, officer, date):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if charge_type == "Normal":
            query = """INSERT INTO MESS_LEDGER (TYPE, DESCRIPTION, REMARKS, AMOUNT, DATE)
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (charge_type, description, remarks, amount, date))   
        else:
            query = """INSERT INTO MESS_LEDGER (TYPE, DESCRIPTION, REMARKS, AMOUNT, OFFICER, DATE)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (charge_type, description, remarks, amount, officer, date))   
            
        connection.commit()
        return "Mess entry added successfully."
    except Error as err:
        connection.rollback()
        return f"Error adding mess entry: {err}"
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===================== UTILITY FUNCTIONS =====================
def existing_officers_uid():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT UID FROM OFFICERS")
        return [row['UID'] for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching officer UIDs: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def existing_officers_name():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT NAME FROM OFFICERS")
        return [row['NAME'] for row in cursor.fetchall()]
    except Error as err:
        print(f"Error fetching officer names: {err}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def get_name_from_uid(uid):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT NAME FROM OFFICERS WHERE UID=%s", (uid,))
        result = cursor.fetchone()
        return result['NAME'] if result else None
    except Error as err:
        print(f"Error fetching name: {err}")
        return None
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# ===================== INITIALIZATION =====================
def initialize_database():
    """Initialize all database tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['db']}")
        cursor.execute(f"USE {DB_CONFIG['db']}")
        
        # Create tables
        tables = [
            """
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
            """,
            """
            CREATE TABLE IF NOT EXISTS FIXED_CHARGES (
                SUB_NAME VARCHAR(50) PRIMARY KEY NOT NULL,
                RANK_1 FLOAT NOT NULL,
                RANK_2 FLOAT NOT NULL,
                RANK_3 FLOAT NOT NULL,
                RANK_4 FLOAT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS TOTAL_CHARGES (
                UID VARCHAR(50) NOT NULL,
                DESCRIPTION VARCHAR(500),
                AMOUNT FLOAT NOT NULL,
                TYPE_OF_CHARGE VARCHAR(200),
                DATE VARCHAR(20) NOT NULL,
                REMARKS VARCHAR(200)
            )
            """,
            """
           CREATE TABLE IF NOT EXISTS CURRENT_SPLIT (
    UID VARCHAR(50) PRIMARY KEY,
    NAME VARCHAR(100),
    AMOUNT FLOAT NOT NULL
)
            """,
            """
            CREATE TABLE IF NOT EXISTS MESS_LEDGER (
                TYPE VARCHAR(50),
                DESCRIPTION VARCHAR(100),
                REMARKS VARCHAR(200),
                AMOUNT FLOAT NOT NULL,
                OFFICER VARCHAR(100),
                DATE VARCHAR(20) NOT NULL
            )
            """
        ]
        
        for table in tables:
            cursor.execute(table)
        
        # Insert default fixed charges
        cursor.execute("""
            INSERT IGNORE INTO FIXED_CHARGES 
            (SUB_NAME, RANK_1, RANK_2, RANK_3, RANK_4)
            VALUES 
            ('Accomodation', 200, 200, 200, 200),
            ('Spouse Memento Fund', 200, 200, 200, 200)
        """)
        
        connection.commit()
        print("Database initialized successfully")
    except Error as err:
        connection.rollback()
        print(f"Error initializing database: {err}")
        raise
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    initialize_database()