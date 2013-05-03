#!/bin/sh

f() {
    echo "$*"
    $*
}

echo "compiling"
f pyuic4 mainWindowUI.ui -o mainWindowUI.py
f pyuic4 importWindowUI.ui -o importWindowUI.py
f pyrcc4 regaudio.qrc -py3 -o regaudio_rc.py
echo "done"
