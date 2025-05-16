import json
import psycopg2
from cryptography.fernet import Fernet
import pyotp
import time

def handle(event, context):
    try:
        data = json.loads(event.body)
        username = data.get("username")
        password = data.get("password")
        totp_code = data.get("totp_code")

        if not username or not password or not totp_code:
            return "Paramètres manquants", 400

        # Lire les secrets
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

        # Connexion à la BDD
        conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT password, mfa, gendate, expired FROM users WHERE username=%s", (username,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return json.dumps({"success": False, "reason": "User not found"}), 401

        db_password_encrypted, mfa_encrypted, gendate, expired = row

        fernet = Fernet(fernet_key)
        try:
            db_password = fernet.decrypt(db_password_encrypted.encode()).decode()
            mfa_secret = fernet.decrypt(mfa_encrypted.encode()).decode() if mfa_encrypted else ""
        except Exception as e:
            return json.dumps({"success": False, "reason": f"Decryption error: {str(e)}"}), 401

        now = int(time.time())
        six_months = 6 * 30 * 24 * 60 * 60  # 6 mois en secondes
        if expired or (now - gendate > six_months):
            # Marquer le compte comme expiré si ce n'est pas déjà fait
            if not expired:
                conn = psycopg2.connect(
                    dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port
                )
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET expired=TRUE WHERE username=%s", (username,)
                )
                conn.commit()
                cur.close()
                conn.close()
            return json.dumps({
                "success": False,
                "reason": "Credentials expired, renewal required"
            }), 403

        if password != db_password:
            return json.dumps({"success": False, "reason": "Bad password"}), 401

        if not mfa_secret:
            return json.dumps({"success": False, "reason": "No 2FA registered"}), 401

        totp = pyotp.TOTP(mfa_secret)
        if not totp.verify(totp_code):
            return json.dumps({"success": False, "reason": "Invalid 2FA code"}), 401

        return json.dumps({"success": True, "reason": "Authentication OK"})

    except Exception as e:
        return json.dumps({"success": False, "reason": str(e)}), 500
