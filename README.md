# Local Webtoon CBZ Reader

A high-performance, lightweight, and local web-based Webtoon Archive (CBZ) reader. Built with Python (Flask) on the backend and plain HTML/CSS/JS on the frontend. 

## Features
- **In-Memory Reading:** Zero extraction to disk. Reads images directly from the ZIP structure into RAM, keeping your drive clean and fast.
- **Natural Sorting:** Files and pages are sorted alphanumerically (`Page 2` comes before `Page 10`).
- **Gapless Vertical Scroll:** Images are loaded lazily and stacked with strict zero-margin rules to avoid any visual breaks between pages.
- **Dynamic Page Counter:** Uses JavaScript's `IntersectionObserver` to track reading progress in real-time.
- **Global Drag & Drop:** Drop any `.cbz` file directly into your browser window to instantly load and read it (files are stored securely in system temp folders).
- **Inter-Archive Navigation:** Seamlessly jump to the "Next" or "Previous" volume stored in the same parent directory.

## Prerequisites
- Python 3.7+
- A modern web browser.

## Installation

1. Clone or download this repository.
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can launch the app by targeting either a specific CBZ file or a directory containing multiple CBZ files.

**Option 1: Target a Directory**
```bash
python app.py /path/to/your/manga/folder
```
This opens an index page listing all CBZ archives in the folder. Click on one to start reading.

**Option 2: Target a File directly**
```bash
python app.py "C:\Comics\Batman_Vol_1.cbz"
```
This bypasses the index and jumps directly into the web reader.

Once the script is running, open `http://127.0.0.1:5000` in your web browser. 

*Note: Drag and drop is supported anywhere on the site at any time.*
