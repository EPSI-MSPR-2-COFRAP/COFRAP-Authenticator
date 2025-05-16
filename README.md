# Projet MSPR 2 – COFRAP
 
## ✨ Objectif
Ce projet a pour but de prototyper une solution d'authentification cloud s'appuyant sur des fonctions Serverless déployées sur Kubernetes avec OpenFaaS. Il s'agit d'une demande de l'entreprise COFRAP pour réduire les risques de compromission de comptes utilisateur.

## 💻 Fonctionnalités attendues
- Création automatique d'identifiants sécurisés (mot de passe + QRCode)
- Mise en place d'une authentification forte via TOTP/2FA
- Stockage chiffré des données utilisateur en base
- Vérification de l'expiration des identifiants (6 mois max)
- Interface frontend simple pour utiliser ces fonctions

## 🚀 Environnement technique
- OpenFaaS (fonctions serverless)
- Kubernetes (minikube ou K3S)
- Base de données (PostgreSQL recommandée)
- Python (langage recommandé pour les fonctions)

## 📊 Livrables principaux
- PoC fonctionnel déployé sur un cluster
- Code source des fonctions et de l'interface
- Diagramme de Gantt, tableau Kanban
- Dossier de présentation et soutenance

> ✅ Ce README sera enrichi avec les choix techniques, commandes d’installation, schémas d’architecture, tests, etc.
