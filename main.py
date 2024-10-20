from flask import Flask, redirect, request, jsonify
import requests
import os

app = Flask(__name__)

# Discord OAuth2 credentials
client_id = 'CID'  # Replace with your actual client ID
client_secret = 'CS'  # Replace with your actual client secret
redirect_uri = 'https://polarhost.uk.to/callback'  # Replace with your actual redirect URI
scope = 'identify email guilds.join'

# Bot token for adding users to a server
bot_token = 'TOKEN'  # Replace with your bot token
guild_id = 'GID'  # Replace with your server ID

@app.route('/')
def home():
    return 'Welcome to PolarHost'

# The callback route where users are redirected after logging in
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Error: No code provided'

    # Exchange authorization code for access token
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    token_response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_json = token_response.json()
    
    if 'access_token' in token_json:
        access_token = token_json['access_token']
        
        # Fetch user info from Discord
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
        user_json = user_response.json()

        # Get user's email and avatar info
        email = user_json.get('email', 'No email provided')
        user_id = user_json['id']
        avatar_hash = user_json.get('avatar')
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png" if avatar_hash else "https://cdn.discordapp.com/attachments/1297308582282526762/1297322065342496838/pfp_round.png?ex=671580d3&is=67142f53&hm=f4240f0b2c885c68324f0bc9763db8af1683213299b25d85ce6c83db3ae9fe06&"
        
        # Invite user to server
        invite_headers = {
            'Authorization': f'Bot {bot_token}',
            'Content-Type': 'application/json'
        }
        invite_data = {
            'access_token': access_token
        }
        guild_response = requests.put(f'https://discord.com/api/guilds/{guild_id}/members/@me', headers=invite_headers, json=invite_data)

        if guild_response.status_code == 201:
            # After successful login and guild join, redirect user to the dashboard
            return redirect(f"https://polarhost.uk.to/dashboard?username={user_json['username']}&email={email}")
        else:
            return f"Error adding user to the server: {guild_response.json()}"
    else:
        return 'Error: Unable to get access token'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
