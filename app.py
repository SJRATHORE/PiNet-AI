#!/usr/bin/env python3
"""PiNet AI v0.2: a lightweight, source-grounded offline question-answer portal.

Uses Python standard library and SQLite FTS5; does NOT run a language model.
"""
import html
from contextlib import closing
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
MAX_QUESTION = 300
STOP_WORDS = set('a an and are as at be can could do does for from how i in is it me my of on or our should tell the their there these this to us was what when where which who why will with would you your about explain difference between'.split())
CSS = '''*{box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;background:#0e1725;color:#e9f1fb;margin:0}main{max-width:790px;margin:5vh auto;padding:0 18px 40px}h1{font-size:2.3rem;margin:.5rem 0}p{line-height:1.6;color:#b5c7dd}.pill{display:inline-block;border:1px solid #46648a;border-radius:100px;padding:5px 12px;color:#9bdfbe;font-size:.78rem}.chat{margin:26px 0}.bubble{border-radius:15px;padding:14px 18px;margin:12px 0;line-height:1.6;white-space:pre-wrap}.user{background:#23517b;margin-left:15%;color:#fff}.assistant{background:#17283d;border:1px solid #314963;margin-right:10%}.source{margin:10px 0 0;font-size:.85rem;color:#9dc5ee}.label{font-size:.75rem;color:#a3bedc;margin-bottom:6px;font-weight:700}form{display:flex;gap:8px;margin:24px 0}input{background:#1b2b41;color:white;border:1px solid #50657d;border-radius:10px;padding:15px;flex:1;min-width:0;font-size:1rem}button{background:#50a6ff;border:0;border-radius:10px;padding:0 18px;font-weight:bold;cursor:pointer}a{color:#9dc5ee}footer{margin-top:35px;color:#8cacce;font-size:.85rem}code{color:#d9ebff}'''


def connect():
    return sqlite3.connect(DB, timeout=10)


def initialize():
    KNOWLEDGE.mkdir(exist_ok=True)
    with closing(connect()) as cx, cx:
        cx.execute('CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(title, content)')
        cx.execute('DELETE FROM documents')
        for file in sorted(KNOWLEDGE.iterdir()):
            if file.is_file() and file.suffix.lower() in ('.txt', '.md') and file.stat().st_size < 2_000_000:
                cx.execute('INSERT INTO documents(title, content) VALUES (?, ?)',
                           (file.name, file.read_text(encoding='utf-8', errors='replace')))


def terms(question):
    words = re.findall(r'\w+', question.casefold(), flags=re.UNICODE)
    return list(dict.fromkeys(w for w in words if w not in STOP_WORDS and len(w) > 1))[:12]


def find_documents(question):
    words = terms(question)
    if not words:
        return []
    query = ' OR '.join('"' + w.replace('"', '') + '"' for w in words)
    with closing(connect()) as cx:
        return cx.execute('SELECT title, content FROM documents WHERE documents MATCH ? '
                          'ORDER BY bm25(documents) LIMIT 5', (query,)).fetchall()


def answer(question):
    """Extract relevant original sentences; never claim generative understanding."""
    keywords = set(terms(question))
    if not keywords:
        return ('Please ask a more specific question, such as “What is DNS?”', [])
    candidates = []
    for rank, (title, content) in enumerate(find_documents(question)):
        for sentence in re.split(r'(?<=[.!?])\s+|\n+', content):
            sentence = sentence.strip().lstrip('#').strip()
            if len(sentence) < 18:
                continue
            text_words = set(re.findall(r'\w+', sentence.casefold()))
            score = len(keywords & text_words)
            if score:
                candidates.append((score, -rank, title, sentence))
    if not candidates:
        return ('I couldn’t find a supported answer in my offline library. Try a different question or add a relevant .md or .txt file to the knowledge folder.', [])
    candidates.sort(reverse=True)
    chosen = candidates[:2]
    excerpts = []
    sources = []
    for _score, _rank, title, sentence in chosen:
        if sentence not in excerpts:
            excerpts.append(sentence[:650])
        if title not in sources:
            sources.append(title)
    return (' '.join(excerpts), sources)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/health':
            self.respond(200, 'text/plain; charset=utf-8', 'OK')
            return
        if parsed.path not in ('/', '/chat'):
            self.send_error(404)
            return
        question = parse_qs(parsed.query).get('q', [''])[0][:MAX_QUESTION].strip()
        discussion = ''
        if question:
            reply, sources = answer(question)
            discussion = ('<div class="chat"><div class="label">YOU</div><div class="bubble user">' +
                          html.escape(question) + '</div><div class="label">PINET ASSISTANT</div>' +
                          '<div class="bubble assistant">' + html.escape(reply))
            if sources:
                discussion += '<div class="source">Source: ' + html.escape(', '.join(sources)) + '</div>'
            discussion += '</div></div>'
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PiNet AI — Offline Assistant</title><style>{CSS}</style></head><body><main><span class="pill">● OFFLINE • LOCAL NETWORK</span><h1>PiNet AI</h1><p>Ask about the documents stored on this Raspberry Pi. Answers are extracted from your offline library—not generated by a language model.</p>{discussion}<form action="/chat" method="get"><input name="q" maxlength="300" placeholder="Ask about DNS, SSH, TCP, networking…" aria-label="Ask the offline assistant" required autofocus><button type="submit">Ask</button></form><p>Try: <a href="/chat?q=What+is+DNS%3F">What is DNS?</a> · <a href="/chat?q=What+does+DHCP+do%3F">What does DHCP do?</a></p><footer>PiNet AI v0.2 • Source-grounded document answers • No internet or API required<br>Everyone connected to this hotspot can access the portal. Do not store private documents here.</footer></main></body></html>'''
        self.respond(200, 'text/html; charset=utf-8', page)

    def respond(self, status, content_type, text):
        body = text.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    initialize()
    print(f'PiNet assistant listening at http://{HOST}:{PORT}', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
