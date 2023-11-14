import os
from . import create_app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    app.run(debug=True, port=port)

