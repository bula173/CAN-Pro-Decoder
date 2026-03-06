# CAN Pro-Decoder v0.3

A high-performance CAN log analyzer and signal visualizer built for Windows using Python, Tkinter, and Matplotlib. Specifically optimized for the **MSYS2 UCRT64** environment.

## Features
* **DBC Parsing**: Load standard `.dbc` files to decode raw CAN traffic.
* **ASC Log Support**: Process Vector ASCII log files.
* **Live Filtering**: Search by Message Name or ID in real-time.
* **Signal Analysis**: Graph multiple signals on a synchronized timeline.
* **Signal Inspector**: Detailed breakdown of physical values and units.

## Installation (MSYS2 UCRT64)

This project requires the Universal C Runtime (UCRT) version of Python for maximum stability.

1. **Install MSYS2**: Download from [msys2.org](https://www.msys2.org/).
2. **Open UCRT64 Terminal** (Yellow icon).
3. **Install System Dependencies**:
   ```bash
   pacman -S --needed mingw-w64-ucrt-x86_64-python-pandas \
                      mingw-w64-ucrt-x86_64-python-matplotlib \
                      mingw-w64-ucrt-x86_64-python-pip \
                      mingw-w64-ucrt-x86_64-python-pyinstaller