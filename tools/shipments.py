MOCK_SHIPMENTS = {
    "123": {"status": "Out for delivery", "city": "Jeddah", "driver": "Ahmed"},
    "456": {"status": "Delayed 3 hours", "city": "Riyadh", "driver": "Saad"},
    "789": {"status": "Delivered", "city": "Dammam", "driver": "Khalid"},
}

def get_shipment_status(tracking_number: str):
    return MOCK_SHIPMENTS.get(tracking_number, {"error": "Shipment not found"})
