# makefile for the debian package

PROJECT_NAME: shodansvc
VERSION: v1.0.0
DEB_NAME = $(PROJECT_NAME)-$(VERSION).deb

# targets
.PHONY: build test clean run build-deb lint-deb 

# build the python program (shodansvc.py)
build:
	./build.sh

# run the project 
run: 
	./run.sh

# clean temp files (including debian packages and binaries) 
clean:
	./clean.sh

# run unit tests
test: 
	./test.sh

# build the debian package
build-deb: build
	./build-deb.sh

# lint the debian package 
lint-deb: build-deb
	./lint-deb.sh