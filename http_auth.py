import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
import base64
from hashlib import sha512

def encrypt_b64(credentials_b64):
    return sha512(credentials_b64).hexdigest()


def encrypt(credentials):
    return sha512(base64.b64encode(credentials)).hexdigest()


hashed_credentials = encrypt('ilya:password')

class Handler(BaseHTTPRequestHandler):
    ''' Main class to present webpages and authentication. '''
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<body><h1>Thats it</h1></body>')

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        ''' Present frontpage with user authentication. '''
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        else:
            credentials = self.headers.getheader('Authorization')\
                    .split('Basic ')[1]
            if encrypt_b64(credentials) == hashed_credentials:
                self.do_HEAD()
                self.wfile.write('authenticated!')
            else:
                self.do_AUTHHEAD()
                self.wfile.write('not authenticated')

httpd = SocketServer.TCPServer(("", 10001), Handler)

httpd.serve_forever()

if __name__ == '__main__':
    main()
