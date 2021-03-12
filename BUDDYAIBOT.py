import discord
import datetime
import pytz
import wikipedia
from googlesearch import search
from discord.ext import commands
from discord.utils import get
import youtube_dl
from gtts import gTTS
import json
import os

data = "Sorry"
keywords_basic = {"what'syourname": "```Hi, My name is BUDDY. Its nice to meet you. What can i do for you ?```",
                          "howareyou": "```Great.. Thanks for asking. How may I help ?```",
                          "whatisyourname": "```Hi, My name is BUDDY. Its nice to meet you. What can i do for you ?```",
                          "whatareyoudoing": "```I am helping you. Ask me, if anything comes by...```",
                          "heybuddy": "```Hello. How are you ?```",
                          "hibuddy": "```Hello. How are you ?```",
                          "hellobuddy": "```Hi. how are you ?```",
                          "iamfine": "```Great! How can i help ?```",
                          "good": "```You are welcome..```",
                          "hello": "```Hi. How are you ?```",
                          "hola": "```Hi. How are you ?```",
                          "hi": "```Hello, How are you ?```",
                          "hey": "```Hello, How are you ?```"}

keywords_wish = ["goodmorning", "goodafternoon", "goodevening", "goodnight"]

keywords_date = ["today", "date", "whatisthedate", "whatistoday", "whatisthemonth", "whatistheday", "whatistheyear", "month", "year"]

keywords_clock = ["whatisthetime", "time", "what'sthetime"]

def read_token():
    with open('app.json') as f:
        appData = json.load(f)
    return appData['env']['TOKEN']['value']

def read_clientid():
    with open('app.json') as f:
        appData = json.load(f)
    return appData['env']['CLIENT_ID']['value']

def read_audioChannelid():
    with open('app.json') as f:
        appData = json.load(f)
    return appData['env']['AUDIOCHANNEL_ID']['value']

def read_ChannelList():
    with open('app.json') as f:
        appData = json.load(f)
    return appData['env']['Channels_Valid']['value']

def read_TimeZone():
    with open('app.json') as f:
        appData = json.load(f)
    return appData['env']['TIMEZONE']['value']



tz = pytz.timezone(read_TimeZone)


token = read_token()

client = discord.Client()

client = commands.Bot(command_prefix="")

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


global channel_audio

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

def get_today(text):
    today_day = text[8:10]
    today_month = text[5:7]
    today_year = text[0:4]
    day_week = today_day + " " + today_month + " " + today_year
    today_month = MONTHS[int(today_month) - 1]
    day_week = datetime.datetime.astimezone(tz).today().weekday()
    end = "th of "
    if int(today_day[1]) == 1:
        end = "st of "
    elif int(today_day[1]) == 2:
        end = "nd of "
    elif int(today_day[1]) == 3:
        end = "rd of "
    today = "It is " + DAYS[day_week] +", the "+ today_day + end + today_month + ", " + today_year
    return today

def get_search(text):
    try:
         url = "https://www.google.com/search?q="
         ans = []
         i = 0
         for j in search(text, tld='com', lang='en', num=5, start=0, stop=5, pause=2.0):
             ans.append(j)
         ans.pop(-1)
         ans.append("Finished Looking. Need Anything else ?")
         return ans
    except:
        print("Sorry. Couldnt Search for it.")

def get_wish(string):
    now = datetime.datetime.now()
    now = now.astimezone(tz)
    curr_time = str(now)
    curr_time = curr_time[11:16]
    if string == "goodmorning":
        if int(curr_time[:2]) < 12:
            return "Good Morning, How can I help ?"
        elif int(curr_time[:2]) >= 12 and int(curr_time[:2]) < 16:
            return "Its Good Afternoon. How can I help ?"
        elif int(curr_time[:2]) > 16 and int(curr_time[:2]) < 24:
            return "Its Good Evening. How can I help ?"

    elif string == "goodafternoon":
        if int(curr_time[:2]) < 12:
            return "Its Good Morning, How can I help ?"
        elif int(curr_time[:2]) >= 12 and int(curr_time[:2]) < 16:
            return "Good Afternoon. How can I help ?"
        elif int(curr_time[:2]) > 16 and int(curr_time[:2]) < 24:
            return "Its Good Evening. How can I help ?"

    elif string == "goodevening":
        if int(curr_time[:2]) < 12:
            return "Its Good Morning, How can I help ?"
        elif int(curr_time[:2]) >= 12 and int(curr_time[:2]) < 16:
            return "Its Good Afternoon. How can I help ?"
        elif int(curr_time[:2]) > 16 and int(curr_time[:2]) < 24:
            return "Good Evening. How can I help ?"

    elif string == "goodnight":
        if int(curr_time[:2]) < 12:
            return "Good Night, Sweet Dreams."
        else:
            return "Night Night..."

@client.command(pass_context=True, aliases=['j','joi'])
async def join(ctx):
    global voice
    global channel_audio
    try:
        channel = ctx.message.author.voice.channel
        channel_audio = channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        await voice.disconnect()
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            print(f"The bot has connected to {channel}\n")

        await ctx.send(f"```Joined {channel}```")
    except:
        print("Call Error")
        await ctx.send("```You are not connected to voice!```")

@client.command(pass_context=True, aliases=['l','lea'])
async def leave(ctx):
    global channel_audio
    channel = channel_audio#ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Bot has left {channel}")
        await ctx.send(f"```Left {channel}```")
    else:
        print("Already Left")
        await ctx.send(f"```Not in {channel}```")

