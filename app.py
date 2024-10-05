import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import time
from keep_alive import keep_alive
keep_alive()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix=",", intents=intents)

# Create a dictionary to track user cooldowns
cooldowns = {}

# Store the queue of TTS messages
tts_queue = asyncio.Queue()

# Cooldown settings
COOLDOWN_TIME = 5  # 5 seconds cooldown per user to prevent spamming

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Function to check if the user is on cooldown
def is_on_cooldown(user_id):
    if user_id in cooldowns and time.time() - cooldowns[user_id] < COOLDOWN_TIME:
        return True
    return False

# Function to update user cooldowns
def update_cooldown(user_id):
    cooldowns[user_id] = time.time()

@bot.command(name="joinvc")
async def join_vc(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            await channel.connect()
            await ctx.send(f"Joined {channel}")
        else:
            await ctx.send("I'm already in a voice channel!")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")

@bot.command(name="leavevc")
async def leave_vc(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name="talkvc")
async def talk_vc(ctx, gender: str, *, message: str):
    if ctx.voice_client:
        user_id = ctx.author.id
        
        # Check if the user is on cooldown
        if is_on_cooldown(user_id):
            remaining_time = round(COOLDOWN_TIME - (time.time() - cooldowns[user_id]), 1)
            await ctx.send(f"You're sending messages too fast! Try again in {remaining_time} seconds.")
            return

        if gender.lower() not in ["male", "female"]:
            await ctx.send("Please specify a valid gender ('male' or 'female').")
            return
        
        # Add the request to the queue
        await tts_queue.put((ctx, gender, message))
        
        # Process the queue
        if not ctx.voice_client.is_playing():
            await process_queue(ctx)
        
        # Update cooldown
        update_cooldown(user_id)
    else:
        await ctx.send("I'm not connected to a voice channel!")

async def process_queue(ctx):
    while not tts_queue.empty():
        ctx, gender, message = await tts_queue.get()
        
        # Generate TTS audio
        if gender.lower() == "male":
            tts = gTTS(text=message, lang='en', slow=False, tld="co.uk")  # UK accent for male
        else:
            tts = gTTS(text=message, lang='en', slow=False, tld="com")  # US accent for female
        
        # Save the audio to a file
        tts.save("tts.mp3")
        
        # Play the audio in the voice channel
        ctx.voice_client.play(discord.FFmpegPCMAudio("tts.mp3"))
        
        # Wait for the audio to finish playing
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        
        # Remove the audio file after playback
        os.remove("tts.mp3")

bot.run(os.environ['TOKEN'])
