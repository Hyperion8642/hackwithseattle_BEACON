import logging
from typing import List
from .config import LEGAL_FLAGS, CATEGORY_LEGAL_FLAGS

# Setup basic audit logging
logging.basicConfig(
    filename='legal_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_legal_reminders(category: str) -> List[str]:
    """
    Returns a list of mandatory legal reminders for a given incident category.
    """
    flags = CATEGORY_LEGAL_FLAGS.get(category, [])
    reminders = [LEGAL_FLAGS[flag] for flag in flags if flag in LEGAL_FLAGS]
    return reminders

def apply_legal_compliance(category: str, operator_id: str = "UNKNOWN") -> List[str]:
    """
    Retrieves legal reminders and logs that they were applied for audit purposes.
    """
    reminders = get_legal_reminders(category)
    if reminders:
        # Write to audit log proving reminders were triggered
        logging.info(f"LEGAL MANDATE APPLIED: Operator {operator_id} | Category {category} | Reminders: {len(reminders)}")
    return reminders
