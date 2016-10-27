#!/usr/bin/env python
import logging
from smol.webview import WebviewThread

logging.basicConfig(level=logging.DEBUG)

wv = WebviewThread('Test')
wv.start()

wv.load_html("Hello, world!")
