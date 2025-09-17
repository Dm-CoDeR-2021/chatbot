from supabase import create_client, Client
import json


def decode_unicode(s):
    return s.encode('utf-8').decode('unicode-escape')

def Connect(url = "https://hcdqohiosggzfjpvheoj.supabase.co",key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhjZHFvaGlvc2dnemZqcHZoZW9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjI4NTk4NywiZXhwIjoyMDcxODYxOTg3fQ.vUj0Z84Vwwx-kR4PQqAdrcApxHCSpAKthO_m8jj937s") -> int:
    try: 
        db: Client = create_client(url, key)
        return db
    except:
        return -1
    
def Fetch(table = "users"):
    try:
        db = Connect()

        response = (
            db.table(table)
            .select('*')
            .execute()
        )

        return response
    except:
        return -1


def Insert(table = "users", data = {}) -> int:
    try:
        db = Connect()

        response = (
        db.table(table)
        .insert(data)
        .execute()
        )

        return response
    except:
        return -1
    
def Update(table = "users", data = {}, eq = "id", eq_value = 0) -> int:
    try:
        db = Connect()

        response = (
            db.table(table)
            .update(data)
            .eq(eq, eq_value)
            .execute()
        )

        return response
    except:
        return -1

def Upsert(table = "users", data = {}) -> int:
    try:
        db = Connect()

        response = (
            db.table(table)
            .upsert(data)
            .execute()
        )

        return response
    except:
        return -1
    

def Select(table = "users", eq = "id", eq_value = 0) -> int:
    try:
        db = Connect()

        response = (
            db.table(table)
            .select("*")
            .eq(eq, eq_value)
            .execute()
        )

        return response
    except:
        return -1
    
def Delete(table = "users", eq = "id", eq_value = 0) -> int:
    try:
        db = Connect()

        response = (
            db.table(table)
            .delete()
            .eq(eq, eq_value)
            .execute()
        )

        return response
    except:
        return -1

def Exist(table = "users", eq = "id", eq_value = 0) -> int:
    try:
        response = Select(table,eq,eq_value)
        return response.data
    except:
        return -1

