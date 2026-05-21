import os

# Qdrant configuration
# Use local file-based storage by default (no server needed)
# Set QDRANT_URL env var to use a remote Qdrant server instead
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "qdrant_store")
QDRANT_COLLECTION = "the_book"

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Categorization rules
CATEGORIES = [
    "medical_emergency",
    "security_threat",
    "mechanical_failure",
    "collision",
    "hazardous_material"
]

CATEGORY_TO_TOOL = {
    "medical_emergency": "call_emergency_services",
    "security_threat": "call_emergency_services",
    "mechanical_failure": "page_field_supervisor",
    "collision": "trigger_regulatory_hold",
    "hazardous_material": "trigger_regulatory_hold"
}

LEGAL_FLAGS = {
    "no_fault_admission": "Do not discuss liability or admit fault on scene.",
    "preserve_evidence": "Do not move the coach unless directed by a supervisor or police.",
    "passenger_info": "Distribute courtesy cards to all passengers and request they fill them out."
}

CATEGORY_LEGAL_FLAGS = {
    "collision": ["no_fault_admission", "preserve_evidence", "passenger_info"],
    "medical_emergency": ["preserve_evidence"],
    "hazardous_material": ["preserve_evidence"],
    "security_threat": ["preserve_evidence"]
}

# Few-shot examples for panic variance
FEW_SHOT_EXAMPLES = """
Example 1:
Input: "throwing green fluid everywhere, smells sweet"
Category: hazardous_material
Reasoning: Green sweet-smelling fluid is engine coolant. This is a hazardous leak.

Example 2:
Input: "guy just collapsed in the back, not moving"
Category: medical_emergency
Reasoning: Passenger collapse indicates a medical emergency requiring immediate attention.

Example 3:
Input: "someone rear ended me hard at the stop light"
Category: collision
Reasoning: "Rear ended" directly indicates a vehicle collision.
"""
