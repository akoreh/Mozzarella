

class URL:
    def __init__(self, url):
        self.url = url
        self.scheme, self.isHttpRequest, self.isHttps, self.isFile = self._extract_scheme(
            self.url)

        self.path = self._extract_path(self.url)

        if self.isHttpRequest:
            self.host = self._extract_host(self.url)
            self.port = self._extract_port(self.scheme, self.host)

    def request(self):
        if self.isHttpRequest:
            return self._make_http_request()
        elif self.isFile:
            return self._make_file_request()

    def _extract_scheme(self, url: str):
        scheme, _ = url.split("://", 1)

        assert scheme in ["http", "https",
                          "file"], f"Unsupported scheme: {scheme}"

        isHttpRequest = scheme in ['http', 'https']
        isHttps = scheme == 'https'
        isFile = scheme == 'file'

        return [scheme, isHttpRequest, isHttps, isFile]

    def _extract_host(self, url: str):
        url = url.split("://", 1)[1]
        host = url.split('/', 1)[0]
        return host

    def _extract_port(self, scheme: str, host: str):
        if ":" in host:
            host, port = host.split(":", 1)

            return int(port)
        elif 'https' in scheme:
            return 443

        return 80

    def _extract_path(self, url: str) -> str:
        if "://" in url:
            _, rest = url.split("://", 1)
        else:
            rest = url

        parts = rest.split("/", 1)

        if len(parts) == 2:
            return "/" + parts[1]
        else:
            return "/"

    def _make_file_request(self):
        import os

        abs_path = os.path.abspath(self.path)

        try:
            with open(abs_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return "<h1>File not found</h1>"

    def _make_http_request(self):
        import socket
        import ssl

        tcp_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        tcp_socket.connect((self.host, self.port))

        if self.isHttps:
            ssl_ctx = ssl.create_default_context()
            tcp_socket = ssl_ctx.wrap_socket(
                tcp_socket, server_hostname=self.host)

        request_string = self._compose_http_req_string()

        tcp_socket.send(request_string)

        response = tcp_socket.makefile("r", encoding="utf8", newline="\r\n")

        statusLine = response.readline()
        version, status, explanation = statusLine.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()

            if line == "\r\n":
                break

            header, value = line.split(":", 1)

            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()

        tcp_socket.close()

        return content

    def _compose_http_req_string(self) -> str:
        from config.constants import USER_AGENT, HTTP_VERSION

        reqStr = f"GET {self.path} {HTTP_VERSION}\r\n"
        reqStr += f"Host: {self.host}\r\n"
        reqStr += "Connection: close\r\n"
        reqStr += f"User-Agent: {USER_AGENT}\r\n"
        reqStr += "\r\n"

        return reqStr.encode("utf8")
