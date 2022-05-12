
def file_paths(self):
    dict = {}
    if self.inDocker == False:
        dict = {
            "index.html": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/index.html',
            "signin.html": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/signin.html',
            "signup.html": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/signup.html',

            "styles.css": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/style.css',
            "functions.js": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/functions.js',
            "/Chess/ChessEngine.js": '../Chess/ChessEngine.js',
            "imagefolder": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/image',
        }
    else:
        dict = {
            "index.html": '/root/frontend/index.html',
            "signin.html": '/root/frontend/signin.html',
            "signup.html": '/root/frontend/signup.html',
            "game.html": '/root/frontend/game.html',
            
            "style.css": '/root/frontend/style.css',
            "signin.css": '/root/frontend/signin.css',
            "signup.css": 'root/frontend/signup.css',

            "functions.js": '/root/frontend/functions.js',
            "game.js": '/root/frontend/game.js',
            "/Chess/ChessEngine.js": '/root/Chess/ChessEngine.js',

            "imagefolder": '/root/frontend/image/',
            "favicon": '/root/frontend/favicon.ico'
        }

    return dict
