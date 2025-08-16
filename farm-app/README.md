# FarmHub

Offline-first farm management web app (PWA) for fields, tasks, weather, inventory, and finances. No backend required; data is stored locally in your browser.

## Features
- Weather dashboard via Open-Meteo (no API key)
- Field registry (name, crop, area, sowing date)
- Task manager with due dates and field linkage
- Inventory tracker
- Simple finance ledger (income/expense)
- Import/Export data (JSON)
- Offline support (Service Worker) and installable PWA

## Run locally
1. Serve the folder with any static server:
   - Python: `python3 -m http.server 5173` (from this directory)
   - Node: `npx serve -p 5173 .`
2. Open `http://localhost:5173/` in your browser.

## Notes
- Set your farm location in Settings for weather.
- All data lives in localStorage; exporting regularly is recommended.