# WAYS TO CONVERT
# decimal to bytes::  to_bytes
# decimal to binray:: bin(int)
# binary to int:: int(bin, 2)
import sys


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


def parse_frame(tcp_instance, data) -> bytearray:
    print(
        f"\r\n------------- WebSocket Data with len = {len(data)} on web_index = {tcp_instance} ----------------")
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
        return bytearray(b'disconnect')  # return empty byte

        # Read the mask and payload len
    mask_mask: int = bytes_to_int(b'\x80')  # mask for the mask bit. = 1000_0000
    cur_byte, i = read_byte(data, i)
    mask_bit: int = mask_mask & bytes_to_int(
        cur_byte)  # is # 1000_0000 if mask bit = 1. 0000_0000 otherwise

    payload_len_mask: int = bytes_to_int(b'\x7f')  # = 0111_1111
    payload_len: int = payload_len_mask & bytes_to_int(
        cur_byte)  # the payload len. Should be 1 bytes in size (8 bits)

    payload = bytearray()
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
                more_payload = tcp_instance.request.recv(1024)
                payload += more_payload
                payload_read += len(more_payload)

            # apply mask
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
                more_payload = tcp_instance.request.recv(1024)
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
                more_payload = tcp_instance.request.recv(1024)
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
                more_payload = tcp_instance.request.recv(1024)
                payload += more_payload
                payload_read += len(more_payload)
    return payload
