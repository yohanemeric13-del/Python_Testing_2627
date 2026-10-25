"""Scénario Locust en lecture seule pour l'application de réservation."""

import json
from pathlib import Path
from urllib.parse import quote

from locust import HttpUser, between, task


PROJECT_ROOT = Path(__file__).resolve().parent
with (PROJECT_ROOT / 'clubs.json').open(encoding='utf-8') as clubs_file:
    CLUBS = json.load(clubs_file)['clubs']
with (PROJECT_ROOT / 'competitions.json').open(encoding='utf-8') as competitions_file:
    COMPETITIONS = json.load(competitions_file)['competitions']

AVAILABLE_CLUBS = [club for club in CLUBS if int(club.get('points', 0)) > 0]
AVAILABLE_COMPETITIONS = [
    competition
    for competition in COMPETITIONS
    if str(competition.get('date', ''))[:4].isdigit()
    and int(str(competition['date'])[:4]) >= 2026
    and int(competition.get('numberOfPlaces', 0)) > 0
]


class BookingPlatformUser(HttpUser):
    """Visite les pages et ouvre une réservation sans en acheter."""

    wait_time = between(1, 3)

    def on_start(self):
        if not AVAILABLE_CLUBS:
            raise RuntimeError('Aucun club avec des points disponibles dans clubs.json.')
        self.club = AVAILABLE_CLUBS[0]
        self.competition = AVAILABLE_COMPETITIONS[0] if AVAILABLE_COMPETITIONS else None
        self.client.post(
            '/showSummary',
            data={'email': self.club['email']},
            name='/showSummary [connexion]',
        )

    @task(4)
    def visit_home(self):
        self.client.get('/', name='/')

    @task(3)
    def visit_points(self):
        self.client.get('/points', name='/points')

    @task(2)
    def refresh_summary(self):
        self.client.post(
            '/showSummary',
            data={'email': self.club['email']},
            name='/showSummary',
        )

    @task(2)
    def open_booking_page(self):
        if self.competition is None:
            return
        competition_name = quote(self.competition['name'], safe='')
        club_name = quote(self.club['name'], safe='')
        self.client.get(
            f'/book/{competition_name}/{club_name}',
            name='/book/<competition>/<club>',
        )
