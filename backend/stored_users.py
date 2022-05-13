authenticated_users = {}  # username -> authentication token
web_socket_connections = {}  # username -> websocket_connection (tcp instance)
# connected users
connected_users = {}  # username -> ['sender' or 'receiver', other_user]
connected_sockets = {}  # username -> websocket connection
