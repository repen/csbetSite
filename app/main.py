from Globals import PRODUCTION_WORK

def create_app():
    from app_main import app
    return app

def run_app_production(app):
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

def run_app_develop(app):
    app.run(port=5000, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    Application = create_app()
    if PRODUCTION_WORK:
        run_app_production(Application)
    else:
        run_app_develop(Application)

