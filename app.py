#importing libraries
import spotipy #lib used as a spotify api wrapper
from spotipy.oauth2 import SpotifyOAuth #module, used for oauth autentication (permission from spotify)
import chatgpt #my chatgpt file, containing the backend logic to call the openai api.
from flask import Flask, render_template, url_for, session, redirect, request #flask: web-dev miniframework
import time #the clue is in the name
#f



CLIENT_ID = "YOUR SPOTIFY CLIENT ID KEY GOES HERE" #spotify client id. https://developer.spotify.com/
CLIENT_SECRET = "YOUR SPOTIFY CLIENT SECRET KEY GOES HERE" #spotify client secret
SCOPE = "playlist-modify-private, playlist-modify-public, user-read-recently-played" #spotify scope (what will the api get access to)
#ATTENTION: CLIENT_ID and CLIENT_SECRET must not be shared. it's better implemented as environment variable.

app = Flask(__name__) #init flask app
app.secret_key="fjfkl511ff559" #randomized. No idea what it's used for.
app.session_cookie_name = "Chat to Spotify Cookie" #defining the name of the Cookie which will save user's info.
TOKEN_INFO = "token_info" #just to avoid name issues. 'token_info' is one of the parameters of a token.



@app.route('/', methods=['POST', 'GET']) #@app.route() defines a route in Flask. A route is like a link/new page.
def homepage():
    if(request.method=='POST'): #if it gets a POST methos, it means the Submit button was presses.
        if request.form.get('btn_login') == 'btn_login': 
            return redirect(url_for('login', _external=True)) #user ir redirected to login page
    return render_template("homepage.html")


@app.route('/login')
def login():
    oauthObj = createOauth() #an oauth object is created
    oauth_url = oauthObj.get_authorize_url() #we get the authorization url from the object and redirect the user
    return redirect(oauth_url)


@app.route('/logged')
def logged():
    oauthObj = createOauth() #another obj is created
    session.clear()
    code = request.args.get('code') #we get the code from the request
    token = oauthObj.get_access_token(code) #we get the token from the oauth obj
    print(token)
    session[TOKEN_INFO] = token #we assign the token in the session with the token value
    return redirect(url_for('searchsong', _external=True))

@app.route('/searchsong', methods=['POST', 'GET']) #defines the request methods. Otherwise it'll return an error.
def searchsong():
    if(request.method=='GET'): #if the request is a GET, it means the form is no in action yet, so it must return the own page.
        return render_template("searchsong.html")
    elif(request.method=='POST'): #if the request is a POST, it means the submit button has been hit. 
        #so we get the data coming from the form ('prompt' and 'playlist_name' are the text box names)
        prompt = request.form.get('prompt') #we get the prompt and the playlist name from the form
        playlist_name = request.form.get('playlist_name')
        try:
            jsonObj = chatgpt.callPrompt(prompt) #we call th callPrompt function, which returns a jsonObj with the songs/artists info
            createplaylist(jsonObj, playlist_name, prompt) #the create playlist function is called
        except Exception as exc:
            print("Searchsong except: ", exc) #we print the except. It helps debugging.
            return redirect(url_for('searchsong',   _external=True))
        
    return render_template("searchsong.html")


def createplaylist(jsonObj, playlist_name, prompt):
    try:
        token = getNewToken() #we get a new token from the current token
    except Exception as exc:
        print("createplaylist except: ", exc)
        redirect(url_for("login", _external=True))

    spotifyObj = spotipy.Spotify(auth=token['access_token']) #a spotify object is created, using spotipy wrapper and passing the access_token
    user = spotifyObj.current_user() #we get info about the current user (the user logged in)
    USER_ID = user['id'] #getting user id
    playlist = spotifyObj.user_playlist_create(user=USER_ID, name=playlist_name, public=True, collaborative=False, 
                                               description="created with A.I with the prompt playlists with..."+prompt) #an empty playlist is created
    playlist_id = playlist['id']


    for i in range(0, len(jsonObj['songs'])): #iteration over the jsonObj
        try:
            artist = jsonObj['songs'][i]['artist'] #artist and track names, from the jsonObj
            track =  jsonObj['songs'][i]['song']
            query = "track:"+track+" artist:"+artist #building a query to make it easier
            songURI = spotifyObj.search(q=query, type='track', limit=1, offset=0)['tracks']['items'][0]['uri'] #we get the song URI by searching with spotify method
            print(artist + " - " + track + " - URI: " + songURI)
            spotifyObj.playlist_add_items(playlist_id, items=[songURI], position=None) #we add the song in the playlist
            print("Song added to playlist")
        except:
            continue #if we catch an excepct, we continue. This way, if a song can't be added to playlist, we just 'skip' it.
    print("Playlist successfully finished!")

   
   
    


def createOauth(): #creates an oauh obj
    return SpotifyOAuth( #oauth method 
        client_id=CLIENT_ID, 
        client_secret=CLIENT_SECRET, 
        redirect_uri=url_for('logged', _external=True), 
        scope=SCOPE)

def getNewToken(): #getnewtoken method
    token = session.get(TOKEN_INFO, None)
    if not token:
        raise "exception"
    now = int(time.time())
    isExpired = token["expires_in"] - now < 60
    if(isExpired):
        oauthObj = createOauth()
        token = oauthObj.refresh_access_token(token['refresh_token'])
    return token
