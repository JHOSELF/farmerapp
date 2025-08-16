# AI Farmer Assistant

Endpoints:

- POST `/disease/identify` (multipart form "image"): detect crop disease from a photo
- POST `/advice/recommend`: real-time advice for planting/soil/irrigation
- POST `/market/users`: create user (farmer or buyer)
- POST `/market/listings`: create a crop listing
- GET `/market/listings`: browse listings
- POST `/market/orders`: create order
- GET `/market/price_suggestion?crop_name=maize&location=lagos`: suggest fair price

Run locally:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Notes:
- Disease model is a placeholder heuristic; swap with a trained model in `app/services/disease_model.py`.
- Data is stored in local SQLite `farmer.db` via SQLAlchemy.