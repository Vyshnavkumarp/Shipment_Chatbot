# Shipment Chatbot

A smart chatbot powered by Groq AI that helps users track shipments and get shipping-related information using the TrackingMore API.

## Features

- Real-time shipment tracking across multiple carriers
- Automatic courier detection
- Natural language interaction
- Streamlit-based user interface
- Powered by Groq's Mixtral-8x7b model

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and fill in your API keys:
   ```bash
   cp .env.template .env
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Environment Variables

- `GROQ_API_KEY`: Your Groq API key
- `TRACKINGMORE_API_KEY`: Your TrackingMore API key

## Usage

1. Start the application
2. Enter your tracking number or ask shipping-related questions
3. Get instant responses about shipment status, delivery estimates, and more

### Supported Tracking Number Formats

- International format (e.g., "AA123456789AA")
- Numeric only (e.g., "123456789012")
- Alpha-numeric (e.g., "AA123456789")
- UPS format (e.g., "1Z1234567890123456")
- USPS format (e.g., "12345678901234567890")

## Note

Make sure to keep your API keys secure and never commit them to version control.
