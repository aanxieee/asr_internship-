"""
Utility functions for the pricing engine
Helper functions for calculations and common operations
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, Any, Tuple


def load_json_data(filename: str) -> Dict[str, Any]:
    """
    Load JSON data from the data directory
    
    Args:
        filename (str): Name of the JSON file to load
        
    Returns:
        Dict: Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root, then into data directory
    data_path = os.path.join(os.path.dirname(current_dir), 'data', filename)
    
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {data_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {filename}: {str(e)}", "", 0)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    Using the Haversine formula
    
    Args:
        lat1, lon1: Latitude and longitude of first point (in decimal degrees)
        lat2, lon2: Latitude and longitude of second point (in decimal degrees)
        
    Returns:
        float: Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def get_seasonal_factor(departure_date: datetime, market_data: Dict) -> float:
    """
    Get seasonal pricing factor based on departure date
    
    Args:
        departure_date (datetime): Date of departure
        market_data (Dict): Market data containing seasonal factors
        
    Returns:
        float: Seasonal multiplier (e.g., 1.4 for peak season)
    """
    month_name = departure_date.strftime("%B").lower()
    
    seasonal_factors = market_data.get('market_data', {}).get('seasonal_factors', {})
    
    # Check each season
    for season, data in seasonal_factors.items():
        if month_name in data.get('months', []):
            return data.get('demand_multiplier', 1.0)
    
    # Default to regular season if not found
    return 1.0


def calculate_fuel_cost(distance_km: float, fuel_efficiency: float, fuel_price_per_liter: float) -> float:
    """
    Calculate fuel cost for a flight
    
    Args:
        distance_km (float): Flight distance in kilometers
        fuel_efficiency (float): Aircraft fuel consumption (liters per km)
        fuel_price_per_liter (float): Current fuel price per liter
        
    Returns:
        float: Total fuel cost
    """
    fuel_consumed = distance_km * fuel_efficiency
    return fuel_consumed * fuel_price_per_liter


def get_advance_booking_factor(days_in_advance: int) -> float:
    """
    Calculate pricing factor based on how far in advance the booking is made
    
    Args:
        days_in_advance (int): Number of days before departure
        
    Returns:
        float: Pricing multiplier
    """
    if days_in_advance <= 7:
        return 1.4  # Last minute premium
    elif days_in_advance <= 30:
        return 1.1  # Standard pricing
    elif days_in_advance <= 60:
        return 0.9  # Early bird discount
    else:
        return 0.85  # Super early discount


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code (default: INR)
        
    Returns:
        str: Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def validate_airport_code(airport_code: str, airports_data: Dict) -> bool:
    """
    Validate if airport code exists in the system
    
    Args:
        airport_code (str): 3-letter airport code
        airports_data (Dict): Airport data from JSON
        
    Returns:
        bool: True if valid, False otherwise
    """
    airports = airports_data.get('airports', [])
    valid_codes = [airport['code'] for airport in airports]
    return airport_code.upper() in valid_codes


def get_airport_info(airport_code: str, airports_data: Dict) -> Dict:
    """
    Get airport information by code
    
    Args:
        airport_code (str): 3-letter airport code
        airports_data (Dict): Airport data from JSON
        
    Returns:
        Dict: Airport information or empty dict if not found
    """
    airports = airports_data.get('airports', [])
    for airport in airports:
        if airport['code'].upper() == airport_code.upper():
            return airport
    return {}


def calculate_flight_duration(distance_km: float, average_speed_kmh: float = 850) -> int:
    """
    Calculate estimated flight duration
    
    Args:
        distance_km (float): Flight distance in kilometers
        average_speed_kmh (float): Average flight speed (default: 850 km/h)
        
    Returns:
        int: Flight duration in minutes
    """
    hours = distance_km / average_speed_kmh
    # Add 30 minutes for taxi, takeoff, and landing
    total_hours = hours + 0.5
    return int(total_hours * 60)


def get_time_based_factor(departure_time: str) -> float:
    """
    Get pricing factor based on time of day
    
    Args:
        departure_time (str): Time in HH:MM format
        
    Returns:
        float: Time-based pricing multiplier
    """
    hour = int(departure_time.split(':')[0])
    
    # Peak hours (6-9 AM, 6-9 PM) have higher pricing
    if (6 <= hour <= 9) or (18 <= hour <= 21):
        return 1.2
    # Off-peak hours (late night/early morning) have lower pricing
    elif (23 <= hour <= 23) or (0 <= hour <= 5):
        return 0.9
    # Regular hours
    else:
        return 1.0


def calculate_load_factor_adjustment(booked_seats: int, total_capacity: int) -> float:
    """
    Calculate pricing adjustment based on current load factor
    
    Args:
        booked_seats (int): Number of seats already booked
        total_capacity (int): Total seat capacity
        
    Returns:
        float: Load factor pricing multiplier
    """
    if total_capacity == 0:
        return 1.0
        
    load_factor = booked_seats / total_capacity
    
    if load_factor >= 0.9:
        return 1.5  # Very high demand
    elif load_factor >= 0.7:
        return 1.3  # High demand
    elif load_factor >= 0.5:
        return 1.1  # Moderate demand
    else:
        return 0.95  # Low demand, slight discount


def get_day_of_week_factor(departure_date: datetime) -> float:
    """
    Get pricing factor based on day of the week
    
    Args:
        departure_date (datetime): Date of departure
        
    Returns:
        float: Day-of-week pricing multiplier
    """
    day_of_week = departure_date.weekday()  # 0 = Monday, 6 = Sunday
    
    # Friday, Sunday have higher pricing (business travel)
    if day_of_week in [4, 6]:  # Friday, Sunday
        return 1.15
    # Monday, Thursday (business travel return)
    elif day_of_week in [0, 3]:  # Monday, Thursday
        return 1.1
    # Tuesday, Wednesday, Saturday (leisure travel)
    else:
        return 0.95


# ---------------------------------------------------------------------------
# Private / Business Aviation Specific Cost Utilities
# ---------------------------------------------------------------------------

def nearest_mt(mtow_kg: float) -> int:
    """Return billable weight in metric tons rounded to nearest integer (AERA practice).

    Example: 11,600 kg -> 12 MT
    """
    return int(round(mtow_kg / 1000.0))


def parking_billable_hours(raw_hours: float, free_hours: float, buffer_min: int) -> float:
    """Compute billable parking hours after free allowance plus buffer.

    Args:
        raw_hours: Actual on-ground time.
        free_hours: Free parking allowance in hours.
        buffer_min: Additional grace buffer in minutes.
    """
    effective_free = free_hours + (buffer_min / 60.0)
    return max(0.0, raw_hours - effective_free)


def calc_airport_handling(
    airport_cfg: Dict,
    mtow_kg: float,
    parking_hours: float,
    pax_departing: int,
    pax_arriving: int,
) -> Dict:
    """Compute single-airport handling cost components.

    Components: landing + parking + UDF (user dev. fee) + optional ATC/navigation flat.
    Expects airport_cfg keys: landing_per_mt, landing_min, parking_per_mt_hr,
    free_hours, buffer_minutes, udf {depart, arrive}, optional atc_navigation_flat.
    """
    wt_mt = nearest_mt(mtow_kg)

    # Landing fee (max of per-MT calc vs minimum)
    landing_per_mt = float(airport_cfg["landing_per_mt"])
    landing_min = float(airport_cfg["landing_min"])
    landing_raw = wt_mt * landing_per_mt
    landing_fee = max(landing_raw, landing_min)

    # Parking fee (after free + buffer)
    per_mt_hr = float(airport_cfg["parking_per_mt_hr"])
    free_hours = float(airport_cfg["free_hours"])
    buffer_minutes = int(airport_cfg["buffer_minutes"])
    billable_hrs = parking_billable_hours(parking_hours, free_hours, buffer_minutes)
    parking_fee = wt_mt * per_mt_hr * billable_hrs

    # UDF (departure + arrival passengers)
    udf_cfg = airport_cfg.get("udf", {"depart": 0, "arrive": 0})
    udf_fee = pax_departing * float(udf_cfg.get("depart", 0)) + pax_arriving * float(udf_cfg.get("arrive", 0))

    # Optional ATC / navigation flat fee
    atc_fee = float(airport_cfg.get("atc_navigation_flat", 0))

    total_airport = landing_fee + parking_fee + udf_fee + atc_fee
    return {
        "weight_mt_billed": wt_mt,
        "landing": landing_fee,
        "parking": parking_fee,
        "udf": udf_fee,
        "atc": atc_fee,
        "total": total_airport,
    }