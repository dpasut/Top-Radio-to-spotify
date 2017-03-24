.PHONY: build run full-reset

full-reset: run

build:
	docker build -f Dockerfile -t radio-spotify .

run: build
	touch data.db
	docker run -ti --rm --name radio-spotify -v $(shell pwd)/data.db:/usr/src/app/data.db radio-spotify python2 load.py
