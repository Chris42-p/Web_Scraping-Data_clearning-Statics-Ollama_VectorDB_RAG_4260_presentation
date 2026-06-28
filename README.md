# 4260_presentation
This is a repo for Big Data class. We're going to demo a vector database.  

# Installing dependenices. 
- Make virtual Env for packages:~/Desktop/4260_presentation$ sudo python3 -m venv package_manager
- Activate package manager: ~/Desktop/4260_presentation$ source ./package_manager/bin/activate
- Installing dependences: pip install -r requirements.txt 
- Deactivating the Env: (package_manager) chris@chris-DevBox:~/Desktop/4260_presentation$ deactivate

# Ollama install 
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.3.14 sh

# Todo 

4260_presentation/Modules/engine_injesting/injest_engine.py: __read_a_document
     - we should save change the output to an object to get more data out of the files. 

4260_presentation/Modules/engine_injesting/injest_engine.py: __ocr_my_pdf    
     - bug: documents are OCRed, then on rerun of object we need to check if the documents have a version called same title_ocr then we know they have been processed. 
          -Optical Character Recognition: OCR: used to turn pictures of letters into letters that the computer can read/find. 

The demo documents should be updated with tables, and images to ensure we can catch all the forms of data. 




# todo: Refactor
- in the __init__.py we need to change exporting of objects to exporting of interfaces, dont want the user calling class.objs ()


# arch

     document needs to have a docker image to run this in, or a virtual env. 
          self contained code that's scalable. --professional ;)

## using an intermediate database .
     this is to increase job reliance. 


## Vector databases 

### what is a vector?


### what is a vector database?



### what is encoding 


### what can it be used for





---
## Docker Setup

### Why
Docker is used to create a self-contained environment so that all team members
can run the same code regardless of their operating system (Windows, macOS, Linux).
This avoids the "works on my machine" problem and ensures consistent results.


### How
- `Dockerfile` — defines the Python 3.11 environment and installs all dependencies
- `docker-compose.yml` — orchestrates 3 services:
  - `ollama` — runs the local LLM (llama3.2) on port 11434
  - `app` — runs the document ingestion pipeline
  - `backend` — runs the FastAPI backend on port 8000
- Volumes are mounted so files persist between runs:
  - `__ingest_file/` — input documents
  - `__processed_file/` — processed documents
  - `data_base/` — SQLite database


### Bugs
- `version: '3.8'` in docker-compose.yml is obsolete — can be removed
- ollama takes 2-3 minutes to load llama3.2 on first run (4+ GiB model)
- Orphan containers warning appears when running after previous failed runs
  - Fix: `docker-compose down --remove-orphans` then `docker-compose up --build`

---

### Install Docker

Usually, it is good enough to ask an AI for how to install Docker tailored to your specific environment.

#### Windows
Doc: [windows-install](https://docs.docker.com/desktop/setup/install/windows-install/)

1. Install WSL
wsl.exe --install
wsl.exe --update

2. Download Installer from https://docs.docker.com/desktop/setup/install/windows-install/
3. Run the Installer — make sure `Use WSL 2` is checked
4. Your Windows might restart after installation

#### macOS
Doc: [macOS](https://docs.docker.com/desktop/setup/install/mac-install/)

---

### Run

#### First Time Setup
docker-compose build
docker-compose exec ollama ollama pull llama3.2

#### Run (after code changes)
docker-compose up --build

#### Run (no changes)
docker-compose up

#### Run in background
docker-compose up -d

#### Check running containers
docker ps

---

### Clean Up

If you need a clean start：
docker-compose down -v
docker-compose up --build

If you see orphan containers warning：
docker-compose down --remove-orphans
docker-compose up --build

---

### Notes
- On first run, ollama may take a few minutes to load llama3.2
