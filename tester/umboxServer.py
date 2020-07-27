from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import json

class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		global alert_handler
		if self.path == "/":
			self.path = "/index.html"
		if self.path == "/alert/":
			self.path = "/alert.html"
		try:
			self.send_response(200)
		except:
			self.send_response(404)
		self.end_headers()
		self.wfile.write(json.dumps(alert_handler).encode())

	def log_message(self, format, *args):
		return 

	def do_POST(self):
		path = self.path
		content_length = int(self.headers['Content-Length']) 
		body = self.rfile.read(content_length)
		alert_handler.append(body.decode())
		self.send_response(200)
		self.end_headers()
		response = BytesIO()
		response.write(b'Received: ')
		response.write(body)
		self.wfile.write(response.getvalue())

httpd = HTTPServer(("10.27.151.106", 80), Serv)
httpd.serve_forever()