StashControl is a prototype for a medical cannabis usage tracking system. It uses Django, React (not yet!), and Plotly.js to deliver a web-based version of the app that aims to provide a minimum viable product (MVP) for alpha testing with a select group of patients.

Requirements
------------

python3.13+
postgres14+ (optional - sqlite can be used in development)

To use sqlite, set the following environment variable:

    DJANGO_SETTINGS_MODULE=stashcontrol.sqlite
	
If you are using postgreql, make sure you have created a database that matches the settings in https://github.com/tttallis/stashcontrol/blob/04a6bea6e2b9c1ebdd0da6b81b7baba8e0982555/stashcontrol/settings.py#L83-L102


Installation
------------

    git clone git@github.com:tttallis/stashcontrol.git
	cd stashcontrol
	./start
	
The start script:
- creates and invokes a virtualenv if it doesn't already exist
- installs all python requirements
- runs any database migrations that may be required
- creates a superuser with the name `dev` and the password `w33d!`
- loads some sample measurements for the `dev` user

Development server
-------------------

    ./manage.py runserver
	
will start a development server, which can be accessed at http://localhost:8000/. There is also a django admin interface available at http://localhost:8000/admin/.