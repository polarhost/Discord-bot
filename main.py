from flask import Flask, redirect, request, jsonify
import requests
import os
import discord
from discord.ext import tasks

app = Flask(__name__)

# Discord OAuth2 credentials from environment variables
client_id = os.getenv('CID')  # Discord client ID
client_secret = os.getenv('CS')  # Discord client secret
redirect_uri = 'https://polarbackendx.onrender.com/callback'  # Your specified redirect URI
scope = 'identify email guilds.join'  # Scopes for user information and guild joining

# Bot token (for adding users to your server)
bot_token = os.getenv('TOKEN')  # Bot token from environment variables
guild_id = os.getenv('GID')  # Guild ID from environment variables
role_id = os.getenv('ROLE_ID')  # Role ID to assign when users join

# Discord bot client
intents = discord.Intents.default()
intents.members = True  # Enable member intent
bot = discord.Client(intents=intents)

@app.route('/')
def home():
    discord_login_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
    return f'<h1>Login with Discord</h1><a href="{discord_login_url}">Login with Discord</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Error: No code provided'

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Get access token
    token_response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_json = token_response.json()

    if 'access_token' in token_json:
        access_token = token_json['access_token']

        # Fetch user info with the access token
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
        user_json = user_response.json()

        # Optionally fetch email if the scope is granted
        email = user_json.get('email')

        # Add user to the server using the guilds.join scope
        invite_headers = {
            'Authorization': f'Bot {bot_token}',
            'Content-Type': 'application/json'
        }
        invite_data = {'access_token': access_token}

        guild_response = requests.put(f'https://discord.com/api/guilds/{guild_id}/members/@me', headers=invite_headers, json=invite_data)

        if guild_response.status_code == 201:
            return f"""
                <h1>Welcome, {user_json['username']}!</h1>
                <p>Email: {email if email else 'No email provided'}</p>
                <p>You have been successfully added to the server.</p>
                <script>
                    window.location.href = "https://dash.polarhost.uk.to";  // Redirect after login
                </script>
            """
        else:
            return f"Error adding user to the server: {guild_response.json()}"

    else:
        return 'Error: Unable to get access token'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('Bot is online!')

@bot.event
async def on_member_join(member):
    # Assign the specified role to the member when they join
    role = discord.utils.get(member.guild.roles, id=int(role_id))
    if role:
        await member.add_roles(role)
        print(f'Assigned {role.name} to {member.name}')

# Run the bot
if __name__ == '__main__':
    bot.run(bot_token)
    app.run(host='0.0.0.0', port=5000)
