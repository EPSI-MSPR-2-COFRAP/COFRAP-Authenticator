from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

GATEWAY_BASE = "http://127.0.0.1:60408/function/"

HTML_FORM = """
<!doctype html>
<title>OpenFaaS MSPR PoC Frontend</title>
<h2>Test MSPR 2 : Fonctions Serverless</h2>

<form method="post">
  <label>Choisir la fonction :</label>
  <select name="fonction" onchange="this.form.submit()">
    <option value="generate-password" {% if fonction == "generate-password" %}selected{% endif %}>Générer mot de passe</option>
    <option value="generate-2fa" {% if fonction == "generate-2fa" %}selected{% endif %}>Générer 2FA</option>
    <option value="authenticate-user" {% if fonction == "authenticate-user" %}selected{% endif %}>Authentifier utilisateur</option>
  </select>
  <br><br>

  <label>Username:</label>
  <input name="username" value="{{ username or '' }}" required><br>

  {% if fonction == "authenticate-user" %}
    <label>Mot de passe:</label>
    <input name="password" type="text" required><br>
    <label>Code 2FA:</label>
    <input name="totp_code" type="text" required><br>
  {% endif %}

  <input type="submit" value="Envoyer">
</form>

{% if result %}
  <h3>Résultat :</h3>
  {% if fonction == "generate-password" and result.get('qr_base64') %}
    <p><b>Mot de passe généré :</b> <code>{{result['password']}}</code></p>
    <img src="data:image/png;base64,{{result['qr_base64']}}" alt="QR Code du mot de passe"><br>
  {% elif fonction == "generate-2fa" and result.get('mfa_qr_base64') %}
    <img src="data:image/png;base64,{{result['mfa_qr_base64']}}" alt="QR Code 2FA"><br>
    <p>QR code à scanner dans Google Authenticator !</p>
  {% elif fonction == "authenticate-user" %}
    <pre>{{result}}</pre>
  {% else %}
    <pre>{{result}}</pre>
  {% endif %}
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    fonction = request.form.get("fonction", "generate-password")
    username = request.form.get("username", "")
    result = None

    if request.method == "POST":
        data = {"username": username}
        endpoint = GATEWAY_BASE + fonction

        if fonction == "authenticate-user":
            data["password"] = request.form.get("password", "")
            data["totp_code"] = request.form.get("totp_code", "")

        try:
            resp = requests.post(endpoint, json=data)
            if resp.status_code == 200:
                result = resp.json()
            else:
                result = {"error": resp.text}
        except Exception as e:
            result = {"error": str(e)}

    return render_template_string(HTML_FORM, fonction=fonction, username=username, result=result)

if __name__ == "__main__":
    app.run(debug=True)
