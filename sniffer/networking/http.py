CRLF = "\r\n"

# Global Authorization pattern
basic_authorization_pattern = None

class HTTP():

    def __init__(self, raw_data):
        try:
            self.data = raw_data.decode('utf-8')
        except:
            self.data = raw_data

        self.method = None
        self.uri = None
        self.version = None
        self.host = None
        self.authorization = None

        self.parseRequest()


    def parseRequest(self):
        data = self.data
        
        if len(data) == 0:
            raise Exception("Error parsing http data: no data")

        #parse the HTTP request line
        request_line = data.split(CRLF, 1)[0]
        split_request_line = request_line.split(" ")
        self.method = split_request_line[0]
        self.uri = split_request_line[1]
        self.version = split_request_line[2]
        
        if "HTTP" not in self.version:
            raise Exception("Error parsing http: not an http packet")

        #parse HTTP header
        self.host = self.getHeaderData("Host")

        #gather authorization
        self.authorization = self.getHeaderData("Authorization")


    def getHeaderData(self, target):
        data = self.data
        target_with_colon = target + ": "
        try:
            start_idx = data.index(target_with_colon) + len(target_with_colon)
            end_idx = data.index(CRLF, start_idx)
            return data[start_idx:end_idx]
        except:
            return None