@client.command(pass_context=True, aliases=['p','pla'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed song")
    except PermissionError:
        print("Trying But Failed!!")
        await ctx.send("```Error. Music Couldnt be played```")
        return

    await ctx.send("```Searching Youtube...```")

    try:
        global channel_audio
        channel = client.get_channel(read_audioChannelid())
        channel_audio = channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        await voice.disconnect()
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            print(f"The bot has connected to {channel}\n")

        await ctx.send(f"```Joined {channel}```")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading...")
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"Renaming {file}\n")
                os.rename(file, "song.mp3")

        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 501

        nname = name.rsplit("-", 2)
        await ctx.send(f"```playing {nname[0]} in channel {channel}```")
        print("Playing\n")

    except:
        print("Call Error")
        await ctx.send("```Try connecting to any voice channel...```")


@client.command(pass_context=True, aliases=['pa','pau'])
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music Paused")
        voice.pause()
        await ctx.send("```Music Paused```")
    else:
        print("Music not Playing..")
        await ctx.send("```Cant Pause if nothing is playing```")

@client.command(pass_context=True, aliases=['r','res'])
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resuming Music")
        voice.resume()
        await ctx.send("```Resumed Music```")
    else:
        print("Music not Paused..")
        await ctx.send("```Cant Resume if music is not played```")


@client.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Stopping Music")
        voice.stop()
        await ctx.send("```Music Stopped```")
    else:
        print("Music not Stopped..")
        await ctx.send("```Cant Stop if music is not played```")


@client.command(pass_context=True, aliases=["search"])
async def google_search(ctx):
    global data
    f = "```Sure. Going Online for " + data[7:] + "```"
    await ctx.send(f)
    await ctx.send("```You Have Results from :```")
    ans = get_search(data[7:])
    for i in ans:
        await ctx.send("```" + str(i) + "```")

@client.command(pass_context=True, aliases=["define"])
async def wiki_search(ctx):
    global data
    try:
        ind = 7
        data = data[ind:]
        dataW = wikipedia.summary(data)

        j = -1
        s = 0
        for i in dataW:
            j = j + 1
            if '.' in i and s < 3:
                s = s + 1
                indexC = j

        await ctx.send("```" + str(wikipedia.summary(data)[:indexC + 1]) + "```")

    except:
       await ctx.send("```Sorry. Try using more words to enhance your experience...```")

@client.command(pass_context=True, aliases=["!users"])
async def member_count(ctx):
    id = client.get_guild(716557689144082443)
    await ctx.send(f"""```{id.member_count} Members ```""")

@client.command(pass_context=True, aliases=list(keywords_basic.keys()))
async def basic(ctx):
    global data
    question = list(keywords_basic.keys())
    for phrase in question:
        if phrase in data:
            await ctx.send(keywords_basic[phrase])

@client.command(pass_context=True, aliases=keywords_wish)
async def basic_wish(ctx):
    global data
    for phrase in keywords_wish:
        if phrase in data:
            await ctx.send("```" + str(get_wish(phrase)) + "```")

@client.command(pass_context=True, aliases=keywords_date)
async def today_date(ctx):
    global data
    for phrase in keywords_date:
        if phrase in data:
            now = datetime.datetime.now()
            now = now.astimezone(tz)
            curr_date = str(now)
            await ctx.send("```" + get_today(curr_date[0:10]) + "```")

@client.command(pass_context=True, aliases=keywords_clock)
async def date_clock(ctx):
    global data
    for phrase in keywords_clock:
        if phrase in data:
            now = datetime.datetime.now()
            now = now.astimezone(tz)
            curr_time = str(now)
            curr_time = curr_time[11:16]
            if int(curr_time[:2]) < 12:
                await ctx.send("```Its " + curr_time + " am```")
            elif int(curr_time[:2]) > 12:
                hours = int(curr_time[:2]) - 12
                min = int(curr_time[3:])
                now_time = str(hours) + ":" + str(min)
                await ctx.send("```Its " + now_time + " pm```")
            elif int(curr_time[:2]) == 12:
                await ctx.send("```Its " + curr_time + " pm```")

@client.event
async def on_message(message):
    channels = read_ChannelList
    if message.author.bot:
        print(message.content)
    elif str(message.channel) in channels and str(message.author):
        bot_code = str(message.content)[:22]
        msg_limit = 23
        bc1 = "<@!" + str(read_clientid()) + ">"
        bc2 = "<@" + str(read_clientid()) + "> "
        if bot_code == bc1 or bot_code == bc2:
            if bot_code == bc2:
                msg_limit = 22
            original = str(message.content)[msg_limit:]
            com = original[0:4].lower()
            music = original[4:]
            google = original[0:6].lower()

            message.content = original

            if com == "play":
                message.content = com + music
                print(com + "Message " + message.content)
            elif google == "search" or google == "define":
                message.content = message.content.lower()
                print(google + "Message " + message.content)
            else:
                message.content = message.content.lower().replace(" ", "")
                print(google + "Message " + message.content)

            global data
            data = str(message.content)
            await client.process_commands(message)

            if data == "!delete":
                await message.channel.purge(limit=125)
        else:
            print(bot_code)
            print(f"""User: {message.author} talking {message.content}, in channel {message.channel}""")
    # else:
    #     await message.channel.send("```Invalid User!!```")
    #     print(f"""User: {message.author} tried to do command {message.content}, in channel {message.channel}""")



client.run(token)
