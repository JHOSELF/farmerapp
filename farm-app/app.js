const STORAGE_KEY = 'farmhub_state_v1';

const DEFAULT_STATE = {
  location: { name: '', latitude: null, longitude: null },
  fields: [],
  tasks: [],
  inventory: [],
  finances: []
};

let state = loadState();
let deferredPrompt = null;

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return structuredClone(DEFAULT_STATE);
    const parsed = JSON.parse(raw);
    return { ...structuredClone(DEFAULT_STATE), ...parsed };
  } catch {
    return structuredClone(DEFAULT_STATE);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString();
}

function formatMoney(num) {
  const n = Number(num || 0);
  return n.toLocaleString(undefined, { style: 'currency', currency: 'USD' });
}

function byDateAsc(a, b) {
  const da = new Date(a.due || a.date).getTime();
  const db = new Date(b.due || b.date).getTime();
  return da - db;
}

function setActiveTab(tab) {
  document.querySelectorAll('.tab-link').forEach(btn => {
    const isActive = btn.dataset.tab === tab;
    btn.classList.toggle('text-sky-600', isActive);
    btn.classList.toggle('border-sky-600', isActive);
    btn.classList.toggle('font-semibold', isActive);
    btn.classList.toggle('text-gray-600', !isActive);
    btn.classList.toggle('border-transparent', !isActive);
  });
  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.toggle('hidden', view.id !== `tab-${tab}`);
  });
}

function updateStats() {
  const totalFields = state.fields.length;
  const openTasks = state.tasks.filter(t => !t.completed).length;
  const dueSoon = state.tasks.filter(t => !t.completed && new Date(t.due) <= new Date(Date.now() + 3 * 24 * 3600e3)).length;
  const inventoryItems = state.inventory.length;
  const expenses = state.finances.filter(f => f.type === 'expense').reduce((s, f) => s + Number(f.amount), 0);
  const income = state.finances.filter(f => f.type === 'income').reduce((s, f) => s + Number(f.amount), 0);
  const net = income - expenses;

  const statsEl = document.getElementById('stats');
  statsEl.innerHTML = `
    <div class="p-3 rounded-md border border-gray-200">
      <div class="text-xs text-gray-500">Fields</div>
      <div class="text-lg font-semibold">${totalFields}</div>
    </div>
    <div class="p-3 rounded-md border border-gray-200">
      <div class="text-xs text-gray-500">Open tasks</div>
      <div class="text-lg font-semibold">${openTasks}</div>
    </div>
    <div class="p-3 rounded-md border border-gray-200">
      <div class="text-xs text-gray-500">Due soon</div>
      <div class="text-lg font-semibold">${dueSoon}</div>
    </div>
    <div class="p-3 rounded-md border border-gray-200">
      <div class="text-xs text-gray-500">Inventory items</div>
      <div class="text-lg font-semibold">${inventoryItems}</div>
    </div>
    <div class="p-3 rounded-md border border-gray-200 col-span-2">
      <div class="text-xs text-gray-500">Net</div>
      <div class="text-lg font-semibold ${net >= 0 ? 'text-emerald-600' : 'text-red-600'}">${formatMoney(net)}</div>
    </div>
  `;
}

async function fetchWeather(lat, lon) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Weather fetch failed');
  return await res.json();
}

