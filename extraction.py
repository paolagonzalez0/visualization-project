
from dotenv import load_dotenv
import os
import base64
from requests import post,get
import json
import pandas as pd

# Load local environment
load_dotenv()

# Fetch Spotify API client id and client secret from local environment (for privacy)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Get token for further authentication and requests
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

# Get access to API using bearer token
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Search for an artist using their name
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist exists with this name...")
        return None
    return json_result[0]

# Get songs of the artist using their artist_id
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result

# Get genres of an artist using their artist_id
def get_artist_genres(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)
    return json_result["genres"]

## Additional functions 

# Split an element for easier parsing
def split_element(element):
    return element.split(sep=",")

# Check if value is a float data type
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# Split artist names and artist ids into separate rows
def divide_artists(dataframe):
    rows = dataframe.to_dict(orient='records')
    data_rs = []
    for idx,row in enumerate(rows):
        if "," not in row["artist_id"]:
            data_rs.append(row)
        else:
            artists_id_list = split_element(row["artist_id"])
            artist_names = split_element(row["artist_name"])
            for i in range(len(artists_id_list)):
                new_row = rows[idx].copy()
                if artists_id_list[i] == "1WsYCXdezMjn0KoIrLvMmC":
                    new_row["artist_id"] = "6eUKZXaKkcviH0Ku9w2n3V"
                    new_row["artist_name"] = "Ed Sheeran"
                else:
                    new_row["artist_id"] = artists_id_list[i]
                    new_row["artist_name"] = artist_names[i]
                data_rs.append(new_row)
    return pd.DataFrame(data_rs)

# Split the genres in each row of data into separate rows
def divide_genres(dataframe):
    rows = dataframe.to_dict(orient='records')
    data_rrs = []
    for idx,row in enumerate(rows):
        if "," not in row["genres"]:
            data_rrs.append(row)
        else:
            subgenres = split_element(row["genres"])
            for i in range(len(subgenres)):
                new_row = rows[idx].copy()
                new_row["genres"] = subgenres[i]
                data_rrs.append(new_row)
    return pd.DataFrame(data_rrs)

# Split artists and genres into separate rows
def divide_all(dataframe):
    data_rs = divide_artists(dataframe)
    data_rrrs = divide_genres(data_rs)
    return pd.DataFrame(data_rrrs)

def get_latin_genres():
     return ['latin','latin talent show','reggae fusion','grupera','tropical alternativo','mariachi',
            'urbano chileno', 'argentine hip hop', 'cumbia peruana', 'pop electronico','trap latino',
            'musica mexicana', 'norteno','ranchera','rap latina','latin alternative','cumbia',
            'indietronica', 'latintronica','mexican pop','reggaeton','puerto rican indie','corrido', 'corridos tumbados',
            'bachata dominicana','banda sinaloense','pop argentino', 'spanish pop','reggaeton colombiano',
            'rap canario','r&b en espanol', 'latin viral pop','sad sierreno', 'colombian pop',
            'trap colombiano', 'indie anthem-folk', 'puerto rican pop', 'sertanejo universitario',
            'urbano mexicano','salsa colombiana','musica potosina','funk carioca','pop reggaeton',
            'banda', 'mexican rock', 'cumbia pop','bachata','rap dominicano', 'tejano', 
            'latin hip hop', 'reggaeton flow', 'urbano latino','musica costena', 'sierreno', 
            'norteno-sax','latin pop','mambo chileno', 'duranguense', 'pop venezolano',
            'concurso de talentos argentino', 'la indie', 'rock en espanol','vallenato',
            'peruvian indie','latin rock', 'trap boricua', 'cantautora mexicana', 'latin arena pop', 
            'trap argentino', 'modern salsa', 'cumbia sonorense','corridos tumbados','latin christian',
            'latin christmas', 'latin electronica','latin jazz','latin metal','pagode baiano',
            'pop ostentacao','funk das antigas','panamanian pop','pop nacional']

# Determine if an artist, track, or genre is latin/nonlatin
def is_latin(row):
    latin_genres = get_latin_genres()
    status = "unknown"
    if "," not in row["genres"]:
        if row["genres"] in latin_genres:
            status = "latin"
        elif row["genres"] == "none":
            status = "unknown"
        else:
            status = "nonlatin"
    else:
        for genre in split_element(row["genres"]):
            if genre in latin_genres:
                status = "latin"
            else:
                status = "nonlatin"
    return status