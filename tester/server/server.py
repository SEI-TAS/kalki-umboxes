from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

alert_handler = []

#RETURN AS A JSON ARRAY
def process_queue():
	output = "Alerts Recieved\n"
	while(len(alert_handler) > 0):
		output += alert_handler.pop(0).decode() + "\n"
	return output[0:len(output)-1]

class Serv(BaseHTTPRequestHandler):
	
	def do_GET(self):
		if self.path == "/":
			self.path = "/index.html"
		if self.path == "/alert/":
			self.path = "/alert.html"
		try:
			self.send_response(200)
		except:
			self.send_response(404)
		self.end_headers()
		self.wfile.write(process_queue().encode())

	def do_POST(self):
		path = self.path
		content_length = int(self.headers['Content-Length']) 
		body = self.rfile.read(content_length)
		alert_handler.append(body)
		self.send_response(200)
		self.end_headers()
		response = BytesIO()
		response.write(b'Received: ')
		response.write(body)
		self.wfile.write(response.getvalue())

httpd = HTTPServer(("0.0.0.0", 6060), Serv)
httpd.serve_forever()