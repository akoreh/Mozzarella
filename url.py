import socket
import ssl

from config.constants import USER_AGENT, HTTP_VERSION


class URL:
    def __init__(self, url):
        self.url = url
        self.scheme, self.isHttps = self._extract_scheme(self.url)
        self.host = self._extract_host(self.url)
        self.port = self._extract_port(self.scheme, self.host)
        self.path = self._extract_path(self.url)

    def _extract_scheme(self, url: str):
        scheme, _ = url.split("://", 1)

        assert scheme in ['http', 'https'], f"Unsupported scheme: {scheme}"

        isHttps = scheme == 'https'

        return [scheme, isHttps]

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

    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        s.connect((self.host, self.port))

        if self.isHttps:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} {}\r\n".format(self.path, HTTP_VERSION)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: close\r\n"
        request += "User-Agent: {}\r\n".format(USER_AGENT)
        request += "\r\n"

        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")

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

        s.close()

        return content
