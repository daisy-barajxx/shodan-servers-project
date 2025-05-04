#!/bin/bash

TEMP_DIR=temp

echo "Starting deb package build"

echo "Making temporary directory tree"
mkdir -p $TEMP_DIR
mkdir -p $TEMP_DIR/etc/
mkdir -p $TEMP_DIR/usr/local/bin/
mkdir -p $TEMP_DIR/etc/systemd/system/
mkdir -p $TEMP_DIR/DEBIAN

echo "Copy control postinst, prerm, and postrm scripts for DEBIAN/"
cp src/debian/control $TEMP_DIR/DEBIAN/
cp src/debian/postinst $TEMP_DIR/DEBIAN/
cp src/debian/prerm $TEMP_DIR/DEBIAN/
cp src/debian/postrm $TEMP_DIR/DEBIAN/

chmod 755 $TEMP_DIR/DEBIAN/postinst
chmod 755 $TEMP_DIR/DEBIAN/prerm
chmod 755 $TEMP_DIR/DEBIAN/postrm

# Copy service and binary
cp shodan.service $TEMP_DIR/etc/systemd/system/
cp src/shodan_service.py $TEMP_DIR/usr/local/bin/
chmod +x $TEMP_DIR/usr/local/bin/shodan_service.py

echo "Building deb package"
dpkg-deb --root-owner-group --build $TEMP_DIR
mv $TEMP_DIR.deb shodansvc-v1.0.0.deb
echo "Package: shodansvc-v1.0.0.deb"

