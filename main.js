const express = require('express');
const axios = require('axios');
const app = express();
const keep_alive = require('./keep_alive.js')

app.get('/callback', async (req, res) => {
    const code = req.query.code;

    try {
        // Exchange the code for an access token
        const response = await axios.post('https://discord.com/api/oauth2/token', null, {
            params: {
                client_id: '1297105461182726197',
                client_secret: 'sAvL6CmS4YqXq9ZMacQcirEjMYr8aQqG',
                grant_type: '8ecylsZD35EZ26BE7tJYnaOq4FsiO7',
                code: code,
                redirect_uri: 'https://polarhost.github.io/callback',
            },
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        const accessToken = response.data.access_token;

        // Fetch the user info using the access token
        const userInfo = await axios.get('https://discord.com/api/users/@me', {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        const user = userInfo.data;

        // Set a session or cookie here to keep the user logged in, then redirect
        // You can also save user details to your database if necessary

        // Redirect the user to the next page after successful login
        res.redirect('/dashboard'); // Example: redirecting to a dashboard page
    } catch (error) {
        console.error('Error fetching access token:', error);
        res.status(500).send('Something went wrong!');
    }
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
