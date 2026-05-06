import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

print("🔄 Connecting to MySQL Database...")

try:
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
    
    cursor = db.cursor(dictionary=True)
    print("✅ Database Connected Successfully!")
    
except mysql.connector.Error as err:
    if err.errno == 2003:
        print("❌ ERROR: MySQL Server is not running!")
        print("Fix: Open Services (Windows+R → services.msc) and start MySQL80")
    elif err.errno == 1045:
        print("❌ ERROR: Wrong username or password!")
    elif err.errno == 1049:
        print("❌ ERROR: Database 'quick_hire' does not exist!")
    else:
        print(f"❌ ERROR: {err}")
    exit()