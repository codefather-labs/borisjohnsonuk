build:
	docker-compose build

example:
	docker-compose run ubuntu python3 marklify.py books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf && docker-compose down

debug:
	docker-compose run ubuntu python3 . books/Cython_with_image.pdf && docker-compose down

test_translate:
	python3 translator.py test