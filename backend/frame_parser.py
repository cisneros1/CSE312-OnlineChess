# WAYS TO CONVERT
# decimal to bytes::  to_bytes
# decimal to binray:: bin(int)
# binary to int:: int(bin, 2)

def parse_frame(frame):
    info_type = ""

    if frame[0] == 129:
        info_type = 'text'
    else:
        info_type = 'close'

    payload_length = (bin(frame[1])[3:])

    mask = []
    start = 0
    full_length_bytes = bytearray()

    if payload_length != '1111110' and payload_length != '1111111':  # < 126    
        full_length_bytes.append(frame[1] & 128)    
        for byte_location in range(2, 6):
            mask.append(frame[byte_location])
        start = 6

    elif payload_length == '1111110':  # 126
        
        for byte_location in range(2, 4):
            full_length_bytes.append(frame[byte_location])

        for byte_location in range(4, 8):
            mask.append(frame[byte_location])
        start = 8

    elif payload_length == '1111111':
        for byte_location in range(2, 10): # [1](1  1111111) (3)(4) (5)(6) (7)(8) (9)(10)
            full_length_bytes.append(frame[byte_location])

        for byte_location in range(10, 14):
            mask.append(frame[byte_location])
        start = 14
    else:
        print('Something wrong')

    full_length_int = int.from_bytes(full_length_bytes, 'big')
    print('The full length of the frame being parsed is: ' + str(full_length_int))

    payload_end = start + full_length_int
    masked_payload = frame[start:payload_end]

    # unmask payload // if length is not a multiple of 4 use only
    i = 0
    unmasked_payload = b''
    for byte in masked_payload:
        masking_byte = mask[i % 4]
        xor = (byte ^ masking_byte).to_bytes(1, 'big')
        unmasked_payload += xor
        i = ((i+1) % 4)

    # print('ENTIRE UNMASKED PAYLOAD' + str(unmasked_payload))


    # RETURN PAYLOAD AND TYPE
    if info_type == 'close':
        payload = ""
        print('Close Request Sent')
        return ("", info_type)
    
    elif 'webRTC' in str(unmasked_payload):
        print('Payload before Return: ' + str(unmasked_payload))
        return (unmasked_payload, info_type)
    
    else:
        print('Payload before Return: ' + str(unmasked_payload))
        return (unmasked_payload.decode('utf8'), info_type)
    

# Create a Websocket frame
def build_output_frame(ws_data):
    print('building frame...')
    frame = bytearray(b'\x81')
    payload_len = len(ws_data)

    if payload_len < 126:
        frame.append(payload_len)
        print(str(frame))

    elif payload_len < 65536:
        frame.append(126)
        l = payload_len.to_bytes(2, 'big')
        print(str(l))
        frame += bytes(l)
        print(str(frame))
        
        
    else:
        frame.append(127)
        l = payload_len.to_bytes(8, 'big')
        print(str(l))
        frame += bytes(l)
        print(str(frame))
    
    # append extra length

    for byte in ws_data:
        frame.append(byte)

    return frame


def find_payload_length(partial_frame): 
    print(str(partial_frame))
    print('We need to get length out of: ' + str(partial_frame[1]) + '==m|L |' + str(bin(partial_frame[1])))
    payload_length = (bin(partial_frame[1])[3:])
    
    print('We got a payload length of ' + str(payload_length) + ' in the partial frame') 
    full_length = bytearray()
    full_length_int=0
    
    if payload_length != '1111110' and payload_length != '1111111':  # < 126
        as_int = int(str(payload_length), 2)
        print('Returning length: ' + str(as_int))
        return as_int
    
    elif payload_length == '1111110':  # 126
        for byte_location in range(2, 4):
            full_length.append(partial_frame[byte_location])

    elif payload_length == '1111111':
        for byte_location in (2,3,4,5,6,7,8,9):
            full_length.append(partial_frame[byte_location])
    else:
        print('No length found in partial frame')
    print('Hex Array: ' + str(full_length))
    full_length_int = int.from_bytes(full_length, 'big')
    print("Partial Frame's Length: " + str(full_length_int))
        
    return full_length_int