paleocore110
==================

paleocore django 1.11

Installation
------------
- Clone the repository from github.


    git clone https://github.com/paleocore/paleocore110

- Create a new Python virtual environment.


    virtualenv -p python3 venv

- Start the virtual environment and install the python libraries stipulated in the requirements file. Separate
files stipulate a base set of libraries which are imported into dev and production requirement files.


    $ source venv/bin/activate
    $ pip install -r requirements/dev.txt

-  Create the database. Assuming the database software is installed. The default database for this project uses 
postgreSQL. The simplest method of implementing the database is using [postgres.app](http://postgresapp.com).


    $ createdb paleocore110

OR load initial data from a backup of an existing paleocore DB.

    $ pg_dump -C - h localhost paleocore110 > paleocore110_data.sql
    $ psql < paleocore110_data.sql
     
- Run migrations.


    $ source venv/bin/activate
    (venv) python manage.py migrate



    
