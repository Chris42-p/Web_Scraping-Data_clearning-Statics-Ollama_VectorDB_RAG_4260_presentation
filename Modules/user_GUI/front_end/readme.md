# Frontend Setup and Run

The frontend app is located in `Modules/user_GUI/front_end`. This guide explains how to install the required dependencies, start the Vite development server, and troubleshoot common local setup issues for the dashboard frontend.

## Prerequisites

Before starting, make sure the following tools are installed on the machine:

- Node.js
- npm
- A terminal such as PowerShell, Command Prompt, Git Bash, or the VS Code terminal

To confirm Node.js and npm are available, run:

```bash
node -v
npm -v
```

## Project location

Open a terminal and move into the frontend folder:

```bash
cd Modules/user_GUI/front_end
```

All frontend commands in this guide should be run from that folder. Installing packages from the wrong directory can lead to missing dependencies in the actual frontend app.

## Install dependencies

Install the project dependencies first:

```bash
npm install
```

If the dashboard uses charts, maps, and icons, make sure these packages are installed in the frontend folder:

```bash
npm install recharts react-leaflet leaflet lucide-react
```

These libraries are used for:

- `recharts` for dashboard charts.
- `react-leaflet` and `leaflet` for the map display.
- `lucide-react` for UI icons.

React Leaflet requires React, React DOM, and Leaflet as peer dependencies, so those packages must remain installed and compatible with one another.

If the project uses TypeScript and Leaflet type errors appear, install the Leaflet type package as a dev dependency:

```bash
npm install -D @types/leaflet
```

## Start the development server

Run the frontend locally with:

```bash
npm run dev
```

Vite commonly starts its local development server on `http://localhost:5173`, though it may choose another port if 5173 is already in use.

Always open the exact local URL printed in the terminal after the dev server starts.

## Recommended first run flow

For a clean first setup on a new machine, use this order:

1. Open the terminal.
2. Go to `Modules/user_GUI/front_end`.
3. Run `npm install`.
4. Run `npm install recharts react-leaflet leaflet lucide-react`.
5. If TypeScript reports missing Leaflet types, run `npm install -D @types/leaflet`.
6. Run `npm run dev`.
7. Open the frontend URL shown in the terminal.

## Leaflet map note

If the map renders but appears blank, broken, or missing tiles, make sure the Leaflet stylesheet is imported in the dashboard-related component or the frontend entry point, because React Leaflet depends on the Leaflet CSS for proper marker and tile rendering.

Typical import:

```ts
import "leaflet/dist/leaflet.css";
```

A Leaflet map also needs an explicit height on its container. If the map area exists in the DOM but is not visibly rendering, check the relevant CSS classes and make sure the map wrapper has a fixed or minimum height.

## React version check

If the page stops rendering after package installation, check that `react` and `react-dom` are both installed and on matching versions:

```bash
npm ls react react-dom
```

The safest rule is to keep `react` and `react-dom` on matching versions and avoid forcing a React upgrade unless the project dependencies require it.

If `package.json` changes, run:

```bash
npm install
```

## Vite port note

If needed, you can temporarily run the dev server on another port:

```bash
npm run dev -- --port 3000
```

If you want to expose the development server to other devices on the same network, run:

```bash
npm run dev -- --host
```

## PowerShell execution policy

If PowerShell blocks npm scripts on Windows, run the following command once in PowerShell and then retry the install or dev command:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Common troubleshooting

### Missing modules

If errors mention packages such as `recharts`, `react-leaflet`, `leaflet`, or `lucide-react`, reinstall them from the frontend folder:

```bash
npm install recharts react-leaflet leaflet lucide-react
```

If TypeScript errors mention missing Leaflet types, install:

```bash
npm install -D @types/leaflet
```

### Leaflet map issues

If the map area is visible but markers or tiles do not display correctly, check these first:

- `import "leaflet/dist/leaflet.css";` is present.
- The map container has an explicit height in CSS.
- Latitude and longitude values from the API are converted to numbers before rendering markers.
- Frontend commands were run in `Modules/user_GUI/front_end`, not at the project root.

### Clean reinstall

If dependencies become inconsistent, remove installed packages and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

On Windows Command Prompt, remove them with:

```cmd
rmdir /s /q node_modules
del package-lock.json
npm install
```

On PowerShell, use:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Port already in use

If port `5173` is already taken, Vite may automatically switch to another local port. Use the URL printed in the terminal instead of assuming the app will always run on port 5173.

### Wrong working directory

If a `cd` command fails because the path appears duplicated, you are probably already inside `Modules/user_GUI/front_end`. In that case, run `npm install` or `npm run dev` directly instead of changing into the same folder again.

## Team notes

- Always run frontend commands inside `Modules/user_GUI/front_end`.
- Install new frontend libraries in the frontend folder, not at the project root.
- When adding dashboard features such as charts or maps, confirm the required packages are installed before debugging application code.
- For the current dashboard map setup, `react-leaflet` and `leaflet` are required; the current implementation does not depend on a clustering package.

## Citation notes

-  Project-specific setup details from the shared frontend instructions in this conversation.
-  React Leaflet installation requirements and CSS dependency guidance.
-  Vite commonly uses localhost:5173 for local development.
-  Vite may switch ports automatically when the default port is occupied.
-  React version troubleshooting guidance for checking installed `react` and `react-dom` versions.