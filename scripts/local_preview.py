"""Run the static pages and the Vercel-style diagnosis endpoint together locally.

Use only for development previews. Production deployment is handled by Vercel.
"""

from __future__ import annotations

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))
from diagnose import handler as DiagnoseHandler  # noqa: E402


class LocalPreviewHandler(SimpleHTTPRequestHandler, DiagnoseHandler):
    """Serve static files, and delegate only ``/api/diagnose`` to the API handler."""

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/diagnose":
            DiagnoseHandler.do_POST(self)
            return
        self.send_error(405, "POST is only supported for /api/diagnose")

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path == "/api/diagnose":
            DiagnoseHandler.do_OPTIONS(self)
            return
        self.send_error(405)


if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    address = ("127.0.0.1", 4173)
    print("Tax Reset preview: http://127.0.0.1:4173")
    ThreadingHTTPServer(address, LocalPreviewHandler).serve_forever()
