import os
import spotipy
import constant
import random

from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BAD_BUNNY_URI = os.getenv('BAD_BUNNY_URI')
FB_CERT = os.getenv('PATH_TO_CERTIFICATE')
FB_DATABASE_URL = os.getenv('DATABASE_URL')

cred = credentials.Certificate(FB_CERT)
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': FB_DATABASE_URL
})
ref = db.reference('/')
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

bot = commands.Bot(command_prefix='!')
bb_albums = []


@bot.event
async def on_ready():
    global bb_albums
    bb_albums = get_albums(BAD_BUNNY_URI)
    print("Bot is connected")


@bot.command(name="bbalbums")
async def get_all_bb_albums(ctx):
    for album in bb_albums:
        await ctx.send(album['name'])
    await ctx.send('END OF LIST')


@bot.command(name="bbmood")
async def recommend_song_by_mood(ctx, mood):
    mood_upper = mood.upper()

    if mood_upper == 'HAPPY':
        songs_by_mood = get_songs_by_mood(mood_upper)
        await send_random_song(ctx, songs_by_mood, mood_upper)
    elif mood_upper == 'SAD':
        songs_by_mood = get_songs_by_mood(mood_upper)
        await send_random_song(ctx, songs_by_mood, mood_upper)
    elif mood_upper == 'ENERGETIC':
        songs_by_mood = get_songs_by_mood(mood_upper)
        await send_random_song(ctx, songs_by_mood, mood_upper)
    else:
        await ctx.send("That's not a mood, cabron")


async def send_random_song(ctx, songs_by_mood, mood):
    key, value = random.choice(list(songs_by_mood.items()))
    formatted_key = key.split(":")[-1]
    link = 'https://open.spotify.com/track/'+formatted_key
    await ctx.send(constant.RECOMMENDATION_MESSAGE.get(mood))
    await ctx.send(link)


@bot.command(name="bbyahyahyah")
async def a_function_for_ray(ctx):
    while (True):
        await ctx.send("bbyahyahyah")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if "bot" in message.content:
        random_message = constant.SASSY_COMEBACKS[random.randrange(len(constant.SASSY_COMEBACKS))]
        await message.channel.send(random_message)
    if "stfu" in message.content:
        await message.channel.send("That's what yo mama said last night")


@bot.event
async def on_command_error(ctx, error):
    await ctx.send('pero like why you being such a pendejo')


def get_songs_by_mood(mood):
    query = ref.order_by_child('mood').equal_to(mood)
    snapshot = query.get()
    return snapshot


def get_albums(name):
    results = spotify.artist_albums(name, album_type='album')
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    return albums


bot.run(TOKEN)
