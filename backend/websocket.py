import sys, json, frame_parser, ast # -> ast is just to turn str into json does no server stuff
from typing import Any # -> Just in case I want to declare a var as Any
import database as db
from generate_response import send_301
from post import *

ws_users = [] # stores usernames only
ws_conn = [] # stores connections (tcp objects)
# --- Each user index must match connection index ---


def websocket_server(tcp_handler, username):    
    # check if user exists and append to lists if not
    user_exists = False
    for user in ws_users:
        if user == username:
            user_exists = True
    if user_exists == False:
        ws_users.append(username)
        ws_conn.append(tcp_handler)
    
    # Begin infinite websocket connection until closed
    while True:
        ws_data = tcp_handler.request.recv(1024)
        sys.stdout.flush()
        sys.stderr.flush()
        full_data = ws_data
        size_to_read = frame_parser.find_payload_length(ws_data)
        print(str(full_data))
        
        while len(full_data) < size_to_read:
            try:
                print(str(len(full_data)) + '<' + str(size_to_read))
                new_data = tcp_handler.request.recv(1024)
                full_data += new_data
            except Exception as e:
                print(e)
                          
        if len(full_data) != 0: 
            print('Received Data')            
            # FRAME PARSING
            frame_data = frame_parser.parse_frame(full_data)
            
            # print(frame_data[0]) # --> actual data
            # print(frame_data[1]) # --> type of data (either text or close)
            
            # WEBRTC
            if frame_data[1] == 'text' and frame_data[0] != "":
                # webRTC is in text format
                # Route all webRTC frames and do nothing more
                if 'offer' in str(frame_data[0]):
                    print('Received a webRTC offer')
                    for conn in ws_conn:
                        if conn != tcp_handler:
                            # build and send
                            frame_to_send = frame_parser.build_output_frame(frame_data[0])
                            conn.request.sendall(frame_to_send)
                elif 'answer' in str(frame_data[0]):
                    print('Received a webRTC answer')
                    for conn in ws_conn:
                        if conn != tcp_handler:
                            frame_to_send = frame_parser.build_output_frame(
                                frame_data[0])
                            conn.request.sendall(frame_to_send)
                elif 'candidate' in str(frame_data[0]):
                    print('Received a candidate request')
                    for conn in ws_conn:
                        if conn != tcp_handler:
                            frame_to_send = frame_parser.build_output_frame(
                                frame_data[0])
                            conn.request.sendall(frame_to_send)
                else:
                    # NORMAL TEXT FRAME
                    # literal_eval function turns a string of a json string into an actual dumped json string 
                    json_as_dict = ast.literal_eval(frame_data[0]) 
                    
                    chattype = json_as_dict['messageType']
                    comment = json_as_dict['comment']
                    comment = escape_html(comment)
                    
                    # outputdict = {'messageType': 'chatMessage','username': username,'comment': comment}
                    # print(str(outputdict))

                    # # DATABASE INSERT
                    # id = db.get_next_id()
                    # entry = {'_id': id,'messageType': 'chatMessage','username': username,'comment': comment}
                    
                    # db.insert(entry)
                    # print('Comment inserted to Database')
                    
                    # CREATE AND SEND FRAME
                    jsonmsg = json.dumps(outputdict)
                    msg_encoded = jsonmsg.encode()
                    output_frame = frame_parser.build_output_frame(msg_encoded)
                    
                    # SEND TO ALL CONNECTIONS
                    for conn in ws_conn:
                        try: 
                            conn.request.sendall(output_frame)
                            print(str(username) + ' has received the frame')
                        except Exception as e: 
                            print(str(e))
                            print('Passing')
                            pass
                        
            elif frame_data[1] == 'close':
                # HANDLE CLOSE FRAME -> index of connection must match user
                i=0
                for conn in ws_conn:
                    if conn == tcp_handler:
                        ws_conn.remove(conn)
                        ws_users.remove(ws_users[i])
                    i = i+1
            else:
                print('Neither a text nor close frame was sent')
        # else:
        #     print('No data')             