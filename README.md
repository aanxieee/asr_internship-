# ASR Aviation – Aircraft Pricing Analytics (Internship Project)

This repository contains the **pricing analytics engine** I built during my **ASR Aviation – Project Intern** role (Aug 2025 – Nov 2025, Jaipur, On-site). It is a production-style Django REST app that exposes an API for estimating end-to-end pricing for private aircraft charters.

## Internship Context – ASR Aviation

**Role:** Project Intern  
**Company:** ASR Aviation  
**Duration:** Aug 2025 – Nov 2025 (4 months)  
**Location:** Jaipur (On-site)-BTH

**Key outcomes:**
- Built a pricing analytics model for 30+ aircraft using structured inputs and cost breakdowns.
- Supported decision-making by translating operational data into pricing insights.
- Automated workflows and APIs to reduce manual work and improve turnaround time.
- Worked cross-functionally to align product, operations, and data requirements.
- Designed the API so it can plug into workflow tools (n8n / Make) and custom back-office systems.

This repo is the pricing component that powered those outcomes.

---

## What This Project Does

- Implements a **pricing engine** that combines:
  - Aircraft hourly rates.
  - Airport–specific handling and regulatory fees.
  - Operating costs (crew, insurance, maintenance).
  - Market demand / seasonal adjustments.
  - Taxes and platform fees.
- Exposes a **single REST endpoint** to calculate a detailed price estimate for a sector (origin → destination).
- Encodes **aviation-specific billing logic** such as MTOW-based landing fees, parking grace hours, UDFs, and ATC/navigation charges.
- Structured to be integrated into a larger backend or workflow automation (n8n / Make / custom ops dashboards).

---

## Tech Stack

- **Language:** Python
- **Framework:** Django + Django REST Framework (DRF)
- **Pricing engine:** Pure Python services with JSON-configured data
- **Data sources:**
  - `aircrafts.json` – fleet, hourly rates, capacities
  - `pricing_airports.json` – airport tariffs and handling rules
  - `ops.json` – per-hour operational cost parameters
  - `market.json` – demand and market adjustment factors

> Note: In the original ASR Aviation system this app lived inside a larger backend. Here it is extracted as a focused pricing module for demonstration.

---

## Project Structure

At a glance:

- `apps.py` – Django app configuration (`pricing`).
- `serializers.py` – Input validation for the pricing API.
- `views.py` – REST API endpoint using Django REST Framework.
- `services.py` – Core pricing service that combines aircraft, airport, ops, and market data.
- `utils.py` – Shared calculation utilities (distance, seasonality, time-of-day, handling tariffs, etc.).
- `urls.py` – Routes the `/estimate/` endpoint.
- `migrations/` – Django migration package (empty in this extracted module).

The app is designed as a **drop-in Django app** called `pricing` that can be plugged into any Django project.

---

## Pricing Flow – High Level

1. **Frontend / workflow tool** calls the API with route + aircraft + passenger inputs.
2. `PricingInputSerializer` in `serializers.py` validates and normalizes the payload.
3. `get_price_estimate` in `views.py` maps frontend keys and calls `pricing_service`.
4. `pricing_service` in `services.py`:
   - Looks up the selected aircraft in `AIRCRAFTS`.
   - Computes flight-hour based pricing from `hourly_rate`.
   - Adds operational costs per flight hour from `OPS`.
   - Builds a list of stops (origin + destination) and calls `calc_airport_handling` for each.
   - Applies a market/demand factor from `MARKET`.
   - Adds GST and a platform fee to output a final price.
5. The API returns a **structured pricing breakdown** JSON response suitable for dashboards or workflow automation.

---

## API Design

### Endpoint

- **Method:** `POST`
- **Path:** `/estimate/`

> In a full Django project, this would usually be included under a project-level prefix, e.g. `/api/pricing/estimate/`.

### Request Payload

The view is flexible to match frontend naming. It accepts:

- `from` / `to` – frontend field names (e.g., form inputs). These are internally mapped to `origin` / `destination`.
- `origin` – origin airport code or identifier.
- `destination` – destination airport code or identifier.
- `mapped_from` – canonical origin airport key used in price config (e.g., `DEL`, `BOM`).
- `mapped_to` – canonical destination airport key used in price config.
- `aircraft_id` – integer ID of the aircraft from `aircrafts.json`.
- `flight_hours` – expected flight time (one way) in hours.
- `passengers` – number of passengers.

Example (frontend style):

```json
{
  "from": "DEL",
  "to": "BOM",
  "mapped_from": "DEL",
  "mapped_to": "BOM",
  "aircraft_id": 3,
  "flight_hours": 2.5,
  "passengers": 6
}
```

