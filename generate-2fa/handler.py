import json
import pyotp
import qrcode
import base64
import psycopg2
from cryptography.fernet import Fernet
from io import BytesIO

def handle(event, context):
    try:
        data = json.loads(event.body)
        username = data.get("username")
        if not username:
            return "Paramètre username manquant", 400

        # Lecture des secrets pour la BDD et Fernet
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

        # Générer le secret TOTP (2FA)
        secret = pyotp.random_base32()
        fernet = Fernet(fernet_key)
        secret_encrypted = fernet.encrypt(secret.encode()).decode()

        # QR code pour l’application d’authentification
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username, issuer_name="COFRAP"
        )
        qr = qrcode.QRCode()
        qr.add_data(uri)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Mise à jour du champ "mfa" en base
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET mfa=%s WHERE username=%s",
            (secret_encrypted, username)
        )
        conn.commit()
        cur.close()
        conn.close()

        return json.dumps({
            "username": username,
            "mfa_qr_base64": qr_base64
        })

    except Exception as e:
        return f"Erreur : {str(e)}", 500
