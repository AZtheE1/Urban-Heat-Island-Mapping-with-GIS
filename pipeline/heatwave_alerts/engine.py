"""Heatwave alert evaluation engine."""

from datetime import datetime, timezone

from .data_loader import (
    load_historical_temperature_observations,
    load_regional_temperature_observations,
)
from .messages import build_alert_message
from .notifiers import NotificationDispatcher, MockTwilioNotifier
from .thresholds import LEVEL_NORMAL, classify_alert_level, threshold_reference

LEVEL_RANK = {
    LEVEL_NORMAL: 0,
    "Warning": 1,
    "Severe": 2,
    "Extreme": 3,
}


def _utc_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_alert(observation, region=None):
    """Convert a temperature observation into an alert payload when thresholds are exceeded."""
    temperature = observation["temperature"]
    level = classify_alert_level(temperature)
    if level == LEVEL_NORMAL:
        return None

    location_name = observation.get("locationName")
    return {
        "id": f"{region or 'unknown'}-{location_name or 'site'}-{round(temperature, 1)}-{observation.get('timestamp', '')}",
        "level": level,
        "temperature": round(temperature, 2),
        "message": build_alert_message(
            temperature,
            level=level,
            location_name=location_name,
        ),
        "timestamp": observation.get("timestamp") or _utc_timestamp(),
        "locationName": location_name,
        "lat": observation.get("lat"),
        "lng": observation.get("lng"),
        "source": observation.get("source", "regional_ground_data"),
        "region": region,
    }


def evaluate_heatwave_alerts(
    base_dir,
    region,
    df,
    include_historical=False,
    dispatch_notifications=True,
    notifiers=None,
):
    """
    Monitor temperature observations and generate heatwave alerts.

    Returns active alerts sorted by severity (highest first), then temperature.
    """
    fallback_timestamp = _utc_timestamp()
    observations = load_regional_temperature_observations(df, fallback_timestamp)

    if include_historical:
        observations.extend(
            load_historical_temperature_observations(base_dir, fallback_timestamp)
        )

    alerts = []
    for observation in observations:
        alert = _build_alert(observation, region=region)
        if alert is not None:
            alerts.append(alert)

    alerts.sort(
        key=lambda item: (LEVEL_RANK.get(item["level"], 0), item["temperature"]),
        reverse=True,
    )

    if dispatch_notifications and alerts:
        if notifiers is None:
            notifiers = [MockTwilioNotifier()]
        dispatcher = NotificationDispatcher(notifiers=notifiers)
        dispatcher.dispatch(alerts)

    highest_level = alerts[0]["level"] if alerts else LEVEL_NORMAL
    return {
        "region": region,
        "activeAlertCount": len(alerts),
        "highestLevel": highest_level,
        "thresholds": threshold_reference(),
        "alerts": alerts,
    }
