#!/usr/bin/env python3
"""Generate base64 encoded icons for embedding in HTML"""
import base64
import os

icon_files = {
    'favicon-32': 'static/icons/favicon-32.png',
    'favicon-16': 'static/icons/favicon-16.png',
    'apple-touch-icon': 'static/icons/apple-touch-icon.png',
}

print("Base64 encoded icons:\n")

for name, path in icon_files.items():
    if os.path.exists(path):
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            print(f"{name}:")
            print(f"data:image/png;base64,{encoded[:100]}...")
            print(f"Length: {len(encoded)} characters\n")
    else:
        print(f"{name}: File not found at {path}\n")
