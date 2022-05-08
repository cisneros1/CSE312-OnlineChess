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


user once logged in
'/logged_in'
    ---> This can only be accessed through sign in form submission
    ---> A normal GET request to this page results in an error

    