#!/usr/bin/env python3
"""PiNet AI v0.1: offline local knowledge search portal, stdlib only."""
import html
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
KNOWLEDGE = ROOT / 'knowledge'
DB = ROOT / 'knowledge.db'
HOST = os.environ.get('PINET_HOST', '0.0.0.0')
PORT = int(os.environ.get('PINET_PORT', '8080'))

CSS = '''body{font-family:system-ui,-apple-system,sans-serif;background:#0e1725;color:#e9f1fb;margin:0}main{max-width:780px;margin:8vh auto;padding:0 20px}h1{font-size:2.5rem;margin-bottom:0}p{line-height:1.65;color:#b5c7dd}.pill{display:inline-block;border:1px solid #46648a;border-radius:100px;padding:5px 12px;color:#9bdfbe;font-size:0.8rem}form{display:flex;gap:8px;margin:28px 0}input{background:#1b2b41;color:white;border:1px solid #50657d;border-radius:10px;padding:15px;flex:1;min-width:0;font-size:1rem}button{background:#50a6ff;border:0;border-radius:10px;padding:0 20px;font-weight:bold;cursor:pointer}.card{background:#17283d;border:1px solid #314963;border-radius:14px;margin:14px 0;padding:18px}h3{margin:0 0 8px}small{color:#8cacce}a{color:#78b8ff}footer{margin-top:40px;color:#8cacce;font-size:.85rem}'''

def connect():
    return sqlite3.connect(DB, timeout=10)

def initialize():
    KNOWLEDGE.mkdir(exist_ok=True)
    with connect() as cx:
        cx.execute('CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(title, content)')
        cx.execute('DELETE FROM documents')
        for file in sorted(KNOWLEDGE.iterdir()):
            if file.is_file() and file.suffix.lower() in ('.txt', '.md') and file.stat().st_size < 2_000_000:
                cx.execute('INSERT INTO documents(title, content) VALUES (?, ?)', (file.name, file.read_text(encoding='utf-8', errors='replace')))

def search(query):
    # Treat input as plain words rather than accepting advanced FTS query syntax.
    words = re.findall(r'\w+', query, flags=re.UNICODE)[:12]
    if not words:
        return []
    terms = ' OR '.join('"' + word.replace('"','') + '"' for word in words)
    with connect() as cx:
        return cx.execute('SELECT title, snippet(documents, 1, "", "", " ... ", 22) FROM documents WHERE documents MATCH ? ORDER BY bm25(documents) LIMIT 8', (terms,)).fetchall()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path)
        if path.path == '/health':
            body = b'OK'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path.path != '/':
            self.send_error(404)
            return
        q = parse_qs(path.query).get('q', [''])[0][:300].strip()
        results = search(q) if q else []
        sections = ''
        if q:
            if results:
                sections = '<p>Found relevant passages in your offline library:</p>'
                for title, excerpt in results:
                    sections += '<article class="card"><h3>' + html.escape(title) + '</h3><p>' + html.escape(excerpt) + '</p></article>'
            else:
                sections = '<div class="card"><p>No matching passages found. Add .txt or .md files to the knowledge folder, then restart the service.</p></div>'
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PiNet AI</title><style>{CSS}</style></head><body><main><span class="pill">● OFFLINE • LOCAL NETWORK</span><h1>PiNet AI</h1><p>Your portable, internet-free knowledge station. Search notes and reference material stored on this Raspberry Pi.</p><form action="/" method="get"><input name="q" maxlength="300" value="{html.escape(q, quote=True)}" placeholder="Ask about DNS, Linux, networking…" aria-label="Search knowledge" required><button type="submit">Search</button></form>{sections}<footer>Version 0.1 • Local document retrieval (not yet a generative LLM) • No internet required</footer></main></body></html>'''
        body = page.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    initialize()
    print(f'PiNet portal listening at http://{HOST}:{PORT}', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
