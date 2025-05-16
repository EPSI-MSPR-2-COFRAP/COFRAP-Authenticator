# MSPR 2 – PoC Serverless Auth avec OpenFaaS & Kubernetes

## 🎯 Objectif

Ce projet est un Proof of Concept (PoC) qui répond au cahier des charges de la COFRAP :
- Générer des mots de passe complexes et QR codes pour les utilisateurs.
- Générer des secrets 2FA (TOTP) et QR codes associés.
- Chiffrer toutes les données sensibles.
- Stocker les infos dans une base PostgreSQL.
- Utiliser une architecture **serverless** moderne (OpenFaaS sur Kubernetes).

---

## 📦 Structure du projet
<pre>
.
├── generate-password/ # Fonction de génération de mot de passe et QR code
│ ├── handler.py
│ ├── requirements.txt
│ └── function/
│ └── requirements.txt
├── postgres-deployment.yaml # Déploiement de PostgreSQL sur Kubernetes
├── stack.yaml # Déploiement OpenFaaS
└── README.md
</pre>

---

## 🚦 Prérequis

- Docker Desktop ou Docker Engine
- Minikube
- kubectl
- Helm 3
- faas-cli (OpenFaaS CLI)
- Python 3.8 ou supérieur

---

## 🚀 Déploiement – Quick Start

1. Cloner le dépôt  
<pre>git clone https://github.com/EPSI-MSPR-2-COFRAP/COFRAP-Authenticator.git</pre>
cd <NOM_DU_REPO>  

2. Lancer Minikube  
<pre>minikube start --driver=docker --cpus=4 --memory=4096 --disk-size=20g</pre>

3. Installer OpenFaaS  
<pre>
kubectl create namespace openfaas
kubectl create namespace openfaas-fn
helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update
helm upgrade openfaas openfaas/openfaas --install --namespace openfaas --set basic_auth=true --set functionNamespace=openfaas-fn
</pre> 

4. Récupérer le mot de passe admin OpenFaaS  
<pre>[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}")))</pre>

5. Ouvrir le dashboard OpenFaaS   
<pre>minikube service gateway-external -n openfaas</pre>
Note l’URL (ex : http://127.0.0.1:60408)  

6. Installer faas-cli  
<pre>curl -sSL https://cli.openfaas.com | sh</pre>
> ou télécharger le binaire sous Windows

7. Déployer PostgreSQL  
<pre>kubectl apply -f postgres-deployment.yaml</pre>

8. Créer les secrets OpenFaaS  
D’abord, connecte-toi à la gateway :  
<pre>faas-cli login --username admin --password [MOT_DE_PASSE] --gateway http://127.0.0.1:[PORT]</pre>
Puis crée les secrets :  
<pre>
echo -n "faasuser" | faas-cli secret create db-user --gateway http://127.0.0.1:[PORT]  
echo -n "faaspass" | faas-cli secret create db-pass --gateway http://127.0.0.1:[PORT]  
echo -n "usersdb" | faas-cli secret create db-name --gateway http://127.0.0.1:[PORT]  
echo -n "postgres.openfaas-fn.svc.cluster.local" | faas-cli secret create db-host --gateway http://127.0.0.1:[PORT]  
echo -n "5432" | faas-cli secret create db-port --gateway http://127.0.0.1:[PORT]  
echo -n "[CLÉ_FERNET]" | faas-cli secret create fernet-key --gateway http://127.0.0.1:[PORT]  
</pre>
NB : Utilisez la même clé Fernet dans toute l’équipe !

9. Correction des dépendances Python  
Important : Copier le fichier requirements.txt dans le sous-dossier function/ pour chaque fonction Python :  
<pre>cp generate-password/requirements.txt generate-password/function/requirements.txt</pre>

10. Build, push et déploiement des fonctions   
<pre>
faas-cli build -f stack.yaml
faas-cli push -f stack.yaml
faas-cli deploy -f stack.yaml --gateway http://127.0.0.1:[PORT]  
</pre>

11. Tester la fonction  
- Via l’interface web :  
Rendez-vous sur http://127.0.0.1:[PORT]  
Cliquez sur la fonction generate-password  
Entrez dans le body :   
	<pre>{"username": "michel.ranu"}</pre>
Cliquez sur “Invoke”  

- Ou via la CLI :  
<pre>echo '{"username": "michel.ranu"}' | faas-cli invoke generate-password --gateway http://127.0.0.1:[PORT]</pre>

## 📚 Fonctionnalités – Documentation
Fonction generate-password  
Génère un mot de passe complexe pour l’utilisateur donné.  

Chiffre le mot de passe avec Fernet.  

Génère un QR code en base64.  

Stocke le tout en base PostgreSQL, colonne mfa vide.  

Retourne : username, password (en clair pour test), qr_base64.  

Exemple d’appel :  
<pre>{"username": "michel.ranu"}</pre>

Exemple de réponse :
<pre>
{
  "username": "michel.ranu",
  "password": "uq3Tn3#F%M6Qr&-P+OhVGZYu",
  "qr_base64": "iVBORw0KGgo...etc..."
}
</pre>