### Response Payload

For security and confidentiality reasons (**ASR Aviation privacy, terms and conditions**), this public repo does **not** expose real pricing numbers or exact commercial breakdowns.

Instead of numeric examples, the response can be understood as a structured object with fields such as:

- `aircraft_model`
- `hourly_rate`
- `flight_hours`
- `base_price`
- `ops_cost`
- `handling_total`
- `handling_breakdown` (per-airport components)
- `subtotal_after_market`
- `platform_fee`
- `gst_18_percent`
- `final_price`

The actual values and formulas used in ASR Aviation production environments are proprietary and have been intentionally omitted here. This structure still makes it **easy to explain pricing** to non-technical stakeholders and to power internal tools (dashboards, workflow automations) without leaking sensitive tariff information.

---

## Key Components

### 1. Serializer – `PricingInputSerializer`

File: `serializers.py`

- Ensures all required fields are present.
- Validates types (e.g., `aircraft_id` as integer, `flight_hours` as float).
- Normalizes incoming data before the service layer sees it.

### 2. REST View – `get_price_estimate`

File: `views.py`

- Decorated with DRF’s `@api_view(["POST"])` and `AllowAny` permission for easy integration.
- Accepts both `from` / `to` (frontend style) and `origin` / `destination` keys.
- Validates payload via `PricingInputSerializer`.
- Calls `pricing_service` and returns:
  - `200 OK` with JSON breakdown on success.
  - `400 Bad Request` with validation errors.
  - `500 Internal Server Error` with a simple error string for unexpected failures.

### 3. Pricing Service – `pricing_service`

File: `services.py`

- Loads JSON configuration for aircraft, airports, ops, and market.
- Calculates:
  - `base_price` from aircraft hourly rate × `flight_hours`.
  - `ops_cost` from crew/insurance/maintenance per hour × `flight_hours`.
  - `handling_total` by iterating over stops and using `calc_airport_handling`.
  - `subtotal_after_market` by applying a multiplier (e.g., demand factor).
  - `gst_18_percent` and a `platform_fee`.
  - `final_price` as the client-facing number.

### 4. Aviation Utilities – `utils.py`

Selected helpers:

- `calculate_distance` – Haversine distance between two coordinates.
- `get_seasonal_factor`, `get_day_of_week_factor`, `get_time_based_factor` – demand / seasonality adjustments.
- `calculate_load_factor_adjustment` – pricing adjustment based on seat load.
- `calc_airport_handling` – detailed airport handling cost (landing, parking, UDF, ATC) using real-world-style rules.

These utilities enable richer pricing logic as the product matures.

---

## How to Run Locally

This repo contains the **Django app only**. To run it end-to-end:

1. **Create a Django project (if you don’t already have one):**
   ```bash
   django-admin startproject backend
   cd backend
   ```

2. **Add this `pricing` app into your project** (copy the `pricing` directory into the project root next to `manage.py`).

3. **Install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   pip install django djangorestframework
   ```

4. **Enable the app & DRF** in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'pricing',
   ]
   ```

5. **Include the pricing URLs** in your project’s `urls.py`:
   ```python
   from django.urls import path, include

   urlpatterns = [
       # ...
       path('pricing/', include('pricing.urls')),
   ]
   ```

6. **Add the required JSON data files** under a `data/` directory at the same level as your Django project root, matching the filenames expected in `services.py` and `utils.py` (e.g., `aircrafts.json`, `pricing_airports.json`, `ops.json`, `market.json`).

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

8. **Test the endpoint:**
   ```bash
   curl -X POST http://127.0.0.1:8000/pricing/estimate/ \
     -H "Content-Type: application/json" \
     -d '{
       "from": "DEL",
       "to": "BOM",
       "mapped_from": "DEL",
       "mapped_to": "BOM",
       "aircraft_id": 3,
       "flight_hours": 2.5,
       "passengers": 6
     }'
   ```

---

## How This Demonstrates Internship Impact

- **Realistic domain modeling:** Encodes aircraft, airport, and operations concepts in a way that matches how aviation pricing teams think.
- **Decision support:** Returns granular breakdowns (base, ops, handling, tax, platform) to help non-technical teams understand and adjust pricing.
- **Automation-ready:** Stateless HTTP API that can be triggered from back-office tools, workflow automation (n8n / Make), or partner integrations.
- **Extensible:** New aircraft, airports, or pricing rules can be added via JSON configs and helper utilities without rewriting the core logic.

This project is intended as a **portfolio / proof-of-work** artifact showcasing my contribution to pricing analytics and workflow automation at ASR Aviation.
# ASR Aviation – Aircraft Pricing Analytics (Internship Project)

