import json
from functools import wraps
from flask import Flask,render_template,request,redirect,flash,url_for,session

CLUBS_FILE = 'clubs.json'
COMPETITIONS_FILE = 'competitions.json'


def loadClubs():
    with open(CLUBS_FILE) as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(COMPETITIONS_FILE) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def saveClubs():
    with open(CLUBS_FILE, 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)


def saveCompetitions():
    with open(COMPETITIONS_FILE, 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

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
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    session['club_email'] = club['email']
    return render_template('welcome.html',club=club,competitions=competitions)


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
    return render_template('booking.html',club=foundClub,competition=foundCompetition)


@app.route('/purchasePlaces',methods=['POST'])
@login_required
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = next(c for c in clubs if c['email'] == session['club_email'])
    try:
        placesRequired = int(request.form.get('places', ''))
    except (TypeError, ValueError):
        flash('Veuillez saisir un nombre entier de places valide.')
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired < 0:
        flash('La quantité de places ne peut pas être négative.')
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired == 0:
        flash('Une réservation doit inclure au moins une place.')
        return render_template('welcome.html', club=club, competitions=competitions)
    if placesRequired > int(competition['numberOfPlaces']):
        flash('La quantité demandée dépasse le nombre de places disponibles.')
        return render_template('welcome.html', club=club, competitions=competitions)
    clubPoints = int(club['points'])
    if clubPoints < placesRequired:
        flash('Le club ne dispose pas de suffisamment de points.')
        return render_template('welcome.html', club=club, competitions=competitions)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = str(clubPoints - placesRequired)
    saveCompetitions()
    saveClubs()
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