function renderWeather(weather) {
  const locLabel = document.getElementById('locationLabel');
  if (state.location && state.location.name) {
    locLabel.textContent = state.location.name;
  } else if (state.location.latitude && state.location.longitude) {
    locLabel.textContent = `${state.location.latitude.toFixed(3)}, ${state.location.longitude.toFixed(3)}`;
  } else {
    locLabel.textContent = 'Set your location in Settings';
  }

  const currentEl = document.getElementById('weatherCurrent');
  if (!weather || !weather.current_weather) {
    currentEl.innerHTML = '<div class="col-span-3 text-gray-500">No weather data</div>';
  } else {
    const cw = weather.current_weather;
    currentEl.innerHTML = `
      <div class="p-3 rounded-md border border-gray-200">
        <div class="text-xs text-gray-500">Temperature</div>
        <div class="text-xl font-semibold">${Math.round(cw.temperature)}°C</div>
      </div>
      <div class="p-3 rounded-md border border-gray-200">
        <div class="text-xs text-gray-500">Wind</div>
        <div class="text-xl font-semibold">${Math.round(cw.windspeed)} km/h</div>
      </div>
      <div class="p-3 rounded-md border border-gray-200">
        <div class="text-xs text-gray-500">Time</div>
        <div class="text-xl font-semibold">${new Date(cw.time).toLocaleTimeString()}</div>
      </div>
    `;
  }

  const dailyEl = document.getElementById('weatherDaily');
  if (weather && weather.daily) {
    const days = weather.daily.time.map((t, i) => ({
      date: t,
      tmax: weather.daily.temperature_2m_max[i],
      tmin: weather.daily.temperature_2m_min[i],
      rain: weather.daily.precipitation_sum[i]
    })).slice(0, 5);
    dailyEl.innerHTML = `
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
        ${days.map(d => `
          <div class="p-3 rounded-md border border-gray-200 text-center">
            <div class="text-xs text-gray-500">${new Date(d.date).toLocaleDateString(undefined, { weekday: 'short' })}</div>
            <div class="text-lg font-semibold">${Math.round(d.tmax)}° / ${Math.round(d.tmin)}°</div>
            <div class="text-xs text-gray-500">Rain: ${Math.round(d.rain)} mm</div>
          </div>
        `).join('')}
      </div>
    `;
  } else {
    dailyEl.innerHTML = '';
  }
}

async function updateWeather() {
  const { latitude, longitude } = state.location || {};
  if (!latitude || !longitude) {
    renderWeather(null);
    return;
  }
  try {
    const wx = await fetchWeather(latitude, longitude);
    renderWeather(wx);
  } catch {
    renderWeather(null);
  }
}

function renderFields() {
  const list = document.getElementById('fieldsList');
  if (state.fields.length === 0) {
    list.innerHTML = '<div class="text-gray-500">No fields yet.</div>';
    return;
  }
  list.innerHTML = state.fields.map(f => `
    <div class="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-2">
      <div class="flex items-start justify-between">
        <div>
          <div class="font-semibold">${f.name}</div>
          <div class="text-sm text-gray-600">${f.crop || '—'} · ${f.area ? `${f.area} ha` : '—'}</div>
        </div>
        <button data-action="delete-field" data-id="${f.id}" class="text-red-600 hover:text-red-700 text-sm">Delete</button>
      </div>
      <div class="text-xs text-gray-500">Sowing: ${f.sowing ? formatDate(f.sowing) : '—'}</div>
    </div>
  `).join('');
}

function renderTasks() {
  const list = document.getElementById('tasksList');
  const open = state.tasks.filter(t => !t.completed).sort(byDateAsc);
  if (open.length === 0) {
    list.innerHTML = '<li class="p-4 text-gray-500">No open tasks.</li>';
    return;
  }
  list.innerHTML = open.map(t => {
    const field = state.fields.find(f => f.id === t.fieldId);
    return `
      <li class="p-4 flex items-center justify-between">
        <div>
          <div class="font-medium">${t.title}</div>
          <div class="text-xs text-gray-500">${formatDate(t.due)}${field ? ` · ${field.name}` : ''} · ${t.category}</div>
        </div>
        <div class="flex items-center gap-3">
          <button data-action="complete-task" data-id="${t.id}" class="text-emerald-600 hover:text-emerald-700 text-sm">Complete</button>
          <button data-action="delete-task" data-id="${t.id}" class="text-red-600 hover:text-red-700 text-sm">Delete</button>
        </div>
      </li>`;
  }).join('');

  const filterEl = document.getElementById('taskFilters');
  const categories = Array.from(new Set(state.tasks.map(t => t.category)));
  filterEl.textContent = `${open.length} open · ${categories.length} categories`;
}

function renderUpcomingTasks() {
  const list = document.getElementById('upcomingTasks');
  const soon = state.tasks
    .filter(t => !t.completed && new Date(t.due) >= new Date())
    .sort(byDateAsc)
    .slice(0, 5);
  if (soon.length === 0) {
    list.innerHTML = '<li class="p-3 text-gray-500">Nothing due soon.</li>';
    return;
  }
  list.innerHTML = soon.map(t => {
    const field = state.fields.find(f => f.id === t.fieldId);
    return `<li class="p-3 flex items-center justify-between">
      <div>
        <div class="font-medium">${t.title}</div>
        <div class="text-xs text-gray-500">${formatDate(t.due)}${field ? ` · ${field.name}` : ''} · ${t.category}</div>
      </div>
      <span class="text-xs px-2 py-1 rounded-full bg-sky-50 text-sky-700">Due</span>
    </li>`;
  }).join('');
}

