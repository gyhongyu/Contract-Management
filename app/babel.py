from flask import current_app

def _(key, **variables):
    if hasattr(current_app, 'custom_translate'):
        return current_app.custom_translate(key, **variables)
    return key