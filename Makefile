#!make
PROJECT_VERSION := $(shell python setup.py --version)

SHELL := /bin/bash
PACKAGE := pyhrp

.PHONY: help build test tag


.DEFAULT: help

help:
	@echo "make build"
	@echo "       Build the docker image."
	@echo "make test"
	@echo "       Build the docker image for testing and run them."
	@echo "make doc"
	@echo "       Construct the documentation."
	@echo "make tag"
	@echo "       Make a tag on Github."

build:
	docker-compose build pyhrp

test:
	docker-compose -f docker-compose.test.yml run sut

lint:
	docker-compose -f docker-compose.test.yml run lint


tag: test
	git tag -a ${PROJECT_VERSION} -m "new tag"
	git push --tags
