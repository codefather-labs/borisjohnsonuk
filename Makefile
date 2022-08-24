docker_build:
	docker-compose build

linux_build:
	apt-get update
	apt-get install -y python3-dev python3-pip gcc g++ cmake clang libgmp10-dev build-essential libssl-dev libffi-dev ca-certificates mupdf libmupdf-dev mupdf-tools python3-fitz
	python3 -m pip install --upgrade pip
	python3 -m pip install setuptools cython fitz
	python3 -m pip install --upgrade pymupdf PyPDF2

linux_example:
	make linux_build
	python3 . --source_pdf_path books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf --output_dir_path result

macos_build:
	brew install mupdf
	brew install mupdf-tools pymupdf
	brew unlink mupdf
	brew link --overwrite mupdf
	brew istall fitz
	python3 -m pip install --upgrade pip
	python3 -m pip install setuptools cython fitz
	python3 -m pip install --upgrade pymupdf PyPDF2

macos_example:
	make macos_build
	python3 . --source_pdf_path books/Using_Asyncio_in_Python_Understanding_Pythons_Asynchronous_Programming.pdf --output_dir_path result

windows_example:
	# Not tested on windows

debug:
	docker-compose run ubuntu python3 . books/Cython_with_image.pdf && docker-compose down

