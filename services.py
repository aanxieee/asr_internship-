"""Core pricing service for aircraft charter estimates.

Note: Specific commercial tariffs, coefficients, and JSON configurations
used inside ASR Aviation production systems are **confidential** and are
not exposed in this public repository. This module is provided only as a
structural / logical proof-of-work implementation, in line with
ASR Aviation privacy, terms and conditions.
"""

import json
from pathlib import Path
from .utils import calc_airport_handling

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/django_core/
DATA_DIR = BASE_DIR.parent / "data"  # backend/data/


def _load_json(name):
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load JSON configs
AIRCRAFTS = _load_json("aircrafts.json")
AIRPORTS = _load_json("pricing_airports.json")
OPS = _load_json("ops.json")
MARKET = _load_json("market.json")


def pricing_service(valid_data):
    mapped_from = valid_data["mapped_from"]
    mapped_to = valid_data["mapped_to"]
    aircraft_id = valid_data["aircraft_id"]
    flight_hours = valid_data["flight_hours"]
    passengers = valid_data["passengers"]

    # Create stops based on inputs (origin + destination)
    stops = [
        {
            "airport": mapped_from,
            "mtow_kg": 0,  # if needed later, fill from aircraft json
            "parking_hours": 0,
            "pax_departing": passengers,
            "pax_arriving": 0
        },
        {
            "airport": mapped_to,
            "mtow_kg": 0,
            "parking_hours": 0,
            "pax_departing": 0,
            "pax_arriving": passengers
        }
    ]

    # Aircraft lookup
    aircraft = next((a for a in AIRCRAFTS if a["id"] == aircraft_id), None)
    if aircraft is None:
        raise ValueError(f"Unknown aircraft_id: {aircraft_id}")

    hourly_rate = float(aircraft["hourly_rate"])
    base_price = flight_hours * hourly_rate

    ops_per_hr = float(
        OPS["crew_cost_per_hr"]
        + OPS["insurance_per_hr"]
        + OPS["maintenance_per_hr"]
    )
    ops_cost = flight_hours * ops_per_hr

    handling_breakdown = []
    handling_total = 0.0

    for s in stops:
        key = s["airport"].upper()
        ap_cfg = AIRPORTS.get(key)

        if not ap_cfg:
            raise ValueError(f"No tariff configured for airport: {s['airport']}")

        h = calc_airport_handling(
            ap_cfg,
            s["mtow_kg"],
            s["parking_hours"],
            s["pax_departing"],
            s["pax_arriving"]
        )

        handling_breakdown.append({
            "airport": s["airport"],
            **h
        })
        handling_total += h["total"]

    subtotal = base_price + ops_cost + handling_total
    subtotal *= float(MARKET.get("demand_factor", 1.0))

    gst = subtotal * 0.18
    platform_fee = 15000.0
    final = subtotal + gst + platform_fee

    return {
        
            "aircraft_model": aircraft["model"],
            "hourly_rate": hourly_rate,
            "flight_hours": flight_hours,
            "base_price": base_price,
            "ops_cost": ops_cost,
            "handling_total": handling_total,
            "handling_breakdown": handling_breakdown,
            "subtotal_after_market": subtotal,
            "platform_fee": platform_fee,
            "gst_18_percent": gst,
            "final_price": final
        
    }
