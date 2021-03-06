#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# one to many: show to artist, show to venue
# many to many past shows to venue and upcoming shows to venue

past_shows_venue = db.Table('past_shows',
    db.Column('Venue_id', db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE")),
    db.Column('Show_id', db.Integer, db.ForeignKey('show.id', ondelete="CASCADE"))
)

upcoming_shows_venue = db.Table('upcoming_shows',
    db.Column('Venue_id', db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE")),
    db.Column('Show_id', db.Integer, db.ForeignKey('show.id', ondelete="CASCADE"))
)

past_shows_artist = db.Table('past_shows_artist',
    db.Column('Artist_id', db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE")),
    db.Column('Show_id', db.Integer, db.ForeignKey('show.id', ondelete="CASCADE"))
)

upcoming_shows_artist = db.Table('upcoming_shows_artist',
    db.Column('Artist_id', db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE")),
    db.Column('Show_id', db.Integer, db.ForeignKey('show.id', ondelete="CASCADE"))
)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    num_upcoming_shows = db.Column(db.Integer)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    past_shows = db.relationship('Show', secondary=past_shows_venue,
                                 backref=db.backref('venue_past', lazy=True))
    upcoming_shows = db.relationship('Show', secondary=upcoming_shows_venue,
                                     backref=db.backref('venue_upcoming', lazy=True))
    past_shows_count = db.Column(db.Integer, default=0)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows = db.relationship('Show', secondary=past_shows_artist,
                                 backref=db.backref('artist_past', lazy=True))
    upcoming_shows = db.relationship('Show', secondary=upcoming_shows_artist,
                                     backref=db.backref('artist_upcoming', lazy=True))
    show = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    venues = Venue.query.all()
    data = []
    cities = {}

    for venue in venues:
        print(type(venue.upcoming_shows_count))
        if venue.city in cities:
            idx = cities[venue.city]
            data[idx][venues].append({"id": venue.id,
                                      "name": venue.name,
                                      "num_upcoming_shows": venue.upcoming_shows_count})
        else:
            cities[venue.city] = len(data)
            data.append({"city": venue.city,
                         "state": venue.state,
                         "venues": [{"id": venue.id,
                                     "name": venue.name,
                                     "num_upcoming_shows": venue.upcoming_shows_count}]})
    # data = [{
    # "city": "San Francisco",
    # "state": "CA",
    # "venues": [{
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "num_upcoming_shows": 0,
    # }, {
    #   "id": 3,
    #   "name": "Park Square Live Music & Coffee",
    #   "num_upcoming_shows": 1,
    # }]
    # }, {
    # "city": "New York",
    # "state": "NY",
    # "venues": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    query_results = db.session.query(Venue).\
      filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))
    query_result_data = []
    for result in query_results:
        query_result_data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": result.upcoming_shows_count})
    response = {
        "count": query_results.count(),
        "data": query_result_data
    }
    # response={
    # "count": 1,
    # "data": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
    # }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    for show in venue.past_shows:
        artist = Artist.query.get(show.artist_id)
        past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    for show in venue.upcoming_shows:
        artist = Artist.query.get(show.artist_id)
        upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })
    data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": venue.past_shows_count,
    "upcoming_shows_count": venue.upcoming_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        venue = Venue(name=name,
                      city=city,
                      state=state,
                      address=address,
                      phone=phone,
                      image_link=image_link,
                      genres=genres,
                      facebook_link=facebook_link,
                      past_shows_count=0,
                      seeking_talent=False,
                      upcoming_shows_count=0
                      )

        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []

    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})
    # data=[{
    # "id": 4,
    # "name": "Guns N Petals",
    # }, {
    # "id": 5,
    # "name": "Matt Quevedo",
    # }, {
    # "id": 6,
    # "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query_results = db.session.query(Artist). \
        filter(Artist.name.ilike('%' + request.form.get('search_term', '') + '%'))
    query_result_data = []
    for result in query_results:
        query_result_data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": result.upcoming_shows_count})
    response = {
        "count": query_results.count(),
        "data": query_result_data
    }

    # response={
    # "count": 1,
    # "data": [{
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "num_upcoming_shows": 0,
    # }]
    # }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    past_shows = []

    for show in artist.past_shows:
      venue = Venue.query.get(show.venue_id)
      past_shows.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(show.start_time)
      })

    upcoming_shows = []
    for show in artist.upcoming_shows:
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(show.start_time)
      })
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": artist.past_shows_count,
      "upcoming_shows_count": artist.upcoming_shows_count,
    }


    # data1={
    # "id": 4,
    # "name": "Guns N Petals",
    # "genres": ["Rock n Roll"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "326-123-5000",
    # "website": "https://www.gunsnpetalsband.com",
    # "facebook_link": "https://www.facebook.com/GunsNPetals",
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # "past_shows": [{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
    # }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    try:
      db.session.query(Artist).filter(Artist.id == artist_id).update(
          {"name": form.name.data,
           "genres": form.genres.data,
           "city": form.city.data,
           "state": form.state.data,
           "phone": form.phone.data,
           "facebook_link": form.facebook_link.data,
           }
      )
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
      print(e)
      error = True
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).update(
        {"name": form.name.data,
        "city": form.city.data,
        "state": form.state.data,
        "address": form.address.data,
        "phone": form.phone.data,
        "image_link": form.image_link.data,
        "genres": form.genres.data,
        "facebook_link": form.facebook_link.data})

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        artist = Artist(name=name,
                        city=city,
                        state=state,
                        phone=phone,
                        image_link=image_link,
                        genres=genres,
                        facebook_link=facebook_link,
                        past_shows_count=0,
                        seeking_venue=False,
                        upcoming_shows_count=0
                        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = []
    for show in shows:
      venue = Venue.query.get(show.venue_id)
      artist = Artist.query.get(show.artist_id)

      data.append({"venue_id": venue.id,
                        "venue_name": venue.name,
                        "artist_id": artist.id,
                        "artist_name": artist.name,
                        "artist_image_link": artist.image_link,
                        "start_time": str(show.start_time)})
    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data

        show = Show(artist_id=artist_id,
                    venue_id=venue_id,
                    start_time=start_time)

        #update artists and venues
        artist = Artist.query.get(artist_id)
        venue = Venue.query.get(venue_id)
        if datetime.now() > start_time:
            artist.past_shows.append(show)
            artist.past_shows_count = artist.past_shows_count + 1
            venue.past_shows.append(show)
            venue.past_shows_count = venue.past_shows_count + 1
        else:
            artist.upcoming_shows.append(show)
            artist.upcoming_shows_count = artist.upcoming_shows_count + 1
            venue.upcoming_shows.append(show)
            venue.upcoming_shows_count = venue.upcoming_shows_count + 1

        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
