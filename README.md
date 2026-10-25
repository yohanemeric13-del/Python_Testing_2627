# Application de réservation de compétitions

Cette application Flask permet aux clubs de consulter les compétitions et de réserver des places avec leurs points. Les données sont conservées dans `clubs.json` et `competitions.json`.

## Prérequis

- Python 3.9 ou une version plus récente (Python 3.14 convient également).
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

Les tests automatisés du projet se trouvent dans `tests/`. Les dépendances de test et leurs commandes sont documentées dans le guide de développement du projet.

## Données

- `competitions.json` contient les compétitions et leurs places disponibles.
- `clubs.json` contient les clubs, leurs adresses e-mail et leurs points.
