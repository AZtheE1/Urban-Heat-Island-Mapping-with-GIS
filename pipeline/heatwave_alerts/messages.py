"""Heatwave alert message generation."""

from .thresholds import classify_alert_level

MESSAGE_TEMPLATES = {
    "Warning": (
        "Heatwave Warning: Temperature reached {temperature}°C{location_suffix}. "
        "Limit prolonged outdoor exposure, seek shade, and stay hydrated."
    ),
    "Severe": (
        "Severe Heat Alert: Temperature reached {temperature}°C{location_suffix}. "
        "Avoid non-essential outdoor activity. Vulnerable populations should remain indoors."
    ),
    "Extreme": (
        "Extreme Heat Emergency: Temperature exceeded {temperature}°C{location_suffix}. "
        "Immediate cooling measures required. Follow local emergency heat advisories."
    ),
}


def build_alert_message(temperature, level=None, location_name=None):
    """Generate a human-readable alert message for the given temperature."""
    alert_level = level or classify_alert_level(temperature)
    if alert_level not in MESSAGE_TEMPLATES:
        return None

    location_suffix = f" at {location_name}" if location_name else ""
    return MESSAGE_TEMPLATES[alert_level].format(
        temperature=round(float(temperature), 2),
        location_suffix=location_suffix,
    )
