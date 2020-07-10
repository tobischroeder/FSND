#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys
from config import app, db
from models import Artist, Venue, Show 

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
@app.template_filter('datetime')
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

# List all venues
@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.all()
  for venue in venues:
    if not any(d.get('city') == venue.city for d in data):
      data.append(dict(city = venue.city, state = venue.state, venues = [dict(id = venue.id, name = venue.name, num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).count())]))
    else:
      city_index = next((index for (index, d) in enumerate(data) if d['city'] == venue.city))
      data[city_index]['venues'].append(dict(id = venue.id, name = venue.name, num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).count()))
      
  return render_template('pages/venues.html', areas=data)

# Search a specific venue
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response = dict(count = venues.count(), data = [])
  for venue in venues:
    response['data'].append(dict(id = venue.id, name = venue.name, num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id).count()))    

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Show a specific venue
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  data = dict(id = venue.id, name = venue.name, genres = venue.genres, address= venue.address, city = venue.city, state = venue.state, phone = venue.phone, website = venue.website, facebook_link = venue.facebook_link, seeking_talent = venue.seeking_talent, seeking_description = venue.seeking_description, image_link = venue.image_link, past_shows = [], upcoming_shows = [], past_shows_count = 0, upcoming_shows_count = 0)
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.utcnow()).all()
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).all()
  
  for ps in past_shows:
    artist = Artist.query.filter_by(id=ps.artist_id).first()
    data['past_shows'].append(dict(artist_id = artist.id, artist_name = artist.name, artist_image_link = artist.image_link, start_time = datetime.strftime(ps.start_time, '%B %d %Y - %H:%M:%S')))
  data['past_shows_count'] = len(data['past_shows'])
  
  for us in upcoming_shows:
    artist = Artist.query.filter_by(id=us.artist_id).first()
    data['upcoming_shows'].append(dict(artist_id = artist.id, artist_name = artist.name, artist_image_link = artist.image_link, start_time = datetime.strftime(us.start_time, '%B %d %Y - %H:%M:%S')))
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_venue.html', venue=data)
  
# Create a new venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    data = request.form
    venue = Venue()
    venue.name = data['name']
    genres = []
    for (k, v) in data.items(multi=True):
      if k == 'genres':
        genres.append(v)
    venue.genres = genres
    venue.address = data['address']
    venue.city = data['city']
    venue.state = data['state']
    venue.phone = data['phone']
    venue.website = data['website']
    venue.facebook_link = data['facebook_link']
    venue.seeking_talent = 'seeking_talent' in data
    venue.seeking_description = data['seeking_description']
    venue.image_link = data['image_link']
    db.session.add(venue)
    db.session.commit()

  except:
    db.session.commit()
    error = True
    print(sys.exc_info())
  
  finally:
    db.session.close()

  if error:
    flash('ERROR: Venue ' + request.form['name'] + ' could not be listed!')
  else:
    flash('Venue ' + request.form['name'] + ' successfully listed!')
  
  return render_template('pages/home.html')

# delete a venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#---------------------------------------------------------------------------#
#  Artists
#---------------------------------------------------------------------------#

# List all artists
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append(dict(id = artist.id, name = artist.name))
  
  return render_template('pages/artists.html', artists=data)

# Search a specific artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response = dict(count = artists.count(), data = [])
  for artist in artists:
    response['data'].append(dict(id = artist.id, name = artist.name, num_upcoming_shows = Show.query.filter(Show.artist_id==artist.id).count()))    

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Show a specific artist
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  genres = [x for x in ''.join(',' if not e else e for e in artist.genres).split(',') if x]
  removetable = str.maketrans('', '', '{}')
  genres = [s.translate(removetable) for s in genres]
  data = dict(id = artist.id, name = artist.name, genres = genres, city = artist.city, state = artist.state, phone = artist.phone, website = artist.website, facebook_link = artist.facebook_link, seeking_venue = artist.seeking_venue, seeking_description = artist.seeking_description, image_link = artist.image_link, past_shows = [], upcoming_shows = [], past_shows_count = 0, upcoming_shows_count = 0)
  past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.utcnow()).all()
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.utcnow()).all()

  for ps in past_shows:
    venue = Venue.query.filter_by(id=ps.venue_id).first()
    data['past_shows'].append(dict(venue_id = venue.id, venue_name = venue.name, venue_image_link = venue.image_link, start_time = datetime.strftime(ps.start_time, '%B %d %Y - %H:%M:%S')))
  data['past_shows_count'] = len(data['past_shows'])
  
  for us in upcoming_shows:
    venue = Venue.query.filter_by(id=us.venue_id).first()
    data['upcoming_shows'].append(dict(venue_id = venue.id, venue_name = venue.name, venue_image_link = venue.image_link, start_time = datetime.strftime(us.start_time, '%B %d %Y - %H:%M:%S')))
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_artist.html', artist=data)