function renderInventory() {
  const list = document.getElementById('inventoryList');
  if (state.inventory.length === 0) {
    list.innerHTML = '<div class="text-gray-500">No inventory items.</div>';
    return;
  }
  list.innerHTML = state.inventory.map(i => `
    <div class="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between">
      <div>
        <div class="font-semibold">${i.name}</div>
        <div class="text-xs text-gray-500">${i.quantity || 0} ${i.unit || ''}</div>
      </div>
      <button data-action="delete-inv" data-id="${i.id}" class="text-red-600 hover:text-red-700 text-sm">Delete</button>
    </div>
  `).join('');
}

function renderFinance() {
  const tbody = document.getElementById('financeTable');
  if (state.finances.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="p-4 text-gray-500">No entries.</td></tr>';
  } else {
    tbody.innerHTML = state.finances.sort((a,b)=>new Date(b.date)-new Date(a.date)).map(f => `
      <tr>
        <td class="p-3">${formatDate(f.date)}</td>
        <td class="p-3">${f.type}</td>
        <td class="p-3">${f.desc}</td>
        <td class="p-3 text-right ${f.type==='expense'?'text-red-600':'text-emerald-600'}">${formatMoney(f.amount)}</td>
        <td class="p-3 text-right"><button data-action="delete-fin" data-id="${f.id}" class="text-red-600 hover:text-red-700 text-sm">Delete</button></td>
      </tr>
    `).join('');
  }
  const expenses = state.finances.filter(f => f.type==='expense').reduce((s,f)=>s+Number(f.amount),0);
  const income = state.finances.filter(f => f.type==='income').reduce((s,f)=>s+Number(f.amount),0);
  const net = income - expenses;
  document.getElementById('financeSummary').textContent = `Income ${formatMoney(income)} · Expenses ${formatMoney(expenses)} · Net ${formatMoney(net)}`;
}

function populateFieldSelects() {
  const selects = [document.getElementById('taskField'), document.getElementById('quickTaskField')];
  selects.forEach(sel => {
    if (!sel) return;
    sel.innerHTML = '<option value="">No field</option>' + state.fields.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
  });
}

function rerenderAll() {
  updateStats();
  renderFields();
  renderTasks();
  renderUpcomingTasks();
  renderInventory();
  renderFinance();
  populateFieldSelects();
  updateWeather();
}

