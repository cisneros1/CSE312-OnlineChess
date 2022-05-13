authenticated_users = {}  # username -> authentication token
web_socket_connections = {}  # username -> websocket_connection (tcp instance)
# connected users - The sender is the person who sent the challenge. The receiver was the recipient
connected_users = {}  # username -> ['sender' or 'receiver', other_user]
connected_sockets = {}  # username -> websocket connection
