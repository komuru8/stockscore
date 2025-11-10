#!/usr/bin/env python3
"""
Simple HTTP server to serve static files (icons, manifest.json)
for the StockScore Streamlit application
"""
import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = "static"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow Streamlit app to access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Static file server running at http://0.0.0.0:{PORT}")
        print(f"📁 Serving directory: {os.path.abspath(DIRECTORY)}")
        httpd.serve_forever()
