from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

GATEWAY_BASE = "http://127.0.0.1:8080/function/"

HTML_FORM = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>OpenFaaS MSPR PoC Frontend</title>
  <style>
    body {
      background: #f6f8fa;
      font-family: 'Segoe UI', Arial, sans-serif;
      margin: 0;
      padding: 0;
    }
    .container {
      background: #fff;
      max-width: 480px;
      margin: 40px auto;
      padding: 32px 28px 24px 28px;
      border-radius: 12px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    }
    h2 {
      color: #2d3a4b;
      margin-bottom: 24px;
      text-align: center;
    }
    form {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    label {
      font-weight: 500;
      color: #374151;
      margin-bottom: 4px;
    }
    input[type="text"], select {
      padding: 8px 10px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 1rem;
      background: #f9fafb;
      transition: border 0.2s;
    }
    input[type="text"]:focus, select:focus {
      border: 1.5px solid #2563eb;
      outline: none;
      background: #fff;
    }
    input[type="submit"] {
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 10px 0;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      margin-top: 10px;
      transition: background 0.2s;
    }
    input[type="submit"]:hover {
      background: #1d4ed8;
    }
    .result {
      margin-top: 28px;
      padding: 18px 14px;
      background: #f1f5f9;
      border-radius: 8px;
      border: 1px solid #e5e7eb;
    }
    code {
      background: #e0e7ef;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 1.05em;
      color: #1e293b;
    }
    img {
      margin: 12px 0;
      border-radius: 8px;
      border: 1px solid #e5e7eb;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      max-width: 180px;
      display: block;
    }
    @media (max-width: 600px) {
      .container { padding: 16px 6px; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Test MSPR 2 : Fonctions Serverless</h2>
    <form method="post">
      <label>Choisir la fonction :</label>
      <select name="fonction" onchange="this.form.submit()">
        <option value="generate-password" {% if fonction == "generate-password" %}selected{% endif %}>Générer mot de passe</option>
        <option value="generate-2fa" {% if fonction == "generate-2fa" %}selected{% endif %}>Générer 2FA</option>
        <option value="authenticate-user" {% if fonction == "authenticate-user" %}selected{% endif %}>Authentifier utilisateur</option>
      </select>

      <label>Username:</label>
      <input name="username" value="{{ username or '' }}" required>

      {% if fonction == "authenticate-user" %}
        <label>Mot de passe:</label>
        <input name="password" type="password" required>
        <label>Code 2FA:</label>
        <input name="totp_code" type="text" required>
      {% endif %}

      <input type="submit" value="Envoyer">
    </form>

    {% if result %}
      <div class="result">
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
      </div>
    {% endif %}
  </div>
</body>
</html>
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
