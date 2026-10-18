# 🔐 Casser l'Algorithme de Chiffrement RSA (Cryptanalyse & Factorisation)

Ce projet est une suite d'outils et de scripts en **Python** dédiée à l'étude de la sécurité du système cryptographique **RSA**, et plus particulièrement aux attaques par **factorisation de la clé publique $N$**.

Le projet met en pratique deux algorithmes majeurs de factorisation (l'**attaque de Fermat** et l'**algorithme $\rho$ de Pollard**) ainsi qu'une implémentation massivement parallélisée sur **GPU NVIDIA (CUDA)** et une interface graphique interactive (**Tkinter**).

---

## 📌 Sommaire

- [1. Contexte & Principe de l'Attaque](#1-contexte--principe-de-lattaque)
- [2. Architecture du Projet](#2-architecture-du-projet)
- [3. Détail des Scripts](#3-détail-des-scripts)
  - [Interface Graphique (GUI)](#interface-graphique-gui---generateur-de-cle-public-avec-messagepy)
  - [Attaque de Fermat (CPU)](#attaque-de-fermat-cpu---dechiffrement_rsa_fermatpy)
  - [Attaque Rho de Pollard](#attaque-rho-de-pollard---dechiffrement_rsa_rho-pollardpy)
  - [Attaque de Fermat Accélérée sur GPU (NVIDIA CUDA)](#attaque-de-fermat-accélérée-sur-gpu---fermat-nvideapy)
- [4. Fondements Mathématiques](#4-fondements-mathématiques)
- [5. Installation & Prérequis](#5-installation--prérequis)
- [6. Utilisation](#6-utilisation)
- [7. Bonnes Pratiques & Sécurité RSA](#7-bonnes-pratiques--sécurité-rsa)

---

## 1. Contexte & Principe de l'Attaque

Le chiffrement asymétrique RSA repose sur la difficulté calculatoire du problème de la décomposition en facteurs premiers :
$$\text{Clé publique} = (N, e) \quad \text{où} \quad N = p \times q$$
Pour retrouver la clé privée $d$, un attaquant doit calculer l'indicatrice d'Euler :
$$\phi(N) = (p - 1)(q - 1)$$
puis dériver l'inverse modulaire :
$$d \equiv e^{-1} \pmod{\phi(N)}$$

Si un attaquant parvient à factoriser $N$ et à isoler $p$ et $q$, la sécurité de RSA est anéantie et tous les messages chiffrés peuvent être déchiffrés instantanément.

### Vulnérabilités exploitées dans ce projet :
1. **Écart faible entre $p$ et $q$ (Attaque de Fermat)** : Si les nombres premiers $p$ et $q$ sont choisis trop proches l'un de l'autre, la méthode de factorisation de Fermat retrouve les facteurs en un temps négligeable.
2. **Petits facteurs ou facteurs à structure favorable ($\rho$ de Pollard)** : Si un des facteurs possède une structure propice, l'algorithme probabiliste de Pollard le détecte bien plus vite qu'une recherche exhaustive.

---

## 2. Architecture du Projet

```text
├── generateur-de-cle-public-avec-message.py   # Application GUI complète (Génération, Chiffrement, Export JSON, Attaque)
├── dechiffrement_RSA_FERMAT.py                # Démonstration de l'attaque de Fermat sur CPU avec cas de test
├── dechiffrement_RSA_RHO-POLLARD.py           # Démonstration de l'algorithme Rho de Pollard
├── Fermat-nvidea.py                           # Factorisation de Fermat ultra-rapide sur GPU via NVIDIA CUDA
├── requirements.txt                           # Dépendances Python requises
├── requerement.txt                            # Fichier miroir des dépendances
└── README.md                                  # Documentation du projet
```

---

## 3. Détail des Scripts

### Interface Graphique (GUI) - `generateur-de-cle-public-avec-message.py`
Application fenêtrée avec onglets :
- **Onglet Chiffrer (Émission)** :
  - Choix du niveau de difficulté (de **32 bits** à **64 bits**).
  - Génération de clés avec $p$ et $q$ proches.
  - Chiffrement du message clair découpé en blocs et encodé en lettres (base 26, `A-Z`).
  - Sauvegarde du paquet public `(n, e, chiffre)` sous format JSON.
- **Onglet Déchiffrer (Attaque)** :
  - Importation d'un fichier JSON ou saisie manuelle.
  - Résolution non-bloquante (multithreading) avec l'attaque de Fermat.
  - Affichage des facteurs $p$ et $q$, de la clé privée $d$, du message en clair reconstruit et des temps d'exécution (factorisation, calcul de $d$, déchiffrement).

### Attaque de Fermat (CPU) - `dechiffrement_RSA_FERMAT.py`
- Implémente l'algorithme de factorisation de Fermat en pur Python.
- Testé sur plusieurs modules $N$ et exposants $e$.
- Démontre la rapidité de l'attaque lorsque $p \approx q$ et met en évidence la limite de l'approche CPU standard lorsque les facteurs s'éloignent ou dépassent une certaine taille.

### Attaque Rho de Pollard - `dechiffrement_RSA_RHO-POLLARD.py`
- Utilise la fonction génératrice $f(x) = (x^2 + 1) \pmod N$.
- Détecte les cycles à l'aide de l'algorithme de Floyd (lièvre et tortue) et calcule $\gcd(|x - y|, N)$.
- Mesure le temps nécessaire à l'extraction de $p$, calcule $q = N / p$ et déduit la clé privée $d$.

### Attaque de Fermat Accélérée sur GPU - `Fermat-nvidea.py`
- Écrit avec **Numba CUDA** pour exploiter la puissance des processeurs graphiques NVIDIA.
- Distribution parallèle de millions de candidats $a$ sur des grilles de threads GPU (`fermat_kernel`).
- Détection instantanée via une opération atomique `cuda.atomic.cas`.
- Fallback automatique sur CPU si le module $N$ dépasse les capacités entières 64 bits (`uint64`).

---

## 4. Fondements Mathématiques

### A. Factorisation de Fermat
Tout entier impair $N$ peut s'écrire sous forme d'une différence de deux carrés :
$$N = a^2 - b^2 = (a - b)(a + b)$$
En posant $a \ge \lceil\sqrt{N}\rceil$, on teste séquentiellement si :
$$b^2 = a^2 - N$$
est un carré parfait. Dès que $b = \sqrt{a^2 - N}$ est un entier :
$$p = a - b \quad \text{et} \quad q = a + b$$

### B. Algorithme $\rho$ de Pollard
Basé sur le paradoxe des anniversaires, il cherche une collision modulo un facteur non trivial $p$ de $N$ :
$$x_{i+1} = f(x_i) \pmod N, \quad y_{i+1} = f(f(y_i)) \pmod N$$
$$d = \gcd(|x_i - y_i|, N)$$
Si $1 < d < N$, alors $d$ est un facteur non trivial de $N$.

---

## 5. Installation & Prérequis

### Prérequis
- **Python 3.10** ou supérieur (testé sur Python 3.12 et 3.14).
- Pour l'accélération GPU (`Fermat-nvidea.py`) : une carte graphique **NVIDIA** avec les pilotes à jour et le support CUDA.

### Installation
Clonez le dépôt puis installez les dépendances :
```bash
git clone https://github.com/ACHRAF-KHAIROUNI/Casser-algorithme-de-chiffrement-RSA.git
cd Casser-algorithme-de-chiffrement-RSA
pip install -r requirements.txt
```

> **Note :** Les modules `tkinter`, `math`, `time`, `json`, `random` et `threading` font partie intégrante de la bibliothèque standard de Python et ne nécessitent aucune installation additionnelle.

---

## 6. Utilisation

### 1. Lancer l'interface graphique
```bash
python generateur-de-cle-public-avec-message.py
```

### 2. Tester l'attaque de Fermat sur CPU
```bash
python dechiffrement_RSA_FERMAT.py
```

### 3. Tester l'attaque Rho de Pollard
```bash
python dechiffrement_RSA_RHO-POLLARD.py
```

### 4. Lancer l'attaque accélérée sur GPU NVIDIA
```bash
python Fermat-nvidea.py
```

---

## 7. Bonnes Pratiques & Sécurité RSA

Pour garantir la sécurité de RSA contre ce type d'attaques :
1. **Éloignement suffisant de $p$ et $q$** : Les deux nombres premiers ne doivent jamais être trop proches. On impose généralement $|p - q| > 2^{n/2 - 100}$ pour rendre l'attaque de Fermat inopérante.
2. **Taille minimale des clés** : Utiliser au minimum des modules $N$ de **2048 bits** (recommandé 3072 ou 4096 bits pour une protection à long terme).
3. **Génération cryptographiquement sûre** : Utiliser des générateurs d'aléa cryptographiques (ex: `secrets` ou `/dev/urandom`).
4. **Schémas de remplissage (Padding)** : Ne jamais utiliser RSA "brut" (Textbook RSA). Utiliser des schémas modernes comme **OAEP** (Optimal Asymmetric Encryption Padding) pour le chiffrement et **PSS** pour la signature.
