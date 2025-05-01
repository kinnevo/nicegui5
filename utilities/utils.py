import uuid
import datetime
import random
from datetime import datetime, timedelta
from nicegui import app, ui
from utilities.users import set_user_logout


# update the status of a user
def update_user_status(username, session_id):


    set_user_logout(username, session_id)
