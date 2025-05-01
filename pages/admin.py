from nicegui import ui, app
from utilities.users import get_all_users_logged_in

@ui.page('/admin')
def admin_page():
    with ui.column().classes('w-full items-center'):
        ui.label('Welcome to SV Exploration -- Admin Page --').classes('text-h4 q-mb-md')

        with ui.column().classes('w-full items-center'):
            ui.label('List of Active Users').classes('text-h5 q-my-md text-center')

        # Create table reference
        table = None

        def refresh_table():
            nonlocal table
            if table:
                table.rows = list(app.storage.general.get('user_list', {}).values())
                table.update()


        with ui.row().classes('w-full justify-center gap-4 q-mb-md'):
            ui.button('Return to Home', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white')

        with ui.card().classes('w-full max-w-3xl mx-auto shadow-lg'):

            # Get the data
            data = get_all_users_logged_in()

            # If data exists, create the table
            if len(data) > 0:

                # Create column definitions
                columns = [
                    {'name': key, 
                     'label': key.replace('_', ' ').title(), 
                     'field': key}
                    for key in data[0].keys()
                ]
                
                # Create the table
                ui.table(
                    columns=columns,
                    rows=data,
                    row_key='id'  # Replace 'id' with your primary key column name
                )
            else:
                ui.label('No data found')
            #ui.run()


