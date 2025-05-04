#!/bin/bash

# lint the debian package using lintian
echo "Linting the debian package..."
# run lintian to check the deb package
lintian shodansvc-v1.0.0.deb

