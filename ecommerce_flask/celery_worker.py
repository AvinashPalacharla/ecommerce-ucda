#!/usr/bin/env python

import os
from dotenv import load_dotenv
from ecom import create_app
from ecom.extensions import celery

load_dotenv(".env")
app = create_app()
app.app_context().push()
