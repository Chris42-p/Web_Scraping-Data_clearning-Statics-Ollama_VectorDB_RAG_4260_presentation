## Backend Setup and Run

The backend must be run separately from the frontend in a different terminal.

### Backend requirements
- Node.js and npm if the backend is a Node project
- or Python if the backend is a Python project
- Backend dependencies installed in the backend folder
- Any required environment variables or `.env` file

### Steps to find the backend folder

From the project root, search for the backend app files.

#### If backend is Node
Run:

```powershell
Get-ChildItem -Path . -Recurse -File -Filter package.json | Where-Object { $_.FullName -notmatch 'node_modules' }
```

This will show the real project folders that contain `package.json`.

#### If backend is Python
Run:

```powershell
Get-ChildItem -Path . -Recurse -Include app.py,main.py,requirements.txt,manage.py -File
```

This will help identify whether the backend uses Flask, FastAPI, or Django.

### Start a Node backend
Backend has a `package.json`, open a second terminal and run:

```bash
cd Modules/user_GUI/back_end
npm install
npm run dev
```

If `npm run dev` does not work, check available scripts:

```bash
npm run
```

Then use the correct script, for example:

```bash
npm start
```

### Start a FastAPI backend
For FastAPI, run:

```bash
cd Modules/user_GUI/back_end
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend usually runs on:

```bash
http://localhost:8000
```

