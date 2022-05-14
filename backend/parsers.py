# JESSE HARTLOFF's Parser
# Not actually used but here if needed


class Request:
    new_line = b'\r\n'
    blank_line_boundary = b'\r\n\r\n'

    def __init__(self, request: bytes):
        # dont do anything with body because we dont know what it is
        [request_line, self.headers_as_bytes, self.body] = self.split_request(request)
        [self.method, self.path, self.http_version] = self.parse_request_line(request_line)
        self.headers = self.parse_headers(self.headers_as_bytes)

    def split_request(request: bytes):
        first_new_line_boundary = request.find(Request.new_line)
        blank_line_boundary = request.find(Request.blank_line_boundary)

        request_line = request[:first_new_line_boundary]
        headers_as_bytes = request[(first_new_line_boundary + len(Request.new_line)):blank_line_boundary]
        body = request[(blank_line_boundary + len(Request.blank_line_boundary)):]
        return [request_line, headers_as_bytes, body]

    def parse_request_line(request_line: bytes):
        return request_line.decode().split(' ')

    def parse_headers(headers_raw: bytes):
        headers = {}
        lines_as_str = headers_raw.decode().split(Request.new_line.decode())
        for line in lines_as_str:
            splits = line.split(':')
            headers[splits[0].strip()] = splits[1].strip()  # remove whitespace of headers after colon
        return


# Returns 'get', 'post' etc
def find_request_type(request: str):
    string_list = request.split('\r\n')
    header_info = string_list[0].split(" ")
    req_type = header_info[0]
    return req_type.lower()


# returns the path, headers and content(if applicable) in a tuple
# return type is a bytearray (for each element)
def parse_request(request: bytes):
    string_list = request.split(b'\r\n')

    # find index of double crlf and the first crlf.

    crlf_index = request.find(b'\r\n\r\n')
    first_crlf = request.find(b'\r\n')

    # Get header info
    header_info = string_list[0].split(b" ")
    # print(f"header info is {header_info}")
    req_type = header_info[0]
    path = header_info[1]
    version = header_info[2]

    # get key values pairs + content (if applicable)
    key_val_string = request[first_crlf + 2:crlf_index]
    key_val_list = key_val_string.split(b'\r\n')

    # get headers
    headers = []
    for pair in key_val_list:
        stripped = pair  # TODO - might need to adjust this
        colon_idx = stripped.find(b':')
        if pair[colon_idx + 1] == b" ":  # remove optional space if present
            stripped = pair.replace(b' ', b'', 1)

        key = stripped[0:colon_idx]
        value = stripped[colon_idx + 1: len(stripped)]
        headers.append([key, value])

    path = path.decode()
    if req_type == b"GET":
        # print((path, headers))
        return path, headers, None

    elif req_type == b'POST':
        content = request[crlf_index + 4: len(request)]
        # print((path, headers, content))
        return path, headers, content
    elif req_type == b'PUT':
        content = request[crlf_index + 4: len(request)]
        # print((path, headers, content))
        return path, headers, content
    elif req_type == b'DELETE':
        # print((path, headers))
        return path, headers, None
    else:
        print("error during parsing.")
        return None


# given a file return the corresponding bytearray
def file_to_array(file):
    array = bytearray()
    byte = file.read(1)
    while byte:
        array += byte
        byte = file.read(1)
    return array


# Retrives the content length if available. Else returns 0
def get_content_length(data: bytes):
    headers = parse_request(data)[1]
    content_length = None
    for header in headers:
        string_header = header[0].decode()
        if string_header.lower() == "content-length":
            content_length = int(header[1].decode())
    if content_length == None:
        content_length = 0
    return content_length


# returns the number of bytes
# This is called for the first packet of data
def bytes_read(data):
    first_double_crlf = data.find(b'\r\n\r\n')
    return len(data) - first_double_crlf - len(b'\r\n\r\n')


# Input: 2d array of headers. Use the outputs from parse_request
# Returns the boundary used in the multi-form request
def get_boundary(headers):
    boundary = b''
    for header in headers:
        string_header = header[0].decode()
        if string_header.lower() == "content-type":
            dashes_index = header[1].find(b'----')
            boundary = header[1][dashes_index + 4: len(header[1])]
            break
    return boundary


# Parses multi-part forms
# Input: Data -> the full request (after getting all the packets)
# Output: 
def parse_content(data, boundary):
    content_start = data.find(b'\r\n\r\n')

    content = data[content_start + len(b'\r\n\r\n'): len(data)]
    form_boundary = b'------' + boundary
    # end_part = b'------WebKitFormBoundaryoumBdBCU5Mn86dQ7--\r\n'
    content_split = content.split(form_boundary)
    # Returns an entry for each piece of content found
    all_content = []
    for form in content_split:
        # print(form)
        if form != b'--\r\n' and form != b'':
            first_crlf_idx = form.find(b'\r\n\r\n')
            header = form[0: first_crlf_idx]
            form_content = form[first_crlf_idx + 4: len(form)]
            # clean up form data
            header = header[2:len(header)]  # remove the \r\n in the beginning of the header
            form_content = form_content[0: len(form_content) - 2]  # remove the \r\n at the end of the content
            all_content.append([header, form_content])
    return all_content


# This function is used when uploading comments or images
# Input: Use the output from parse_content above
# Returns all parsed content [  [content, (header, header_content), (header2, header2_content)], ..., ]
def parse_data(data):
    print('-------- Parse Data ----------')

    all_content = []
    for form in data:
        print(form)
        header_list = form[0].split(b'\r\n')
        print(header_list)
        content = form[1]
        content_list = [content]
        for header in header_list:
            # print(header)
            header_split = header.split(b':')
            if len(header_split) == 1:
                # print(f"header with len(0) is {header_split}")
                continue
            header_name = header_split[0]
            header_content = header_split[1].strip()

            header_info = (header_name, header_content)
            content_list.append(header_info)
        all_content.append(content_list)

    return all_content

    # Parses form data by splitting at ';'
    # Used to determine if an image or a comment was uploaded or both
    # Input: Uses the inputs from parse_data above
    # Output: A dictionary where the key is the form's name and the value is the form data
    # Example output: dict["name"] = '"comment"'


def parse_form_data(form):
    all_form_data = {}
    form_data_list = form.split(b';')
    for form_data in form_data_list:
        form_data = form_data.strip()
        if form_data == b'form-data':
            continue
        form_name, form_name_content = form_data.split(b'=')
        all_form_data.update({form_name.decode().strip(): form_name_content.decode().strip()})
    return all_form_data
