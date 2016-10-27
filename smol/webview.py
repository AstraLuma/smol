"""
Runtime for flexx
"""
import webview
import threading
from webview import OPEN_DIALOG, FOLDER_DIALOG, SAVE_DIALOG
import asyncio


# FIXME: Multiple
class WebviewThread(threading.Thread):
    """
    Webview as a thread.
    """
    def __init__(self, title, url="", width=800, height=600, resizable=True, fullscreen=False, min_size=(200, 100)):
        """
        Create a web view window using a native GUI. The execution blocks after this function is invoked, so other
        program logic must be executed in a separate thread.
        :param title: Window title
        :param url: URL to load
        :param width: Optional window width (default: 800px)
        :param height: Optional window height (default: 600px)
        :param resizable True if window can be resized, False otherwise. Default is True
        :param fullscreen: True if start in fullscreen mode. Default is False
        :param min_size: a (width, height) tuple that specifies a minimum window size. Default is 200x100
        :param webview_ready: threading.Event object that is set when WebView window is created
        :return:
        """
        super().__init__(name='webview', daemon=True)
        self._args = {k:v for k,v in locals().items() if k != self and not k.startswith('_')}
        del self._args['self']

    def run(self):
        webview.create_window(**self._args)

    def close(self):
        """
        Destroy a web view window
        """
        webview.destroy_window()

    def load_url(self, url):
        """
        WARNING: May segfault with PyWebview v1.2.2
        Load a new URL into a previously created WebView window. This function must be invoked after WebView windows is
        created with create_window(). Otherwise an exception is thrown.
        :param url: url to load
        """
        webview.load_url(url)

    def load_html(self, content, base_uri=""):
        """
        Load a new content into a previously created WebView window. This function must be invoked after WebView windows is
        created with create_window(). Otherwise an exception is thrown.
        :param content: Content to load.
        :param base_uri: Base URI for resolving links. Default is "".
        """
        webview.load_html(content, base_uri)

    async def create_file_dialog(self, dialog_type=OPEN_DIALOG, directory='', allow_multiple=False, save_filename=''):
        """
        Create a file dialog
        :param dialog_type: Dialog type: open file (OPEN_DIALOG), save file (SAVE_DIALOG), open folder (OPEN_FOLDER). Default
                            is open file.
        :param directory: Initial directory
        :param allow_multiple: Allow multiple selection. Default is false.
        :param save_filename: Default filename for save file dialog.
        :return:
        """
        return await asyncio.get_event_loop().run_in_executor(None, webview.create_file_dialog, dialog_type, directory, allow_multiple, save_filename)