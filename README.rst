YafBlog - Yet Another Flask Blog
================================

Simple blog application written with Flask and PostgreSQL.


Features:

* Simple full text search
* Authentication for admin user
* Posts with tags (posts may be composed with html)


TODO:

* CSRF protection
* support for a markup language
* post preview


Run
---

    pip install -r requirements.txt

    createdb yafblog-db

    python syncdb.py

    python run.py


Development
-----------

    git clone

Install requirements

    pip install -r requirements-dev.txt

Create postgresql database

    createdb yafblog-test-db

Run tests

    flake8 . && py.test tests/ --cov=yafblog