# get artist information
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id)
  form = dict(id = artist.id, name = artist.name, genres = artist.genres, city = artist.city, state = artist.state, phone = artist.phone, website = artist.website, facebook_link = artist.facebook_link, seeking_venue = artist.seeking_venue, seeking_description = artist.seeking_description, image_link = artist.image_link)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

# update artist information
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try: 
    artist = Artist.query.filter_by(id=artist_id)
    data = request.form
    artist.name = data['name']
    artist.genres = data['genres']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.website = data['website']
    artist.facebook_link = data['facebook_link']
    artist.seeking_venue = data['seeking_venue']
    artist.seeking_description = data['seeking_description']
    artist.image_link = data['image_link']

    db.session.add(artist)
    db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  
  finally:
    db.session.close()
  
  if error:
    flash('ERROR: Artist ' + request.form['name'] + ' could not be edited!')
    
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  
  return redirect(url_for('show_artist', artist_id=artist_id))
    
  
# get venue information
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id)
  form = dict(id = venue.id, name = venue.name, genres = venue.genres, address = venue.address, city = venue.city, state = venue.state, phone = venue.phone, website = venue.website, facebook_link = venue.facebook_link, seeking_talent = venue.seeking_talent, seeking_description = venue.seeking_description, image_link = venue.image_link)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

# update venue information
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    data = request.form
    venue = Venue.query.filter_by(id=venue_id)
    venue.name = data['name']
    venue.genres = data['genres']
    venue.address = data['address']
    venue.city = data['city']
    venue.state = data['state']
    venue.phone = data['phone']
    venue.website = data['website']
    venue.facebook_link = data['facebook_link']
    venue.seeking_talent = data['seeking_talent']
    venue.seeking_description = data['seeking_description']
    venue.image_link = ['image_link']
    db.session.add(venue)
    db.session.commit()
  
  except:
    db.session.rollback()
    print(sys.exc_info)
    error = True

  finally:
    db.session.close()

  if error:
    flash('ERROR: Venue ' + request.form['name'] + ' could not be edited!')
  
  else:
    flash('Venue ' + request.form['name'] + ' successfully edited!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

# create new artist
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    data = request.form
    artist = Artist()
    artist.name = data['name']
    genres = []
    for (k, v) in data.items(multi=True):
      if k == 'genres':
        genres.append(v)
    artist.genres = genres
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.website = data['website']
    artist.facebook_link = data['facebook_link']
    artist.seeking_venue = 'seeking_venue' in data
    artist.seeking_description = data['seeking_description']
    artist.image_link = data['image_link']

    db.session.add(artist)
    db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())

  finally:
    db.session.close()
  
  if error:
    flash('ERROR: Artist ' + request.form['name'] + ' could not be listed!')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

#------------------------------------------------------------------#
#  Shows
#------------------------------------------------------------------#

# list all shows
@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = Venue.query.filter(Venue.id==show.venue_id).first()
    artist = Artist.query.filter(Artist.id==show.artist_id).first()
    data.append(dict(venue_id = venue.id, venue_name = venue.name, artist_id = artist.id, artist_name = artist.name, artist_image_link = artist.image_link, start_time = datetime.strftime(show.start_time, '%B %d %Y - %H:%M:%S')))

  return render_template('pages/shows.html', shows=data)

# create new show
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    data = request.form
    show = Show()
    show.venue_id = data['venue_id']
    show.artist_id = data['artist_id']
    show.start_time = data['start_time']

    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())

  finally:
    db.session.close()
  
  if error:
    flash('ERROR: Show could not be listed!')
  else:
    flash('Show successfully listed!')
  
  return render_template('pages/home.html')

# handle 404 error
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

#handle 500 error
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