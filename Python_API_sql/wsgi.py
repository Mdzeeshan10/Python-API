# from waitress import serve
# from app import app

# def create_app():
#     return app

# if __name__ == "__main__":
#     serve(create_app, host="0.0.0.0", port=5000)

from waitress import serve
from app import app

def create_app():
    return app

if __name__ == "__main__":
    application = create_app()
    serve(application, host="0.0.0.0", port=5000)


