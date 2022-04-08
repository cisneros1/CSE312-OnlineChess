class Request:
    new_line = b'\r\n'
    blank_line_boundary = b'\r\n\r\n'

    def __init__(self, request: bytes):
        # dont do anything with body because we dont know what it is
        [request_line, self.headers_as_bytes,
            self.body] = split_request(request)
        [self.method, self.path, self.http_version] = parse_request_line(
            request_line)
        self.headers = parse_headers(self.headers_as_bytes)


def split_request(request: bytes):
    first_new_line_boundary = request.find(Request.new_line)
    blank_line_boundary = request.find(Request.blank_line_boundary)

    request_line = request[:first_new_line_boundary]
    headers_as_bytes = request[(
        first_new_line_boundary + len(Request.new_line)):blank_line_boundary]
    body = request[(blank_line_boundary + len(Request.blank_line_boundary)):]
    return [request_line, headers_as_bytes, body]


def parse_request_line(request_line: bytes):
    return request_line.decode().split(' ')


def parse_headers(headers_raw: bytes):
    headers = {}
    lines_as_str = headers_raw.decode().split(Request.new_line.decode())
    for line in lines_as_str:
        splits = line.split(':')
        # remove whitespace of headers after colon
        headers[splits[0].strip()] = splits[1].strip()
    return headers