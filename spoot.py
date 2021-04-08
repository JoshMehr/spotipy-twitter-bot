from signin import *
import spotipy
import spotipy.util as util
import twitter
import json

api = twitter.Api(consumer_key=c_key, consumer_secret=c_secret, access_token_key=a_token, access_token_secret=a_token_secret)

def playlistLen(playlist_tracks):
    return len(playlist_tracks)

def get_playlist_tracks(playlist_id, spot):
    plist = spot.playlist_tracks(playlist_id, fields='items, uri, name, id, total, next')
    trackz = plist['items']
    while plist['next']:
        plist = spot.next(plist)
        trackz.extend(plist['items'])
    return trackz

def playlistContains(playlist_tracks,top_id):
    plen = playlistLen(playlist_tracks)
    # print(plen)
    for i in range(0,plen):
        # print()
        # print("top_id: ", top_id, "\nplaylist tracks: ", playlist_tracks[i]['track']['name'])
        # print(top_id == playlist_tracks[i]['track']['name'])
        if top_id == playlist_tracks[i]['track']['name']:
            return True
    return False


username = 'majorleagueturtle'
top_tracks_id = '5TvBNo6PTKAjBdD55yRJDs'

def lambda_handler(event, context):
    token = util.prompt_for_user_token(username, 'user-top-read playlist-modify-public playlist-read-collaborative',
                                       client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                       redirect_uri=SPOTIPY_REDIRECT_URI)
    # client_credentials_manager = SpotifyClientCredentials()
    if token:
        sp = spotipy.Spotify(auth=token, requests_timeout=50)

        tracks = get_playlist_tracks(top_tracks_id, sp)
        # print(tracks[0]['track']['name'])
        results = sp.current_user_top_tracks(limit=(playlistLen(tracks) + 300), time_range='short_term')
        # print(results['items'][0]['name'])
        tweet = "\nJosh's current most played track is:\n"
        for i, track in enumerate(results['items']):
            # top = track['id']
            top = track['name']
            topp = track['id']
            # print(track['id'])
            # print(track['name'])
            # print(track['external_urls']['spotify'])
            # print(track['id'])
            # print(i, track['name'], '//', track['artists'][0]['name'])
            boolean = not playlistContains(tracks, top)
            # print("ah", boolean)
            if boolean:
                sp.user_playlist_add_tracks(user=username,playlist_id=top_tracks_id,tracks=[topp])
                tweet += track['name'] + " by " + track['artists'][0]['name']
                break
        tweet += "\nIt was added to https://open.spotify.com/playlist/5TvBNo6PTKAjBdD55yRJDs?si=K7gANBBTRcaCrRwdquVBhw"

        print(tweet)
        status = api.PostUpdate(status=tweet)
    else:
        print("Can't get token for", username)

    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }


