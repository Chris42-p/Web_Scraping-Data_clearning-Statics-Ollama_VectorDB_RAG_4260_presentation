## Running Frontend and Backend Together

Please see the `README files` in the `frontend` and `backend` folders for setup and run instructions for each service.

For local development, keep **two terminals open**:

### Terminal 1
Run the frontend:

```bash
cd Modules/user_GUI/front_end
npm install
npm run dev
```

### Terminal 2
Run the backend:

```bash
cd Modules/user_GUI/back_end
npm install
npm run dev
```

or use the appropriate Python command if the backend is not Node.

---

## Troubleshooting

### npm error: `ENOENT`
This usually means you are running `npm` in the wrong folder.
Make sure you are inside the folder that contains `package.json`.

### PowerShell blocks npm
Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Backend command not working
Check whether the backend is:
- Node (`package.json`)
- FastAPI (`main.py`)
- Flask (`app.py`)
- Django (`manage.py`)

Then run the matching command.

---

## Current Status

- Frontend structure and app feature pages are in progress.
- Styling is not fully complete yet.
- Some backend integration is still pending.