This repository contains the **pricing analytics engine** I built during my **ASR Aviation – Project Intern** role (Aug 2025 – Nov 2025, Jaipur, On-site). It is a production-style Django REST app that exposes an API for estimating end-to-end pricing for private aircraft charters.

## Internship Context – ASR Aviation

**Role:** Project Intern  
**Company:** ASR Aviation  
**Duration:** Aug 2025 – Nov 2025 (4 months)  
**Location:** Jaipur (On-site)-BTH

**Key outcomes:**
- Built a pricing analytics model for 30+ aircraft using structured inputs and cost breakdowns.
- Supported decision-making by translating operational data into pricing insights.
- Automated workflows and APIs to reduce manual work and improve turnaround time.
- Worked cross-functionally to align product, operations, and data requirements.
- Designed the API so it can plug into workflow tools (n8n / Make) and custom back-office systems.

This repo is the pricing component that powered those outcomes.

---

## What This Project Does

- Implements a **pricing engine** that combines:
  - Aircraft hourly rates.
  - Airport–specific handling and regulatory fees.
  - Operating costs (crew, insurance, maintenance).
  - Market demand / seasonal adjustments.
  - Taxes and platform fees.
- Exposes a **single REST endpoint** to calculate a detailed price estimate for a sector (origin → destination).
- Encodes **aviation-specific billing logic** such as MTOW-based landing fees, parking grace hours, UDFs, and ATC/navigation charges.
- Structured to be integrated into a larger backend or workflow automation (n8n / Make / custom ops dashboards).

---

## Tech Stack

- **Language:** Python
- **Framework:** Django + Django REST Framework (DRF)
- **Pricing engine:** Pure Python services with JSON-configured data
- **Data sources:**
  - `aircrafts.json` – fleet, hourly rates, capacities
  - `pricing_airports.json` – airport tariffs and handling rules
  - `ops.json` – per-hour operational cost parameters
  - `market.json` – demand and market adjustment factors

> Note: In the original ASR Aviation system this app lived inside a larger backend. Here it is extracted as a focused pricing module for demonstration.

---

## Project Structure

At a glance:

- `apps.py` – Django app configuration (`pricing`).
- `serializers.py` – Input validation for the pricing API.
- `views.py` – REST API endpoint using Django REST Framework.
- `services.py` – Core pricing service that combines aircraft, airport, ops, and market data.
- `utils.py` – Shared calculation utilities (distance, seasonality, time-of-day, handling tariffs, etc.).
- `urls.py` – Routes the `/estimate/` endpoint.
- `migrations/` – Django migration package (empty in this extracted module).

The app is designed as a **drop-in Django app** called `pricing` that can be plugged into any Django project.

---

## Pricing Flow – High Level

1. **Frontend / workflow tool** calls the API with route + aircraft + passenger inputs.
2. `PricingInputSerializer` in `serializers.py` validates and normalizes the payload.
3. `get_price_estimate` in `views.py` maps frontend keys and calls `pricing_service`.
4. `pricing_service` in `services.py`:
   - Looks up the selected aircraft in `AIRCRAFTS`.
   - Computes flight-hour based pricing from `hourly_rate`.
   - Adds operational costs per flight hour from `OPS`.
   - Builds a list of stops (origin + destination) and calls `calc_airport_handling` for each.
   - Applies a market/demand factor from `MARKET`.
   - Adds GST and a platform fee to output a final price.
5. The API returns a **structured pricing breakdown** JSON response suitable for dashboards or workflow automation.

---

## API Design

### Endpoint

- **Method:** `POST`
- **Path:** `/estimate/`

> In a full Django project, this would usually be included under a project-level prefix, e.g. `/api/pricing/estimate/`.

### Request Payload

The view is flexible to match frontend naming. It accepts:

- `from` / `to` – frontend field names (e.g., form inputs). These are internally mapped to `origin` / `destination`.
- `origin` – origin airport code or identifier.
- `destination` – destination airport code or identifier.
- `mapped_from` – canonical origin airport key used in price config (e.g., `DEL`, `BOM`).
- `mapped_to` – canonical destination airport key used in price config.
- `aircraft_id` – integer ID of the aircraft from `aircrafts.json`.
- `flight_hours` – expected flight time (one way) in hours.
- `passengers` – number of passengers.

Example (frontend style):

```json
{
  "from": "DEL",
  "to": "BOM",
  "mapped_from": "DEL",
  "mapped_to": "BOM",
  "aircraft_id": 3,
  "flight_hours": 2.5,
  "passengers": 6
}
```

### Response Payload

