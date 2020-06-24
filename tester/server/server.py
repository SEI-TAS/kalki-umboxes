from http.server import HTTPServer, BaseHTTPRequestHandler

class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		print("HELLO")
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
		try:
			self.send_response(200)
		except:
			self.send_response(301)

httpd = HTTPServer(("0.0.0.0", 6060), Serv)
httpd.serve_forever()