import os
import requests
from typing import Dict, Any, Optional, List

class TrackingMoreClient:
    def __init__(self):
        self.api_key = os.getenv("TRACKINGMORE_API_KEY")
        if not self.api_key:
            raise ValueError("TRACKINGMORE_API_KEY environment variable is not set")
        
        self.base_url = "https://api.trackingmore.com/v4"
        self.headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": self.api_key
        }

    def get_courier_list(self) -> List[Dict[str, str]]:
        """Get list of available courier services"""
        endpoint = f"{self.base_url}/couriers"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    def create_tracking(self, tracking_number: str, courier_code: Optional[str] = None) -> Dict[str, Any]:
        """Create a new tracking"""
        endpoint = f"{self.base_url}/trackings/create"
        data = {
            "tracking_number": tracking_number,
            "courier_code": courier_code
        }
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_tracking_info(self, tracking_number: str) -> Dict[str, Any]:
        """Get tracking information for a specific tracking number"""
        endpoint = f"{self.base_url}/trackings/get"
        params = {"tracking_numbers": tracking_number}
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def format_tracking_response(self, tracking_data: Dict[str, Any]) -> str:
        """Format tracking response into a readable string"""
        try:
            data = tracking_data.get("data", [])
            if not data:
                return "No tracking information available."

            tracking_info = data[0]
            status = tracking_info.get("status", "unknown")
            latest_event = tracking_info.get("latest_event", "No events recorded")
            estimated_delivery = tracking_info.get("estimated_delivery", "Not available")
            courier = tracking_info.get("courier_code", "Unknown")
            events = tracking_info.get("events", [])
            
            # Format tracking events
            event_log = "\n\n📋 Tracking History:"
            for event in events[:5]:  # Show last 5 events
                date = event.get("date", "No date")
                status = event.get("status", "No status")
                location = event.get("location", "No location")
                event_log += f"\n• {date}: {status} at {location}"
            
            formatted_response = f"""
📦 Tracking Information:
------------------------
🚚 Courier: {courier}
📊 Status: {status}
🔄 Latest Update: {latest_event}
📅 Estimated Delivery: {estimated_delivery}
{event_log}
"""
            return formatted_response.strip()
        except Exception as e:
            return f"Error formatting tracking data: {str(e)}"

    def detect_courier(self, tracking_number: str) -> Dict[str, Any]:
        """Detect courier based on tracking number"""
        endpoint = f"{self.base_url}/couriers/detect"
        data = {"tracking_number": tracking_number}
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
