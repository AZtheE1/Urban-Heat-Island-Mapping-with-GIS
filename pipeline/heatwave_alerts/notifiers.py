"""Notification dispatch layer for future SMS, email, and push integrations."""

from abc import ABC, abstractmethod


class BaseAlertNotifier(ABC):
    """Interface for external alert delivery channels."""

    name = "base"

    @abstractmethod
    def notify(self, alert):
        """Deliver a single alert payload to an external channel."""


class LogAlertNotifier(BaseAlertNotifier):
    """Development notifier that records alerts without sending externally."""

    name = "log"

    def notify(self, alert):
        print(
            f"[HEATWAVE ALERT:{alert.get('level')}] "
            f"{alert.get('temperature')}°C — {alert.get('message')}"
        )

class MockTwilioNotifier(BaseAlertNotifier):
    """Mocks the Twilio API integration as requested for the hackathon."""

    name = "mock_twilio"

    def notify(self, alert):
        print("\n" + "="*50)
        print("📲 MOCK TWILIO SMS DISPATCHED")
        print(f"TO: [+1234567890 (Admin)]")
        print(f"BODY: URGENT: Heatwave Alert! {alert.get('temperature')}°C. {alert.get('message')}")
        print("="*50 + "\n")


class NotificationDispatcher:
    """Fan-out dispatcher for pluggable notification backends."""

    def __init__(self, notifiers=None):
        self.notifiers = list(notifiers or [])

    def register(self, notifier):
        self.notifiers.append(notifier)

    def dispatch(self, alerts):
        """Send alerts through all registered notifiers."""
        delivered = []
        for alert in alerts:
            for notifier in self.notifiers:
                notifier.notify(alert)
            delivered.append(alert)
        return delivered
