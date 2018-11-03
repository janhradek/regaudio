#!/bin/sh

f() {
    echo "$*"
    $*
}

echo "compiling"
f pyuic5 mainWindowUI.ui -o mainWindowUI.py
f pyuic5 importWindowUI.ui -o importWindowUI.py
f pyrcc5 regaudio.qrc -o regaudio_rc.py
echo "done"
