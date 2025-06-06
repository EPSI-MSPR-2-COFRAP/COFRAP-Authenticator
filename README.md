# Projet MSPR 2 – COFRAP

# 🚀 MSPR 2 — PoC Authentification Serverless (OpenFaaS, Kubernetes, Python)

Bienvenue sur le projet MSPR 2 “Serverless Auth System” !  
Ce PoC illustre comment déployer, tester et scaler une chaîne d’authentification multi-facteurs moderne sur Kubernetes avec OpenFaaS, Python et PostgreSQL.

---

## ⚡️ Présentation du projet

- **Technos :** Python 3, OpenFaaS, Kubernetes, PostgreSQL, Flask, QR code, 2FA
- **Objectifs :**
  - Générer et stocker des mots de passe forts, chiffrés
  - Créer et associer un secret 2FA (TOTP) à chaque utilisateur
  - Authentifier un utilisateur en multi-facteur
  - “Scale-to-zero” (OpenFaaS) : zéro instance active hors besoin
  - Tester l’ensemble via un petit frontend web ergonomique

---

## 🛠️ Installation & Lancement

### 1. **Pré-requis**

- Docker Desktop ou Docker Engine
- Minikube (ou autre cluster Kubernetes local)
- kubectl, helm, faas-cli
- Python 3.12+ (pour le frontend Flask)

### 2. **Cloner le repo**

```bash
git clone https://github.com/EPSI-MSPR-2-COFRAP/COFRAP-Authenticator
```

### 3. **Démarrer Minikube**
minikube start --driver=docker --cpus=4 --memory=4096 --disk-size=20g

### 4. **Déployer PostgreSQL et OpenFaaS**
kubectl apply -f postgres-deployment.yaml
# Installer OpenFaaS (si besoin) :
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml
helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update
helm upgrade openfaas openfaas/openfaas \
  --install --namespace openfaas \
  --set basic_auth=true \
  --set functionNamespace=openfaas-fn

### 5. **Récupérer le mot de passe admin OpenFaaS**
 [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}")))

### 6. **Exposer la gateway OpenFaaS**
kubectl port-forward -n openfaas svc/gateway 8080:8080

### 7. **Créer les secrets nécessaire**
# Secrets PostgreSQL
echo -n "faasuser" | faas-cli secret create db-user --gateway http://127.0.0.1:8080
echo -n "faaspass" | faas-cli secret create db-pass --gateway http://127.0.0.1:8080
echo -n "usersdb" | faas-cli secret create db-name --gateway http://127.0.0.1:8080
echo -n "postgres.openfaas-fn.svc.cluster.local" | faas-cli secret create db-host --gateway http://127.0.0.1:8080
echo -n "5432" | faas-cli secret create db-port --gateway http://127.0.0.1:8080
# Secret Fernet (chiffrement)
echo -n "<LA_FERNET_KEY>" | faas-cli secret create fernet-key --gateway http://127.0.0.1:8080

### 8. **Créer les secrets nécessaire**
kubectl exec -it -n openfaas-fn <nom_pod_postgres> -- bash
psql -U faasuser -d usersdb

-- Dans psql :
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    mfa TEXT NOT NULL,
    gendate BIGINT NOT NULL,
    expired BOOLEAN NOT NULL DEFAULT FALSE
);


### 9. **Build, push, deploy toutes les fonctions**
faas-cli build -f stack.yaml
faas-cli push -f stack.yaml
faas-cli deploy -f stack.yaml --gateway http://127.0.0.1:8080

### 9. **Lancer le frontend Flask**
cd frontend
pip install -r requirements.txt
python app.py
