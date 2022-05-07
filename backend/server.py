import socketserver

import sys
import os
import secrets
from parsers import *
from get import *
from database import *
from postRequests import *


# Read n number of bytes and increment i by n
def read_byte(data, i, n=1):
    byte = bytearray()
    for index in range(n):
        byte += int_to_bytearray(data[i + index], 1)
    i += n
    return byte, i


def escape_html(input):
    return input.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def bytes_to_int(b: bytes):
    return int.from_bytes(b, "big")


# applies the mask to the payload
def apply_mask(mask: bytearray, payload: bytearray) -> bytearray:
    mask_len = len(mask)  # This should be 4
    payload_len = len(payload)
    masked_payload = bytearray()
    # print(f"mask_len = {mask_len} and payload_len = {payload_len}")

    for i in range(payload_len):
        masked_byte: int = mask[i % mask_len] ^ payload[i]
        # print(masked_byte)
        masked_payload += masked_byte.to_bytes(1, 'big')
    return masked_payload


def int_to_bytearray(num: int, num_bytes) -> bytearray:
    num_bytes: bytes = num.to_bytes(length=num_bytes, byteorder='big')
    return bytearray(num_bytes)


# Mask-bit is assumed to be zero
def build_frame(message: str, opcode: int):
    frame: bytearray = bytearray()
    frame += int_to_bytearray(opcode, 1)
    payload_len = len(message)
    if payload_len < 126:
        frame += int_to_bytearray(payload_len, 1)
        frame += message.encode()
    elif payload_len >= 126 and payload_len < 65536:
        frame += int_to_bytearray(126, 1)  # 7 bit length will be 126
        frame += int_to_bytearray(payload_len, 2)  # next two bytes will be the actual payload_len
        frame += message.encode()
    elif payload_len >= 65536:
        frame += int_to_bytearray(127, 1)  # 7 bit length will be 127
        frame += int_to_bytearray(payload_len, 8)  # next two bytes will be the actual payload_len
        frame += message.encode()
    return frame


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    web_sockets = []
    if os.path.isdir('/root'):
        inDocker = True
        
    usernames = []
    valid_tokens = [] # The same for each user

    full_bytes_sent = b''

    full_bytes_sent: bytes = b''

    def handle_websocket(self):
        random_username = "User" + str(random.randint(0, 1000))
        while True:
            data = self.request.recv(1024)
            if data != b'':
                print(
                    f"\r\n------------- WebSocket Data with len = {len(data)} on web_index = {MyTCPHandler.web_sockets.index(self)}----------------")
                # print("\r\n------------- End WebSocket Data 1 ----------------")
                # opcode_mask = b'\x0f'   # 15 = 0000_1111
                opcode_mask = 15  # 15 = 0000_1111
                i = 0
                cur_byte, i = read_byte(data, i)
                opcode = opcode_mask & bytes_to_int(cur_byte)
                # Handle disconnect
                disconnect_opcode = b'\x08'
                print(
                    f"opcode is {opcode} and disconnect opcode is {bytes_to_int(disconnect_opcode)} curbyte = {cur_byte}")

                if opcode == bytes_to_int(disconnect_opcode):
                    MyTCPHandler.web_sockets.remove(self)
                    return

                # Read the mask and payload len
                mask_mask: int = bytes_to_int(b'\x80')  # mask for the mask bit. = 1000_0000
                cur_byte, i = read_byte(data, i)
                mask_bit: int = mask_mask & bytes_to_int(
                    cur_byte)  # is # 1000_0000 if mask bit = 1. 0000_0000 otherwise

                payload_len_mask: int = bytes_to_int(b'\x7f')  # = 0111_1111
                payload_len: int = payload_len_mask & bytes_to_int(
                    cur_byte)  # the payload len. Should be 1 bytes in size (8 bits)

                payload = None
                print(f"first 7 bits of payload length is {payload_len}. mask_bit = {mask_bit}")
                sys.stdout.flush()
                sys.stderr.flush()
                # payload with len < 126
                if payload_len < 126:
                    # mask bit = 1. Read the mask bits
                    if mask_bit == mask_mask:
                        mask_key, i = read_byte(data, i, 4)  # next 4 bytes are the mask-key
                        payload, i = read_byte(data, i,
                                               payload_len)  # read the next payload len bytes to get the payload
                        payload_unmasked: bytearray = apply_mask(mask_key, payload)
                        payload = payload_unmasked
                        # print(f"payload message is {payload_unmasked.decode()} with a mask")
                        # return payload_unmasked
                    else:
                        # the payload begins
                        payload, i = read_byte(data, i, payload_len)
                        # print(f"payload message is {payload.decode()} with no mask")
                        # return payload

                elif payload_len == 126:
                    if mask_bit == mask_mask:
                        # TODO - Correct implementation here
                        # Get the actual payload length
                        payload_len_bytearray, i = read_byte(data, i,
                                                             2)  # the next 16 bits (2 bytes) are the rest of the payload length
                        # get mask-key
                        mask_key, i = read_byte(data, i, 4)  # next 4 bytes are the mask-key

                        # Read the payload with buffering
                        payload_read: int = len(data) - i
                        payload_len: int = int.from_bytes(payload_len_bytearray, 'big')
                        payload: bytearray = data[i: len(data)]
                        while payload_read < payload_len:
                            more_payload = self.request.recv(1024)
                            payload += more_payload
                            payload_read += len(more_payload)

                        # apply mask
                        print(f"applying mask to payload of size {len(payload)}.")
                        payload_unmasked: bytearray = apply_mask(mask_key, payload)
                        payload = payload_unmasked

                    else:
                        # TODO - this might not work
                        # Get the actual payload length
                        payload_len_bytearray, i = read_byte(data, i,
                                                             2)  # the next 16 bits (2 bytes) are the rest of the payload length

                        # Read the payload with buffering
                        payload_read: int = len(data) - i
                        payload_len: int = int.from_bytes(payload_len_bytearray, 'big')
                        payload: bytearray = data[i: len(data)]
                        while payload_read < payload_len:
                            more_payload = self.request.recv(1024)
                            payload += more_payload
                            payload_read += len(more_payload)


                elif payload_len == 127:
                    if mask_bit == mask_mask:
                        # Get the actual payload length
                        payload_len_bytearray, i = read_byte(data, i,
                                                             8)  # the next 64 bits (8 bytes) are the rest of the payload length
                        # get mask-key
                        mask_key, i = read_byte(data, i, 4)  # next 4 bytes are the mask-key

                        # Read the payload with buffering
                        payload_read: int = len(data) - i
                        payload_len: int = int.from_bytes(payload_len_bytearray, 'big')
                        payload: bytearray = data[i: len(data)]
                        while payload_read < payload_len:
                            more_payload = self.request.recv(1024)
                            payload += more_payload
                            payload_read += len(more_payload)

                        payload_unmasked: bytearray = apply_mask(mask_key, payload)
                        payload = payload_unmasked
                    else:
                        # Get the actual payload length
                        payload_len_bytearray, i = read_byte(data, i,
                                                             8)  # the next 64 bits (8 bytes) are the rest of the payload length
                        # Read the payload with buffering
                        payload_read: int = len(data) - i
                        payload_len: int = int.from_bytes(payload_len_bytearray, 'big')
                        payload: bytearray = data[i: len(data)]
                        while payload_read < payload_len:
                            more_payload = self.request.recv(1024)
                            payload += more_payload
                            payload_read += len(more_payload)

                # Pack into a json object
                message = {}
                try:
                    message = json.loads(payload.decode())
                except Exception as e:
                    print(e)
                print(f"\r\nmessage = {message}\r\n")
                if message == {}:
                    continue
                sys.stdout.flush()
                sys.stderr.flush()
                message_type: str = message['messageType']
                if message_type.startswith('webRTC-'):
                    # webrtc
                    try:
                        for websocket in MyTCPHandler.web_sockets:
                            if websocket != self:
                                frame = build_frame(payload.decode(), 129)
                                print(f"Sending frame of size {len(frame)} with message type {message_type}")
                                websocket.request.sendall(frame)
                    except Exception as e:
                        print(e)
                else:
                    # Send chat message
                    response = {'messageType': 'chatMessage', 'username': random_username,
                                'comment': escape_html(message['comment'])}
                    response = json.dumps(response)
                    sys.stdout.flush()
                    sys.stderr.flush()
                    add_user(random_username, response, cursor, db)  # Store on database
                    sys.stdout.flush()
                    sys.stderr.flush()
                    send_opcode = 129
                    response_frame = build_frame(response, send_opcode)
                    for websocket in MyTCPHandler.web_sockets:
                        websocket.request.sendall(response_frame)
                sys.stdout.flush()
                sys.stderr.flush()

    def handle(self):
        while True:
            self.data = self.request.recv(1024)
            string_data: str = self.data.decode()
            path, headers, content = parse_request(self.data)
            # # Data buffering
            # data = self.data
            # boundary = None  # This is used when form data is sent
            # buffered = False
            # content_read = bytes_read(self.data)  # Content read in the first packet
            # content_length = get_content_length(self.data)  # The value of the content length header

            # if len(self.data) <= 0:
            #     return

            # # Buffering loop
            # while content_read < content_length:
            #     buffer_data = self.request.recv(1024)
            #     content_read += len(buffer_data)
            #     buffered = True
            #     data += buffer_data  # Append the buffered bytes

            # # Parsing the buffered data
            # if buffered:
            #     boundary = get_boundary(headers)
            #     content = parse_content(data, boundary)
            # request_type = find_request_type(string_data)   # is either 'get', 'post', 'delete' etc

            sys.stdout.flush()
            sys.stderr.flush()

            self.full_bytes_sent += self.data

            if len(self.data) < 1023:
                break

        print(str(self.full_bytes_sent))
        if 'GET' in str(self.full_bytes_sent):
            handle_get(self, self.full_bytes_sent)
        
        elif 'POST' in str(self.full_bytes_sent):
            handle_post(self, self.full_bytes_sent)

        if path.lower() == '/websocket':
            MyTCPHandler.web_sockets.append(self)
            self.handle_websocket()


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8000

    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
