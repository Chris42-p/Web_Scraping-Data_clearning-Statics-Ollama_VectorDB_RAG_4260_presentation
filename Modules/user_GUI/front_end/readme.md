## Frontend Setup and Run

The frontend is located in:

```bash
Modules/user_GUI/front_end
```

### Frontend requirements
- Node.js
- npm
- Frontend dependencies installed with `npm install`

### Steps to start the frontend

1. Open a terminal.
2. Go to the frontend folder:

```bash
cd Modules/user_GUI/front_end
```

3. Install dependencies:

```bash
npm install
```

4. Start the frontend development server:

```bash
npm run dev
```

5. Open the local frontend URL shown in the terminal, usually:

```bash
http://localhost:5173
```

### Frontend notes
- Run the frontend command only inside the `front_end` folder.
- If PowerShell blocks npm, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```