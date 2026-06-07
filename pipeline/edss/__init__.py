"""
Environmental Decision Support System (EDSS).

Clean architecture layout:
  - domain: business rules and constants
  - infrastructure: data access via existing pipeline modules
  - application: use cases, policy engine, presentation
"""

from .application.service import generate_decision_support

__all__ = ["generate_decision_support"]
