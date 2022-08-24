build:
	docker-compose build

linux_example:
	python3 . --source_pdf_path books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf --output_dir_path result

macos_example:
	brew install mupdf
	brew install mupdf-tools pymupdf
	brew unlink mupdf
	brew link --overwrite mupdf
	brew istall fitz
	python3 -m pip install --upgrade pip
	python3 -m pip install setuptools cython fitz
	python3 -m pip install --upgrade pymupdf PyPDF2
	python3 . --source_pdf_path books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf --output_dir_path result

windows_example:
	# Not tested on windows

debug:
	docker-compose run ubuntu python3 . books/Cython_with_image.pdf && docker-compose down

