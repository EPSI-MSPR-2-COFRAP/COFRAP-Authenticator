import json
import random
import string
import base64
import psycopg2
import qrcode
from cryptography.fernet import Fernet
from io import BytesIO
import time

def generate_password(length=24):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_-=+"
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*()_-=+" for c in password)):
            return password

def handle(event, context):
    try:
        data = json.loads(event.body)
        username = data.get("username")
        if not username:
            return "Paramètre username manquant", 400

        # Lecture secrets
        with open('/var/openfaas/secrets/db-user') as f:
            db_user = f.read().strip()
        with open('/var/openfaas/secrets/db-pass') as f:
            db_pass = f.read().strip()
        with open('/var/openfaas/secrets/db-name') as f:
            db_name = f.read().strip()
        with open('/var/openfaas/secrets/db-host') as f:
            db_host = f.read().strip()
        with open('/var/openfaas/secrets/db-port') as f:
            db_port = f.read().strip()
        with open('/var/openfaas/secrets/fernet-key') as f:
            fernet_key = f.read().strip()

        # Générer mot de passe et le chiffrer
        password = generate_password()
        fernet = Fernet(fernet_key)
        password_encrypted = fernet.encrypt(password.encode()).decode()

        # Générer QR code du mot de passe
        qr = qrcode.QRCode()
        qr.add_data(password)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Connexion BDD et insertion
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )
        gendate = int(time.time())
        expired = False
        mfa = ""  # sera rempli plus tard

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, password, mfa, gendate, expired)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET password=EXCLUDED.password, gendate=EXCLUDED.gendate, expired=EXCLUDED.expired
            """,
            (username, password_encrypted, mfa, gendate, expired))
        conn.commit()
        cur.close()
        conn.close()

        # Retourne le résultat
        return json.dumps({
            "username": username,
            "password": password,     # à masquer côté prod
            "qr_base64": qr_base64
        })

    except Exception as e:
        return f"Erreur : {str(e)}", 500
