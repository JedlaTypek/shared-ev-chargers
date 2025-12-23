import requests
import random
import string

# Konfigurace
API_URL = "http://localhost:8000/api/v1"

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def create_user(email_prefix, name):
    email = f"{email_prefix}_{generate_random_string()}@example.com"
    payload = {
        "email": email,
        "password": "password123",
        "name": name,  # <--- PŘIDÁNO: Jméno je povinné
        "is_active": True
    }
    # Vytvoření uživatele
    response = requests.post(f"{API_URL}/users/", json=payload)
    if response.status_code == 201:
        user = response.json()
        print(f"✅ Vytvořen uživatel ({name}): ID {user['id']}, Email: {user['email']}")
        return user['id']
    else:
        print(f"⚠️ Nepodařilo se vytvořit uživatele {email}: {response.text}")
        return None

def create_rfid(card_uid, user_id):
    payload = {
        "card_uid": card_uid,
        "owner_id": user_id,
        "is_active": True
    }
    response = requests.post(f"{API_URL}/rfid-cards/", json=payload)
    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ Vytvořena RFID karta: {card_uid}")
    else:
        print(f"⚠️ Chyba RFID {card_uid}: {response.text}")

def create_charger(owner_id):
    payload = {
        "name": f"Test Charger",
        "latitude": 50.08804,
        "longitude": 14.42076,
        "street": "Testovací",
        "city": "Praha",
        "owner_id": owner_id,
        "is_active": True
    }
    response = requests.post(f"{API_URL}/chargers/", json=payload)
    if response.status_code == 201:
        charger = response.json()
        print(f"✅ Vytvořena nabíječka: ID {charger['id']}, OCPP ID: {charger['ocpp_id']}")
        return charger
    else:
        print(f"❌ Chyba nabíječky: {response.text}")
        return None

def main():
    print("--- PŘÍPRAVA DAT PRO TESTOVÁNÍ ---")
    
    # 1. Vytvoření uživatelů
    owner_id = create_user("owner", "Majitel Nabíječky")
    driver_id = create_user("driver", "Řidič Testovací")

    if not owner_id or not driver_id:
        print("❌ Chyba: Nepodařilo se vytvořit uživatele. Končím.")
        return

    # 2. Vytvoření RFID karet
    rfid_owner = f"DEAD{generate_random_string(4).upper()}"
    rfid_driver = f"BEEF{generate_random_string(4).upper()}"
    
    create_rfid(rfid_owner, owner_id)
    create_rfid(rfid_driver, driver_id)

    # 3. Vytvoření prázdné nabíječky
    charger = create_charger(owner_id)

    print("\n--- HOTOVO: DATA PŘIPRAVENA ---")
    print("Nyní se připoj se svým OCPP simulátorem s těmito údaji:")
    print(f"🔌 ChargePoint Identity (OCPP ID): {charger['ocpp_id']}")
    print(f"💳 RFID karta (Majitel):           {rfid_owner}")
    print(f"💳 RFID karta (Řidič - pro test):  {rfid_driver}")

if __name__ == "__main__":
    main()