function addEventListeners() {
  document.querySelectorAll('.tab-link').forEach(btn => {
    btn.addEventListener('click', () => setActiveTab(btn.dataset.tab));
  });

  document.getElementById('btnReload').addEventListener('click', (e) => { e.preventDefault(); location.reload(); });

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('btnInstall').classList.remove('hidden');
  });
  document.getElementById('btnInstall').addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    document.getElementById('btnInstall').classList.add('hidden');
  });

  // Fields
  document.getElementById('fieldForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const f = {
      id: crypto.randomUUID(),
      name: document.getElementById('fieldName').value.trim(),
      crop: document.getElementById('fieldCrop').value.trim(),
      area: Number(document.getElementById('fieldArea').value) || null,
      sowing: document.getElementById('fieldSowing').value || null
    };
    if (!f.name) return;
    state.fields.push(f);
    saveState();
    e.target.reset();
    rerenderAll();
  });
  document.getElementById('fieldsList').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action="delete-field"]');
    if (!btn) return;
    const id = btn.dataset.id;
    state.fields = state.fields.filter(f => f.id !== id);
    state.tasks = state.tasks.map(t => (t.fieldId === id ? { ...t, fieldId: '' } : t));
    saveState();
    rerenderAll();
  });

  // Tasks
  document.getElementById('taskForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const t = {
      id: crypto.randomUUID(),
      title: document.getElementById('taskTitle').value.trim(),
      due: document.getElementById('taskDue').value,
      fieldId: document.getElementById('taskField').value,
      category: document.getElementById('taskCategory').value,
      completed: false
    };
    if (!t.title || !t.due) return;
    state.tasks.push(t);
    saveState();
    e.target.reset();
    rerenderAll();
  });
  document.getElementById('tasksList').addEventListener('click', (e) => {
    const completeBtn = e.target.closest('button[data-action="complete-task"]');
    const deleteBtn = e.target.closest('button[data-action="delete-task"]');
    if (completeBtn) {
      const id = completeBtn.dataset.id;
      const task = state.tasks.find(t => t.id === id);
      if (task) task.completed = true;
      saveState();
      rerenderAll();
    } else if (deleteBtn) {
      const id = deleteBtn.dataset.id;
      state.tasks = state.tasks.filter(t => t.id !== id);
      saveState();
      rerenderAll();
    }
  });

  // Quick add task
  document.getElementById('quickTaskForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const t = {
      id: crypto.randomUUID(),
      title: document.getElementById('quickTaskTitle').value.trim(),
      due: document.getElementById('quickTaskDue').value,
      fieldId: document.getElementById('quickTaskField').value,
      category: 'General',
      completed: false
    };
    if (!t.title || !t.due) return;
    state.tasks.push(t);
    saveState();
    e.target.reset();
    rerenderAll();
  });

  // Inventory
  document.getElementById('inventoryForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const item = {
      id: crypto.randomUUID(),
      name: document.getElementById('invName').value.trim(),
      quantity: Number(document.getElementById('invQty').value) || 0,
      unit: document.getElementById('invUnit').value.trim()
    };
    if (!item.name) return;
    state.inventory.push(item);
    saveState();
    e.target.reset();
    rerenderAll();
  });
  document.getElementById('inventoryList').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action="delete-inv"]');
    if (!btn) return;
    const id = btn.dataset.id;
    state.inventory = state.inventory.filter(i => i.id !== id);
    saveState();
    rerenderAll();
  });

  // Finance
  document.getElementById('financeForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const entry = {
      id: crypto.randomUUID(),
      type: document.getElementById('finType').value,
      amount: Number(document.getElementById('finAmount').value) || 0,
      desc: document.getElementById('finDesc').value.trim(),
      date: document.getElementById('finDate').value
    };
    if (!entry.desc || !entry.date) return;
    state.finances.push(entry);
    saveState();
    e.target.reset();
    rerenderAll();
  });
  document.getElementById('financeTable').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action="delete-fin"]');
    if (!btn) return;
    const id = btn.dataset.id;
    state.finances = state.finances.filter(f => f.id !== id);
    saveState();
    rerenderAll();
  });

  // Settings: location
  document.getElementById('btnSaveLocation').addEventListener('click', () => {
    const name = document.getElementById('locName').value.trim();
    const lat = Number(document.getElementById('locLat').value);
    const lon = Number(document.getElementById('locLon').value);
    state.location = { name, latitude: isFinite(lat) ? lat : null, longitude: isFinite(lon) ? lon : null };
    saveState();
    updateWeather();
  });
  document.getElementById('btnUseMyLocation').addEventListener('click', async () => {
    if (!('geolocation' in navigator)) return;
    navigator.geolocation.getCurrentPosition((pos) => {
      const { latitude, longitude } = pos.coords;
      state.location = { name: 'Current location', latitude, longitude };
      document.getElementById('locName').value = state.location.name;
      document.getElementById('locLat').value = latitude.toFixed(6);
      document.getElementById('locLon').value = longitude.toFixed(6);
      saveState();
      updateWeather();
    });
  });

  // Data export/import/reset
  document.getElementById('btnExport').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'farmhub-data.json';
    a.click();
    URL.revokeObjectURL(url);
  });
  document.getElementById('importFile').addEventListener('change', (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result);
        state = { ...structuredClone(DEFAULT_STATE), ...data };
        saveState();
        rerenderAll();
      } catch {
        alert('Failed to import file');
      }
    };
    reader.readAsText(file);
  });
  document.getElementById('btnReset').addEventListener('click', () => {
    if (!confirm('Reset all local data?')) return;
    state = structuredClone(DEFAULT_STATE);
    saveState();
    rerenderAll();
  });
}

function init() {
  // Initial tab
  setActiveTab('dashboard');

  // Settings fields
  document.getElementById('locName').value = state.location.name || '';
  document.getElementById('locLat').value = state.location.latitude ?? '';
  document.getElementById('locLon').value = state.location.longitude ?? '';

  addEventListeners();
  rerenderAll();
}

window.addEventListener('DOMContentLoaded', init);