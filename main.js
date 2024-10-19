const express = require('express');
const fetch = require('node-fetch');
const querystring = require('querystring');
const keep_alive = require('./keep_alive.js');

const app = express();
const port = 3000;

// Discord app credentials
const client_id = '1297105461182726197'; // Your client ID
const client_secret = 'YOUR_CLIENT_SECRET'; // Your client secret
const redirect_uri = 'https://polarhost.uk.to/callback'; // Your callback URL

// Main route with login button
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>PolarHost Login</title>
      </head>
      <body>
        <h1>Login with Discord</h1>
        <a href="https://discord.com/oauth2/authorize?client_id=${client_id}&redirect_uri=${encodeURIComponent(redirect_uri)}&response_type=code&scope=identify email">Login with Discord</a>
      </body>
    </html>
  `);
});

// Handle callback from Discord
app.get('/callback', async (req, res) => {
  const code = req.query.code;
  if (!code) {
    return res.send('Error: No code provided');
  }

  try {
    // Exchange authorization code for access token
    const data = {
      client_id,
      client_secret,
      grant_type: 'authorization_code',
      code,
      redirect_uri
    };

    const tokenResponse = await fetch('https://discord.com/api/oauth2/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: querystring.stringify(data)
    });
    
    const tokenData = await tokenResponse.json();

    if (tokenData.access_token) {
      // Fetch user info with the access token
      const userResponse = await fetch('https://discord.com/api/users/@me', {
        headers: { Authorization: `Bearer ${tokenData.access_token}` }
      });
      const userData = await userResponse.json();

      // Redirect to the dashboard with user info
      res.redirect(`https://dash.polarhost.uk.to?username=${userData.username}`);
    } else {
      res.send('Error exchanging code for token');
    }
  } catch (error) {
    res.send('Error: ' + error.message);
  }
});

app.listen(port, () => {
  console.log(`App running at http://localhost:${port}`);
});
