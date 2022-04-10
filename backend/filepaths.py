
def file_paths(self):
    dict = {}
    if self.inDocker == False:
        dict = {
            "index.html": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/index.html',
            "styles.css": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/style.css',
            "functions.js": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/functions.js',
            "imagefolder": '/Users/brianc/Desktop/cse312/CSE312-OnlineChess/frontend/images',
        }
    else:
        dict = {
            "index.html": '/root/frontend/index.html',
            "style.css": '/root/frontend/style.css',
            "functions.js": '/root/frontend/functions.js',
            "imagefolder": '/root/frontend/images/',
            "favicon": '/root/frontend/favicon.ico'
        }

    return dict
