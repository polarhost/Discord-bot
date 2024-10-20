from flask import Flask, redirect, request, jsonify
import requests
import os

app = Flask(__name__)

# Discord OAuth2 credentials from environment variables
client_id = os.getenv('CID')
client_secret = os.getenv('CS')
redirect_uri = 'https://polarbackendx.onrender.com/callback'  # Your specified redirect URI
scope = 'identify email guilds.join'

# Bot token (for creating invites)
bot_token = os.getenv('TOKEN')
guild_id = os.getenv('GID')

# Default profile picture URL
default_avatar_url = "https://cdn.discordapp.com/attachments/1297308582282526762/1297322065342496838/pfp_round.png?ex=671580d3&is=67142f53&hm=f4240f0b2c885c68324f0bc9763db8af1683213299b25d85ce6c83db3ae9fe06"

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

        # Get user's avatar and fallback to the provided default if none
        user_id = user_json['id']
        avatar_hash = user_json['avatar']
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png" if avatar_hash else default_avatar_url

        # Invite the user to the server using the guilds.join scope
        invite_headers = {
            'Authorization': f'Bot {bot_token}',
            'Content-Type': 'application/json'
        }
        invite_data = {
            'access_token': access_token
        }

        guild_response = requests.put(f'https://discord.com/api/guilds/{guild_id}/members/{user_id}', headers=invite_headers, json=invite_data)

        if guild_response.status_code == 201:
            # Successful invitation
            return redirect("https://dash.polarhost.uk.to")  # Redirect to the dashboard
        else:
            return f"Error adding user to the server: {guild_response.json()}"

    else:
        return 'Error: Unable to get access token'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
