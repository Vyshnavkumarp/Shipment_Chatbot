import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from trackingmore_client import TrackingMoreClient
import re
import json

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize TrackingMore client
try:
    tracking_client = TrackingMoreClient()
    courier_list = tracking_client.get_courier_list()
except Exception as e:
    st.error(f"Failed to initialize TrackingMore client: {str(e)}")
    tracking_client = None
    courier_list = []

# Set page configuration
st.set_page_config(
    page_title="Shipment Assistant",
    page_icon="🚚",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial system message
    st.session_state.messages.append({
        "role": "system",
        "content": """You are a helpful shipment assistant. Your role is to:
        1. Help users track their shipments and provide status updates
        2. Answer questions about shipping services and tracking numbers
        3. Explain shipping statuses and estimated delivery times
        4. Provide clear and concise responses
        Always maintain a professional and friendly tone."""
    })

st.title("🚚 Shipment Assistant")

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Track Your Shipment")
    
    # Tracking input form
    with st.form("tracking_form"):
        tracking_number = st.text_input("Tracking Number")
        
        # Common courier services with their codes
        common_couriers = [
            ("Auto Detect", "auto"),
            ("UPS", "ups"),
            ("USPS", "usps"),
            ("FedEx", "fedex"),
            ("DHL Express", "dhl"),
            ("DHL eCommerce", "dhl-ecommerce"),
            ("TNT", "tnt"),
            ("China Post", "china-post"),
            ("Royal Mail", "royal-mail"),
            ("Canada Post", "canada-post"),
            ("Australia Post", "australia-post")
        ]
        
        # Create courier options list
        courier_options = [f"{name}" for name, _ in common_couriers]
        if courier_list:  # Add other couriers from API if available
            additional_couriers = [f"{c['courier_name']} ({c['courier_code']})" 
                                 for c in courier_list 
                                 if c['courier_code'] not in [code for _, code in common_couriers]]
            courier_options.extend(additional_couriers)
        
        selected_courier = st.selectbox("Select Courier", courier_options)
        
        submitted = st.form_submit_button("Track Shipment")
        
        if submitted and tracking_number:
            courier_code = None
            if selected_courier != "Auto Detect":
                # Handle common couriers
                for name, code in common_couriers:
                    if selected_courier == name:
                        courier_code = code
                        break
                # Handle other couriers from API
                if not courier_code and "(" in selected_courier:
                    courier_code = selected_courier.split("(")[-1].strip(")")
            
            try:
                if courier_code and courier_code != "auto":
                    # Create tracking with selected courier
                    tracking_client.create_tracking(tracking_number, courier_code)
                else:
                    # Auto detect courier
                    courier_info = tracking_client.detect_courier(tracking_number)
                    detected_courier = courier_info.get("data", [{}])[0].get("courier_code")
                    if detected_courier:
                        tracking_client.create_tracking(tracking_number, detected_courier)
                
                # Get tracking information
                tracking_data = tracking_client.get_tracking_info(tracking_number)
                if isinstance(tracking_data, dict):
                    tracking_info = tracking_client.format_tracking_response(tracking_data)
                    # Add tracking info to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Here's what I found for tracking number {tracking_number}:\n\n{tracking_info}"
                    })
            except Exception as e:
                st.error(f"Error tracking shipment: {str(e)}")
    
    # Display helpful information
    with st.expander("ℹ️ Tracking Number Format Examples"):
        st.markdown("""
        Common Tracking Number Formats:
        
        🚚 UPS
        - 1Z9999999999999999
        - 1Z999AA9999999999
        
        📬 USPS
        - 9400 1000 0000 0000 0000 00
        - 9205 5000 0000 0000 0000 00
        - CP000000000US
        
        📦 FedEx
        - 9999 9999 9999
        - 9999 9999 9999 999
        
        🌐 DHL
        - 1234567890
        - JD123456789
        
        🌍 International Format
        - AA123456789AA
        - RB123456789CN
        
        Note: The system can auto-detect most courier services based on the tracking number format.
        """)

with col2:
    st.subheader("Chat with Shipment Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't show system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your shipment..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Extract tracking number from message if present
        tracking_number = None
        for pattern in [
            r'\b([A-Z]{2}\d{9}[A-Z]{2})\b',  # International format
            r'\b(\d{12,14})\b',               # Numeric only
            r'\b([A-Z]{2}\d{10})\b',          # Alpha-numeric
            r'\b(1Z[A-Z0-9]{16})\b',          # UPS format
            r'\b(\d{20,22})\b',               # USPS format
        ]:
            match = re.search(pattern, prompt.upper())
            if match:
                tracking_number = match.group(1)
                break
        
        # If tracking number found in message, get tracking info
        if tracking_number and tracking_client:
            with st.spinner("Fetching shipment details..."):
                try:
                    # Auto detect courier
                    courier_info = tracking_client.detect_courier(tracking_number)
                    detected_courier = courier_info.get("data", [{}])[0].get("courier_code")
                    if detected_courier:
                        tracking_client.create_tracking(tracking_number, detected_courier)
                    
                    # Get tracking information
                    tracking_data = tracking_client.get_tracking_info(tracking_number)
                    if isinstance(tracking_data, dict):
                        tracking_info = tracking_client.format_tracking_response(tracking_data)
                        # Add tracking info to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"I found tracking information for {tracking_number}:\n\n{tracking_info}"
                        })
                except Exception as e:
                    st.error(f"Error tracking shipment: {str(e)}")
        
        # Get response from Groq
        with st.spinner("Thinking..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=1,
                    stream=True
                )
                
                # Display assistant response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Process the streamed response
                    for chunk in chat_completion:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                # Add assistant's response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
            except Exception as e:
                st.error(f"Error getting response from AI: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I apologize, but I'm having trouble generating a response right now. Please try again."
                })
