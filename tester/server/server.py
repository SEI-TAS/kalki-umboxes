from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO



class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == "/":
			self.path = "/index.html"
		if self.path == "/alert/":
			self.path = "/alert.html"
		try:
			file_to_open = open(self.path[1:]).read()
			self.send_response(200)
		except:
			file_to_open = "File not found"
			self.send_response(404)
		self.end_headers()
		self.wfile.write(bytes(file_to_open, "utf-8"))
	def do_POST(self):
		path = self.path
		content_length = int(self.headers['Content-Length']) 
		body = self.rfile.read(content_length)
		self.send_response(200)
		self.end_headers()
		response = BytesIO()
		response.write(b'Received: ')
		response.write(body)
		self.wfile.write(response.getvalue())
		

httpd = HTTPServer(("0.0.0.0", 6060), Serv)
httpd.serve_forever()