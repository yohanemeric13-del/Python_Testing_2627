"""Chargement et sauvegarde des données JSON de l'application."""

import json


def load_clubs(file_path):
    """Charge la liste des clubs depuis un fichier JSON."""
    with open(file_path, encoding='utf-8') as clubs_file:
        return json.load(clubs_file)['clubs']


def load_competitions(file_path):
    """Charge la liste des compétitions depuis un fichier JSON."""
    with open(file_path, encoding='utf-8') as competitions_file:
        return json.load(competitions_file)['competitions']


def save_clubs(file_path, clubs):
    """Enregistre la liste des clubs dans un fichier JSON."""
    with open(file_path, 'w', encoding='utf-8') as clubs_file:
        json.dump({'clubs': clubs}, clubs_file, indent=4, ensure_ascii=False)


def save_competitions(file_path, competitions):
    """Enregistre la liste des compétitions dans un fichier JSON."""
    with open(file_path, 'w', encoding='utf-8') as competitions_file:
        json.dump(
            {'competitions': competitions},
            competitions_file,
            indent=4,
            ensure_ascii=False,
        )
