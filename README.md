# Application de réservation de compétitions

Cette application Flask permet aux clubs de consulter les compétitions et de réserver des places avec leurs points. Les données sont conservées dans `clubs.json` et `competitions.json`.

## Prérequis

- Python 3.11 ou une version plus récente (Python 3.14 convient également). Locust, utilisé pour les tests de performance, nécessite Python 3.11 ou plus récent.
- Git.

## Installation

Depuis le dossier du projet, créez puis activez un environnement virtuel.

### macOS et Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l’activation du script, utilisez l’invite de commandes Windows à la place.

### Windows (invite de commandes)

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

Une fois l’environnement activé, installez les dépendances sur toutes les plateformes :

```text
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration et lancement

L’application utilise `server.py`. Définissez `FLASK_APP` dans le terminal où vous lancerez Flask.

Pour conserver les sessions après un redémarrage, définissez aussi `FLASK_SECRET_KEY` avec une clé aléatoire. Générez-la avec `python -c "import secrets; print(secrets.token_hex(32))"`, puis copiez la valeur générée dans les commandes ci-dessous. Gardez cette valeur privée et ne l’ajoutez pas à Git. Sans cette variable, l’application génère une clé temporaire au démarrage.

### macOS et Linux

```bash
export FLASK_APP=server
export FLASK_SECRET_KEY='votre-cle-generee'
flask run
```

### Windows PowerShell

```powershell
$env:FLASK_APP = "server"
$env:FLASK_SECRET_KEY = "votre-cle-generee"
flask run
```

### Windows (invite de commandes)

```bat
set FLASK_APP=server
set FLASK_SECRET_KEY=votre-cle-generee
flask run
```

Le serveur affiche une adresse locale, généralement `http://127.0.0.1:5000`. Ouvrez cette adresse dans votre navigateur. Pour arrêter le serveur, faites `Ctrl+C` dans le terminal. Ces commandes lancent le serveur de développement Flask, destiné au développement local.

## Tests

Les dépendances de l’application, les outils de test et l’outil de mesure de performance sont tous listés dans `requirements.txt`. Installe-les avec :

```text
python -m pip install -r requirements.txt
```

Lancer les tests automatisés avec pytest :

```text
python -m pytest
```

Mesurer la couverture de ces tests et afficher le rapport dans le terminal :

```text
python -m coverage run -m pytest
python -m coverage report
```

Pour générer aussi un rapport HTML, exécutez `python -m coverage html`, puis ouvrez `htmlcov/index.html` dans un navigateur.

### Test de performance avec Locust

Le scénario `locustfile.py` consulte l’accueil, le tableau des points, le résumé du club et une page de réservation. Il n’envoie aucune réservation.
Pour vérifier que Locust est installé, exécutez `locust --version`.

Dans un premier terminal, démarrez l’application. Dans un second terminal, à la racine du projet et avec l’environnement virtuel activé, créez le dossier du rapport et lancez une charge de 10 utilisateurs pendant une minute :

```bash
mkdir -p reports/performance
locust -f locustfile.py --host http://127.0.0.1:5000 --headless -u 10 -r 2 -t 1m --csv reports/performance/locust --html reports/performance/rapport.html
```

Le rapport HTML et les résultats CSV seront enregistrés dans `reports/performance/`. Complétez `reports/performance/rapport.md` avec les conditions de test (machine, version de Python, nombre d’utilisateurs et durée), ainsi que les résultats Locust.

## Données

- `competitions.json` contient les compétitions et leurs places disponibles.
- `clubs.json` contient les clubs, leurs adresses e-mail et leurs points.
