#!/usr/bin/env python
import os
from app import create_app

app = create_app(os.getenv('FLASK_BMS_ENV') or 'default')

if __name__ == '__main__':
    app.run()