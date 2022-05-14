# CSE312-OnlineChess

Website functionality

Homepage
-> GET '/'
response: 
    index.html  # the logged out site

login page
-> GET '/sigin'
response: 
    create a token
    send signin.html with token

    onLogin:
        check token
        if valid
            sends 'POST /signup_log' with username, password, and authentication token
                POST Response :: in response to request we send the logged_in.html which welcoms user


sign up page
-> GET '/siginup'
response: 
    create a token
    send signup.html with token

    onSignUp:
        check token
            if valid
                sends 'POST /login' with username token -> NO AUTHENTICATION TOKEN HERE
                POST Response :: Re routes user back to /signin
* Users can save the background color which is picked on the signup page.
* Refresh the page after logging in into different accounts to see  them on the homepage.html
  * Users have the options to send a DM or 'challenge' them to a game of chess
* 'Challenge a user to redirect both users to another page'
  * On this websocket users can send message to each other. Only these two users will be able to see each other messages.
  * Users should also be able to play live chess. Simply click and let go of the piece. The user who got the notification get to make the first move. (currently does not work properly)
* At this 'Challenge' page there is an option to start a webrtc chat

    