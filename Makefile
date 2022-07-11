build:
	docker-compose build

example:
	docker-compose run ubuntu python3 marklify.py books/CPython_Internals.pdf && docker-compose down