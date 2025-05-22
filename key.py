import random
import time
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os 

# Supabase setup
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_key():
    return ''.join(str(random.randint(1, 9)) for _ in range(6))

def update_keys():
    timestamp = datetime.utcnow().isoformat()

    # Fetch all rows from the table
    result = supabase.table("Key").select("id").execute()

    if result.data:
        for row in result.data:
            row_id = row["id"]
            new_key = generate_key()

            # Update each row with a unique key
            response = supabase.table("Key").update({
                "current_key": new_key,
                "update_at": timestamp
            }).eq("id", row_id).execute()

            if response.data:
                print(f"[{timestamp}] Row {row_id} updated with key: {new_key}")
            else:
                print(f"[{timestamp}] Failed to update row {row_id}")
    else:
        print("No data found to update.")

def run_hourly_key_updater():
    while True:
        update_keys()
        time.sleep(3600)

if __name__ == "__main__":
    run_hourly_key_updater()
