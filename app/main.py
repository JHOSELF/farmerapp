from fastapi import FastAPI
from .routers import disease, advice, market
from .db import create_database_tables
from fastapi.responses import HTMLResponse

app = FastAPI(
	title="AI Farmer Assistant",
	description="Identify crop diseases from photos, get real-time farming advice, and connect to a simple marketplace.",
	version="0.1.0",
)

@app.on_event("startup")
def on_startup() -> None:
	create_database_tables()

app.include_router(disease.router, prefix="/disease", tags=["Disease Detection"])
app.include_router(advice.router, prefix="/advice", tags=["Farming Advice"])
app.include_router(market.router, prefix="/market", tags=["Marketplace"])

@app.get("/health")
def health() -> dict:
	return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
	html = """
	<!doctype html>
	<html lang=\"en\">
	<head>
		<meta charset=\"utf-8\" />
		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
		<title>AI Farmer Assistant</title>
		<style>
			body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 20px; }
			h1 { margin-bottom: 4px; }
			section { border: 1px solid #ddd; padding: 16px; border-radius: 8px; margin: 16px 0; }
			label { display: block; margin: 6px 0 2px; font-weight: 600; }
			input, select, button, textarea { padding: 8px; font-size: 14px; }
			pre { background: #f6f8fa; padding: 8px; border-radius: 6px; overflow: auto; }
			.grid { display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
			.small { font-size: 12px; color: #666; }
		</style>
	</head>
	<body>
		<h1>AI Farmer Assistant</h1>
		<p class=\"small\"><a href=\"/docs\" target=\"_blank\">Open API Docs</a> • <a href=\"/health\" target=\"_blank\">Health</a></p>

		<section>
			<h2>Disease detection</h2>
			<input type=\"file\" id=\"diseaseImage\" accept=\"image/*\" />
			<button onclick=\"detectDisease()\">Identify disease</button>
			<pre id=\"diseaseOut\"></pre>
		</section>

		<section>
			<h2>Real-time advice</h2>
			<div class=\"grid\">
				<div>
					<label>Crop name</label>
					<input id=\"advCrop\" placeholder=\"maize\" value=\"maize\" />
				</div>
				<div>
					<label>Growth stage</label>
					<select id=\"advStage\">
						<option>pre-planting</option>
						<option selected>vegetative</option>
						<option>flowering</option>
						<option>fruiting</option>
						<option>harvest</option>
					</select>
				</div>
				<div>
					<label>Soil pH</label>
					<input id=\"advPh\" type=\"number\" step=\"0.1\" placeholder=\"6.5\" />
				</div>
				<div>
					<label>Rain last 7d (mm)</label>
					<input id=\"advRain\" type=\"number\" step=\"1\" placeholder=\"20\" />
				</div>
				<div>
					<label>Temperature (°C)</label>
					<input id=\"advTemp\" type=\"number\" step=\"0.1\" placeholder=\"30\" />
				</div>
				<div>
					<label>Soil type</label>
					<input id=\"advSoil\" placeholder=\"loam\" />
				</div>
				<div>
					<label>Irrigation available</label>
					<select id=\"advIrr\"><option value=\"true\">true</option><option value=\"false\">false</option></select>
				</div>
			</div>
			<button onclick=\"getAdvice()\">Get advice</button>
			<pre id=\"adviceOut\"></pre>
		</section>

		<section>
			<h2>Price suggestion</h2>
			<div class=\"grid\">
				<div>
					<label>Crop name</label>
					<input id=\"priceCrop\" placeholder=\"maize\" value=\"maize\" />
				</div>
				<div>
					<label>Location</label>
					<input id=\"priceLoc\" placeholder=\"lagos\" value=\"lagos\" />
				</div>
			</div>
			<button onclick=\"getPrice()\">Suggest price</button>
			<pre id=\"priceOut\"></pre>
		</section>

		<section>
			<h2>Marketplace (demo)</h2>
			<div class=\"grid\">
				<div>
					<label>New user name</label>
					<input id=\"mkUserName\" placeholder=\"Amina\" />
					<label>Phone</label>
					<input id=\"mkUserPhone\" placeholder=\"+23470000000\" />
					<label>Role</label>
					<select id=\"mkUserRole\"><option>farmer</option><option>buyer</option></select>
					<button onclick=\"mkCreateUser()\">Create user</button>
				</div>
				<div>
					<label>New listing crop</label>
					<input id=\"mkListCrop\" placeholder=\"maize\" />
					<label>Quantity (kg)</label>
					<input id=\"mkListQty\" type=\"number\" step=\"1\" placeholder=\"500\" />
					<label>Price per kg</label>
					<input id=\"mkListPpk\" type=\"number\" step=\"0.01\" placeholder=\"0.25\" />
					<label>Location</label>
					<input id=\"mkListLoc\" placeholder=\"lagos\" />
					<label>Seller ID</label>
					<input id=\"mkListSeller\" type=\"number\" placeholder=\"1\" />
					<button onclick=\"mkCreateListing()\">Create listing</button>
				</div>
				<div>
					<label>Order listing ID</label>
					<input id=\"mkOrderListing\" type=\"number\" placeholder=\"1\" />
					<label>Buyer ID</label>
					<input id=\"mkOrderBuyer\" type=\"number\" placeholder=\"2\" />
					<label>Quantity (kg)</label>
					<input id=\"mkOrderQty\" type=\"number\" placeholder=\"100\" />
					<button onclick=\"mkCreateOrder()\">Create order</button>
				</div>
			</div>
			<pre id=\"marketOut\"></pre>
		</section>

		<script>
		async function detectDisease() {
			const file = document.getElementById('diseaseImage').files[0];
			if (!file) { alert('Choose an image'); return; }
			const form = new FormData();
			form.append('image', file);
			const res = await fetch('/disease/identify', { method: 'POST', body: form });
			document.getElementById('diseaseOut').textContent = JSON.stringify(await res.json(), null, 2);
		}

		async function getAdvice() {
			const payload = {
				crop_name: document.getElementById('advCrop').value,
				growth_stage: document.getElementById('advStage').value,
				soil_ph: parseFloat(document.getElementById('advPh').value) || null,
				rainfall_mm_last_7d: parseFloat(document.getElementById('advRain').value) || null,
				temperature_c: parseFloat(document.getElementById('advTemp').value) || null,
				soil_type: document.getElementById('advSoil').value || null,
				irrigation_available: document.getElementById('advIrr').value === 'true'
			};
			const res = await fetch('/advice/recommend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
			document.getElementById('adviceOut').textContent = JSON.stringify(await res.json(), null, 2);
		}

		async function getPrice() {
			const crop = encodeURIComponent(document.getElementById('priceCrop').value);
			const loc = encodeURIComponent(document.getElementById('priceLoc').value);
			const res = await fetch(`/market/price_suggestion?crop_name=${crop}&location=${loc}`);
			document.getElementById('priceOut').textContent = JSON.stringify(await res.json(), null, 2);
		}

		async function mkCreateUser() {
			const payload = { name: document.getElementById('mkUserName').value, phone: document.getElementById('mkUserPhone').value, role: document.getElementById('mkUserRole').value };
			const res = await fetch('/market/users', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
			document.getElementById('marketOut').textContent = JSON.stringify(await res.json(), null, 2);
		}

		async function mkCreateListing() {
			const payload = {
				crop_name: document.getElementById('mkListCrop').value,
				quantity_kg: parseFloat(document.getElementById('mkListQty').value),
				price_per_kg: parseFloat(document.getElementById('mkListPpk').value),
				location: document.getElementById('mkListLoc').value,
				seller_id: parseInt(document.getElementById('mkListSeller').value)
			};
			const res = await fetch('/market/listings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
			document.getElementById('marketOut').textContent = JSON.stringify(await res.json(), null, 2);
		}

		async function mkCreateOrder() {
			const payload = {
				listing_id: parseInt(document.getElementById('mkOrderListing').value),
				buyer_id: parseInt(document.getElementById('mkOrderBuyer').value),
				quantity_kg: parseFloat(document.getElementById('mkOrderQty').value)
			};
			const res = await fetch('/market/orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
			document.getElementById('marketOut').textContent = JSON.stringify(await res.json(), null, 2);
		}
		</script>
	</body>
	</html>
	"""
	return HTMLResponse(content=html)