For security and confidentiality reasons (**ASR Aviation privacy, terms and conditions**), this public repo does **not** expose real pricing numbers or exact commercial breakdowns.

Instead of numeric examples, the response can be understood as a structured object with fields such as:

- `aircraft_model`
- `hourly_rate`
- `flight_hours`
- `base_price`
- `ops_cost`
- `handling_total`
- `handling_breakdown` (per-airport components)
- `subtotal_after_market`
- `platform_fee`
- `gst_18_percent`
- `final_price`

The actual values and formulas used in ASR Aviation production environments are proprietary and have been intentionally omitted here. This structure still makes it **easy to explain pricing** to non-technical stakeholders and to power internal tools (dashboards, workflow automations) without leaking sensitive tariff information.

---

## Key Components

### 1. Serializer – `PricingInputSerializer`

File: `serializers.py`

- Ensures all required fields are present.
- Validates types (e.g., `aircraft_id` as integer, `flight_hours` as float).
- Normalizes incoming data before the service layer sees it.

### 2. REST View – `get_price_estimate`

File: `views.py`

- Decorated with DRF’s `@api_view(["POST"])` and `AllowAny` permission for easy integration.
- Accepts both `from` / `to` (frontend style) and `origin` / `destination` keys.
- Validates payload via `PricingInputSerializer`.
- Calls `pricing_service` and returns:
  - `200 OK` with JSON breakdown on success.
  - `400 Bad Request` with validation errors.
  - `500 Internal Server Error` with a simple error string for unexpected failures.

### 3. Pricing Service – `pricing_service`

File: `services.py`

- Loads JSON configuration for aircraft, airports, ops, and market.
- Calculates:
  - `base_price` from aircraft hourly rate × `flight_hours`.
  - `ops_cost` from crew/insurance/maintenance per hour × `flight_hours`.
  - `handling_total` by iterating over stops and using `calc_airport_handling`.
  - `subtotal_after_market` by applying a multiplier (e.g., demand factor).
  - `gst_18_percent` and a `platform_fee`.
  - `final_price` as the client-facing number.

### 4. Aviation Utilities – `utils.py`

Selected helpers:

- `calculate_distance` – Haversine distance between two coordinates.
- `get_seasonal_factor`, `get_day_of_week_factor`, `get_time_based_factor` – demand / seasonality adjustments.
- `calculate_load_factor_adjustment` – pricing adjustment based on seat load.
- `calc_airport_handling` – detailed airport handling cost (landing, parking, UDF, ATC) using real-world-style rules.

These utilities enable richer pricing logic as the product matures.

---

## How to Run Locally

This repo contains the **Django app only**. To run it end-to-end:

1. **Create a Django project (if you don’t already have one):**
   ```bash
   django-admin startproject backend
   cd backend
   ```

2. **Add this `pricing` app into your project** (copy the `pricing` directory into the project root next to `manage.py`).

3. **Install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   pip install django djangorestframework
   ```

4. **Enable the app & DRF** in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'pricing',
   ]
   ```

5. **Include the pricing URLs** in your project’s `urls.py`:
   ```python
   from django.urls import path, include

   urlpatterns = [
       # ...
       path('pricing/', include('pricing.urls')),
   ]
   ```

6. **Add the required JSON data files** under a `data/` directory at the same level as your Django project root, matching the filenames expected in `services.py` and `utils.py` (e.g., `aircrafts.json`, `pricing_airports.json`, `ops.json`, `market.json`).

7. **Run the server:**
   ```bash
   python manage.py runserver
   ```

8. **Test the endpoint:**
   ```bash
   curl -X POST http://127.0.0.1:8000/pricing/estimate/ \
     -H "Content-Type: application/json" \
     -d '{
       "from": "DEL",
       "to": "BOM",
       "mapped_from": "DEL",
       "mapped_to": "BOM",
       "aircraft_id": 3,
       "flight_hours": 2.5,
       "passengers": 6
     }'
   ```

---

## How This Demonstrates Internship Impact

- **Realistic domain modeling:** Encodes aircraft, airport, and operations concepts in a way that matches how aviation pricing teams think.
- **Decision support:** Returns granular breakdowns (base, ops, handling, tax, platform) to help non-technical teams understand and adjust pricing.
- **Automation-ready:** Stateless HTTP API that can be triggered from back-office tools, workflow automation (n8n / Make), or partner integrations.
- **Extensible:** New aircraft, airports, or pricing rules can be added via JSON configs and helper utilities without rewriting the core logic.

This project is intended as a **portfolio / proof-of-work** artifact showcasing my contribution to pricing analytics and workflow automation at ASR Aviation.
