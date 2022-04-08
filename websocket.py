
def ws_server(MyTCPHandler):
    print('Inside the ws_server')
    while True:
        # Perform websocket Parsing
        data = MyTCPHandler.request.recv(1024)
        print('WS DATA SENT: ' + str(data))