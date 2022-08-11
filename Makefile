build:
	docker-compose build

example:
	docker-compose run ubuntu python3 marklify.py books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf && docker-compose down