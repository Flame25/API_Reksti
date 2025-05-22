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

def update_key():
    new_key = generate_key()
    timestamp = datetime.utcnow().isoformat()

    response = supabase.table("Key").update({
        "current_key": new_key,
        "update_at": timestamp
    }).eq("id", 1).execute()

    if response.data:
        print(f"[{timestamp}] Key updated successfully: {new_key}")
    else:
        print(f"[{timestamp}] Failed to update key: {response}")

def run_hourly_key_updater():
    while True:
        update_key()
        time.sleep(3600)

if __name__ == "__main__":
    run_hourly_key_updater()
