from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import threading
import json
import datetime
import socket
import os


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        """Handle HTTP GET requests."""
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self) -> None:
        """Handle HTTP POST requests."""
        data = self.rfile.read(int(self.headers["Content-Length"]))

        current_time = datetime.datetime.now()
        data_with_time = f"{current_time}"
        print(data_with_time)

        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)

        data_dict = {
            data_with_time: {
                key: value
                for key, value in [el.split("=") for el in data_parse.split("&")]
            }
        }
        print(data_dict)

        file_name = "storage/data.json"

        os.makedirs("storage", exist_ok=True)

        with open(file_name, "a") as f:
            json.dump(data_dict, f, indent=2)
            f.write("\n")

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename: str, status: int = 200) -> None:
        """Send an HTML file as the HTTP response."""
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self) -> None:
        """Send static files as the HTTP response."""
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http_server(ip: str, port: int) -> None:
    """Run an HTTP server."""
    server_address = (ip, port)
    httpd = HTTPServer(server_address, HttpHandler)
    httpd.serve_forever()


def run_socket_server(ip: str, port: int) -> None:
    """Run a UDP socket server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f"Received data: {data.decode()} from: {address}")
            sock.sendto(data, address)
            print(f"Send data: {data.decode()} to: {address}")

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        sock.close()


if __name__ == "__main__":
    HTTP_IP = "127.0.0.1"
    HTTP_PORT = 3000
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000

    http_thread = threading.Thread(target=run_http_server, args=(HTTP_IP, HTTP_PORT))
    socket_thread = threading.Thread(target=run_socket_server, args=(UDP_IP, UDP_PORT))
    http_thread.start()
    socket_thread.start()
    http_thread.join()
    socket_thread.join()

    print(f"Server started on HTTP: {HTTP_IP}:{HTTP_PORT}, UDP: {UDP_IP}:{UDP_PORT}")
