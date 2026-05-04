# RetroBuild

A full-stack web application that helps League of Legends players reach their key item "power spikes" faster by computing the most gold-efficient purchase path from a player's current inventory and gold to a chosen target item. The League item shop is modeled as a **directed weighted graph** (items and their upgrade recipes); a NetworkX shortest-path algorithm picks the cheapest reachable target item for the player's current state and produces a step-by-step purchase recommendation.

## Tech stack

| Layer | Technology |
|-------|------------|
| Database | MySQL 8 |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic |
| Algorithm | NetworkX  |
| Frontend | Angular 19 |

## Features

- **Item Browser** - search and filter all 197 items pulled from Riot's Data Dragon CDN, view recipe components and what an item builds into.
- **Build Plans** - create reusable named lists of target items per champion/playstyle.
- **Run Analysis** - pick a plan, enter current gold and inventory, get the optimal next-purchase path with per-step costs.
- **History** - every analysis run is persisted; review past runs, expand for full path detail, filter by plan, delete.

## Architecture overview

```
Angular UI (port 4300)  ──HTTP/JSON──►  FastAPI (port 8000)  ──SQL──►  MySQL (port 3306)
```

---

## Prerequisites

Before setup you need:

- **Python 3.12+** - for the FastAPI backend
- **Node.js 22+** with **npm 10+** - for the Angular frontend
- **MySQL 8+** - server running locally
- **Angular CLI 19+** - install with `npm install -g @angular/cli@19`


---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Trexxin/RetroBuild.git
cd RetroBuild
```

### 2. Database setup

Start MySQL and create the database + a dedicated app user:

```bash
sudo service mysql start

sudo mysql <<'EOF'
CREATE DATABASE IF NOT EXISTS retrobuild;
CREATE USER IF NOT EXISTS 'retrobuild'@'localhost' IDENTIFIED BY 'retrobuild';
GRANT ALL PRIVILEGES ON retrobuild.* TO 'retrobuild'@'localhost';
FLUSH PRIVILEGES;
EOF
```

The schema itself is created automatically by SQLAlchemy on the first backend startup 

### 3. Backend setup

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

### 4. Seed the item data

The seed script fetches the full item catalog from Riot's public Data Dragon CDN, filters to Summoner's Rift purchasable items, and inserts the items + recipe junction rows.

From the `backend/` directory with the venv active:

```bash
python -m app.seed.seed_items
```

### 5. Frontend setup

```bash
cd ../frontend
npm install
```

---

## Running the app

Open two terminals.

**Terminal 1 - backend (FastAPI on port 8000):**

```bash
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API docs (Swagger UI) are available at <http://localhost:8000/docs>.

**Terminal 2 - frontend (Angular on port 4300):**

```bash
cd frontend
ng serve --host 0.0.0.0 --port 4300
```

The app is now at <http://localhost:4300>.


---

## Database schema

Seven tables, automatically created by SQLAlchemy at first startup.

| Table | PK | Notable columns / constraints |
|-------|-----|---|
| `items` | `item_id` (Riot's numeric ID, not auto-increment) | `name`, `total_cost`, `purchasable`, `version_tag`, `icon_url` |
| `item_recipe` | composite `(parent_item_id, component_item_id)` | `qty` for items requiring multiple of the same component |
| `build_plans` | `plan_id` (auto-increment) | `name`, `notes`, `user_id` (reserved for auth), `created_at` |
| `build_plan_targets` | composite `(plan_id, target_item_id)` | cascade delete with parent plan |
| `analysis_runs` | `run_id` (auto-increment) | FK to `build_plans`, `current_gold` (`CHECK >= 0`), `created_at` |
| `run_inventory_items` | composite `(run_id, slot_index)` | `slot_index CHECK 0..5`, FK to `items`, cascade with run |
| `run_path_steps` | composite `(run_id, step_num)` | FK to `items`, `step_cost`, cascade with run |

---

## REST API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/items` | List items. Query params: `search`, `min_cost`, `max_cost`. |
| `GET` | `/api/items/{item_id}` | Item detail with components + builds_into. |
| `GET` | `/api/plans` | List all build plans (summaries with target counts). |
| `POST` | `/api/plans` | Create plan. Body: `{name, notes, target_item_ids}`. |
| `GET` | `/api/plans/{plan_id}` | Plan detail with target items. |
| `PUT` | `/api/plans/{plan_id}` | Update plan name/notes/targets. |
| `DELETE` | `/api/plans/{plan_id}` | Delete plan (cascades to targets). |
| `POST` | `/api/analysis/run` | Run an analysis and persist the result. |
| `GET` | `/api/analysis/history` | List past runs. Optional `?plan_id=` filter. |
| `GET` | `/api/analysis/history/{run_id}` | Full detail of a past run. |
| `DELETE` | `/api/analysis/history/{run_id}` | Delete a run (cascades inventory + path). |

Full interactive docs at <http://localhost:8000/docs> when the backend is running.
