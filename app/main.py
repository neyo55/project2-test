import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

if __name__ == "__main__":
    logging.basicConfig(
        filename="flask.log",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    app.run(host="0.0.0.0", port=5000, debug=True)
