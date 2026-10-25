import json
import os
import secrets
from copy import deepcopy
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Flask,render_template,request,redirect,flash,url_for,session

CLUBS_FILE = 'clubs.json'
COMPETITIONS_FILE = 'competitions.json'


def get_secret_key():
    return os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)


def loadClubs():
    with open(CLUBS_FILE) as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(COMPETITIONS_FILE) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def is_competition_upcoming(competition, current_time=None):
    try:
        competition_time = datetime.strptime(competition.get('date', ''), '%Y-%m-%d %H:%M:%S')
    except (AttributeError, TypeError, ValueError):
        return False
    return competition_time > (current_time or datetime.now())


def get_upcoming_competitions():
    return [competition for competition in competitions if is_competition_upcoming(competition)]


def saveClubs():
    with open(CLUBS_FILE, 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)


def saveCompetitions():
    with open(COMPETITIONS_FILE, 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)


app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret_key()

competitions = loadCompetitions()
clubs = loadClubs()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        email = session.get('club_email')
        if not email or not any(club['email'] == email for club in clubs):
            flash('Veuillez vous connecter avant de réserver.')
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club['email'] == email), None)
    if club is None:
        session.clear()
        flash('Adresse e-mail inconnue. Veuillez vérifier votre saisie.')
        return redirect(url_for('index'))
    session['club_email'] = club['email']
    return render_template('welcome.html',club=club,competitions=get_upcoming_competitions())


@app.route('/book/<competition>/<club>')
@login_required
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    if foundClub is None:
        flash('Club inconnu. Veuillez vérifier le lien de réservation.')
        return redirect(url_for('index'))
    if foundClub['email'] != session.get('club_email'):
        flash('Vous ne pouvez réserver que pour votre club.')
        return redirect(url_for('index'))
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundCompetition is None:
        flash('Compétition inconnue. Veuillez vérifier le lien de réservation.')
        return redirect(url_for('index'))
    if not is_competition_upcoming(foundCompetition):
        flash('Cette compétition est passée ou sa date est invalide.')
        return render_template('welcome.html', club=foundClub, competitions=get_upcoming_competitions())
    if int(foundCompetition.get('numberOfPlaces', 0)) <= 0:
        flash('Cette compétition est complète.')
        return render_template('welcome.html', club=foundClub, competitions=get_upcoming_competitions())
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
@login_required
def purchasePlaces():
    club = next(c for c in clubs if c['email'] == session['club_email'])
    upcoming_competitions = get_upcoming_competitions()
    competition_name = request.form.get('competition', '').strip()
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    if competition is None:
        flash('Compétition absente ou inconnue.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    if not is_competition_upcoming(competition):
        flash('Cette compétition est passée ou sa date est invalide.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    if int(competition.get('numberOfPlaces', 0)) <= 0:
        flash('Cette compétition est complète.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    try:
        placesRequired = int(request.form.get('places', ''))
    except (TypeError, ValueError):
        flash('Veuillez saisir un nombre entier de places valide.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    if placesRequired < 0:
        flash('La quantité de places ne peut pas être négative.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    if placesRequired == 0:
        flash('Une réservation doit inclure au moins une place.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    if placesRequired > int(competition['numberOfPlaces']):
        flash('La quantité demandée dépasse le nombre de places disponibles.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    bookedPlacesByClub = competition.get('bookedPlacesByClub', {})
    placesAlreadyBooked = int(bookedPlacesByClub.get(club['name'], 0))
    if placesAlreadyBooked + placesRequired > 12:
        flash('Un club ne peut pas réserver plus de 12 places pour une compétition.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    clubPoints = int(club['points'])
    if clubPoints < placesRequired:
        flash('Le club ne dispose pas de suffisamment de points.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    clubSnapshot = deepcopy(club)
    competitionSnapshot = deepcopy(competition)
    try:
        clubFileSnapshot = Path(CLUBS_FILE).read_text()
        competitionFileSnapshot = Path(COMPETITIONS_FILE).read_text()
    except OSError:
        flash('La réservation n’a pas pu être enregistrée. Aucune donnée n’a été modifiée.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = str(clubPoints - placesRequired)
    bookedPlacesByClub[club['name']] = placesAlreadyBooked + placesRequired
    competition['bookedPlacesByClub'] = bookedPlacesByClub
    try:
        saveCompetitions()
        saveClubs()
    except (OSError, TypeError):
        club.clear()
        club.update(clubSnapshot)
        competition.clear()
        competition.update(competitionSnapshot)
        for filePath, fileSnapshot in (
            (CLUBS_FILE, clubFileSnapshot),
            (COMPETITIONS_FILE, competitionFileSnapshot),
        ):
            try:
                Path(filePath).write_text(fileSnapshot)
            except OSError:
                app.logger.exception('Échec de la restauration de %s après une erreur de sauvegarde.', filePath)
        flash('La réservation n’a pas pu être enregistrée. Aucune donnée n’a été modifiée.')
        return render_template('welcome.html', club=club, competitions=upcoming_competitions)
    placeLabel = 'place' if placesRequired == 1 else 'places'
    flash(f'Réservation confirmée : {placesRequired} {placeLabel}.')
    return render_template('welcome.html', club=club, competitions=get_upcoming_competitions())


@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
