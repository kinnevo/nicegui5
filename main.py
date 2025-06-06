from nicegui import ui, app
from datetime import datetime, timedelta
import uuid
import secrets
import random
from utilities.utils import initialize_users
from utilities.database import UserDB
from pages.admin import admin_page
from pages.home1 import home1
from pages.langflow_chat import chat_page


@ui.page('/')
def home():
    with ui.column().classes('w-full items-center'):
        ui.label('Prepara tu exploración al Silicon Valley').classes('text-h3 q-mb-md')
        ui.label('Explora en forma colaborativa tu experiencia de planear una visita al Silicon Valley').classes('text-h5 q-mb-md')
        
        with ui.row().classes('w-full items-center'):

            # Left column with text
            with ui.column().classes('w-2/5'):  # Takes up 50% of the width
                ui.label('Conversa con Lucy, nuestra guía y mentora que te ayudará a descubrir como hacer mas valiosa y productiva tu próxima visita al Silicon Valley').classes('text-body1 q-mb-md text-left')            
                ui.label('Durante una conversación de descubrimiento generas ideas y material, al igual que otros participantes, que como tu quieren vivir la experiencia de un viaje a la innovación.').classes('text-body1 q-mb-md text-left')            
                ui.label('Al final de tu conversación, que puede ser una o varias conversaciones. Te compartiremos el resumen de cada conversación y un reporte de los puntos de interés y experiencias que los otros participantes que podrían ser tus compañeros de viaje quieren experimentar.').classes('text-body1 q-mb-md text-left')    
                ui.label('Este resumen, en colaboración con nuestro equipo de expertos es un material de referencia para construir tu agenda y abrir la mente que hará a tu viaje ser un viaje de aprendizaje y exploración.').classes('text-body1 q-mb-md text-left')            
            
                with ui.row().classes('w-full justify-center'):
                    ui.button('Planear  ...').classes('text-h6 q-mb-md').on_click(lambda: ui.navigate.to('/chat'))

            # Right column with image
            with ui.column().classes('w-2/5'):  # Takes up 50% of the width
                ui.image('static/visit_sv_cover.jpeg').classes('w-full rounded-lg shadow-lg')

        
        ui.label('Inicia tu experiencia ahora mismos y crear tu futuro innovando.').classes('text-h6 q-mb-md')
        ui.html('<strong>Aviso de Privacidad</strong>: Las conversaciones en este sitio son almacenadas de manera anónima con el propósito exclusivo de analizar los intereses de los participantes y mejorar el desarrollo de experiencias de conocimiento. Toda la información recopilada es para uso interno y no será compartida con terceros.').classes('text-body2 q-mb-md text-justify')

      
@app.on_shutdown
def shutdown():
    # This code runs when the app is shutting down
    print("Application is shutting down...")
    # Clean up resources, close connections, etc.
    # Cleanup code here
    pass


@app.on_startup
def on_startup():
    print("Starting up...")

    app.storage.general['user_list'] = initialize_users()
    print("Initializing users...")

    # Initialize database
    print("Initializing database...")
    user_db = UserDB()
    user_db._init_db()
    print("Database initialized")


secret_key = secrets.token_hex(32)
ui.run(title='SV Exploration', port=8080, favicon='static/favicon.svg', storage_secret=secret_key) 
