"""
GUI for the browser. 

.. note:: important
    
    Should not be publicly hosted.

"""
import sys
import time
import re
import webbrowser
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from decimal import Decimal, InvalidOperation
from cli import get_config, parse_args

from core import Arithmetictrainer, create_arithmetictrainer_from_files

# DATA = Path(__file__).parent.joinpath('data')
# HTML = DATA.joinpath('html/index.html')
# CSS = DATA.joinpath('html/style.css')

DATA = Path(__file__).parent.joinpath('tests')
HTML = DATA.joinpath('index.html')
CSS = DATA.joinpath('style.css')
global trainer


def get_html(html_file: Path, css_file=None, context={}):
    """
    **html_file** is the path to an html file.
    **css_file** is the path to an html file. If the html contains the 'STYLE'
    keyword it gets replaced by the content of **css_file**.
    **context** should be a dictonary, each key found in the html file
    gets replaced by its value.
    """
    if not html_file.is_file():
        raise ValueError(f'[{html_file}] is not a file.')
    with open(html_file) as f:
        html = f.read()
    if css_file != None:
        with open(CSS) as f:
            css = f.read()
        html = html.replace('STYLE', css, 1)
    for k, v in context.items():
        pattern = r'\{\{\s' + k + r'\s\}\}'
        html = re.sub(pattern, str(v), html)
    return html.encode()


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """
        Display the current task.
        """
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        task = trainer.getTask()
        context = trainer.getTask()
        context.update(trainer.getState())
        context['time_since_start'] = time.time(
        ) - trainer.getState()['started_at']
        html = get_html(HTML, css_file=CSS, context=context)
        self.wfile.write(html)

    def do_POST(self):
        """
        Try to answer the current task.
        """
        content_len = int(self.headers.get('Content-Length'))
        data = self.rfile.read(content_len).decode()
        try:
            data = data.split('=')[-1]
            trainer.answer(Decimal(data))
        except InvalidOperation:
            print(f'Could not convert "{data}" to Decimal.')
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def main(arithmetictrainer: Arithmetictrainer, port=8000):
    global trainer
    trainer = arithmetictrainer
    with ThreadingHTTPServer(('localhost', port), Handler) as httpd:
        webbrowser.open_new('http://localhost' + ':' + str(port))
        print("serving at port", port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Keyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == '__main__':
    args = parse_args()
    config = get_config(args)
    trainer = create_arithmetictrainer_from_files(config)
    main(trainer)
