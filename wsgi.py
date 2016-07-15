# wsgi.py
# uWSGI application entry point

from finance import application

if __name__ == "__main__":
	application.run()
