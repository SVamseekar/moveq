"""Clean URL development server for moveq website.
Serves clean slugs like /docs/core, /guides, /reference without .html or index.html.
"""

import os
import sys
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
DOC_ROOT = os.path.dirname(os.path.abspath(__file__))

class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOC_ROOT, **kwargs)

    def do_GET(self):
        url_path = self.path.split('?')[0].split('#')[0]
        
        # Remove leading slash
        rel_path = url_path.lstrip('/')
        local_path = os.path.join(DOC_ROOT, rel_path)

        # 1. Exact file match (e.g. /assets/css/theme.css)
        if os.path.isfile(local_path):
            return super().do_GET()

        # 2. Clean directory slug with index.html (e.g. /docs/core -> website/docs/core/index.html)
        dir_index = os.path.join(local_path, "index.html")
        if os.path.isfile(dir_index):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            with open(dir_index, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # 3. Clean slug with .html (e.g. /docs/core -> website/docs/core.html)
        html_file = local_path + ".html"
        if os.path.isfile(html_file):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            with open(html_file, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # 4. Root / -> website/index.html
        if url_path == "" or url_path == "/":
            root_index = os.path.join(DOC_ROOT, "index.html")
            if os.path.isfile(root_index):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                with open(root_index, "rb") as f:
                    content = f.read()
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        return super().do_GET()

if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(("0.0.0.0", PORT), CleanURLHandler)
    print(f"Serving clean URLs on http://localhost:{PORT}")
    server.serve_forever()
