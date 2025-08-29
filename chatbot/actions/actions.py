# This file contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted
import re
import logging
from datetime import datetime, timedelta
import random
import requests
import json
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
import openai

import trace_stuff

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API configuration
from api_config import APIConfig, APIResponse, APIError, format_license_number, parse_api_date, mask_sensitive_data

def get_user_license_number(tracker: Tracker) -> str:
    """Get user license number from tracker session or metadata."""
    # Try to get from slot first
    license_number = tracker.get_slot("license_number")
    if license_number:
        return license_number
    
    # Try to get from latest message metadata
    try:
        metadata = (tracker.latest_message or {}).get("metadata", {}) if hasattr(tracker, "latest_message") else {}
        license_from_metadata = metadata.get("license_number")
        if license_from_metadata:
            return license_from_metadata
    except Exception:
        pass
    
    # Return None if not found
    return None

def build_auth_headers_from_tracker(tracker: Tracker) -> Dict[str, str]:
    """Build Authorization headers using user's token from message metadata when available.

    Expects React to send token from message metadata, e.g.:
    { message, sender, metadata: { token: "<jwt>" } }
    """
    try:
        metadata = (tracker.latest_message or {}).get("metadata", {}) if hasattr(tracker, "latest_message") else {}
        user_token = metadata.get("token")
        if user_token:
            return {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }
    except Exception:
        # Fall back to default headers below on any issue extracting token
        pass
    return APIConfig.get_auth_headers()



class ActionSessionStarted(Action):
    """Action to handle session start and reset authentication."""
    
    def name(self) -> Text:
        return "action_session_started"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Reset authentication on session start
        return [SlotSet("authenticated", False)]

class ActionResetAuthentication(Action):
    """Action to reset user authentication."""
    
    def name(self) -> Text:
        return "action_reset_authentication"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("authenticated", False)]

class ActionValidateLicense(Action):
    """Action to validate license number format and existence using API."""
    
    def name(self) -> Text:
        return "action_validate_license"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        license_number = tracker.get_slot("license_number")
        
        if not license_number:
            dispatcher.utter_message(text="❌ Please provide a valid license number.")
            return []
        
        # Validate license number format (basic validation)
        if not self._is_valid_format(license_number):
            dispatcher.utter_message(text="❌ Invalid license number format. Please provide a valid license number.")
            return []
        
        # Check if license exists using API
        if not self._license_exists(license_number, headers):
            dispatcher.utter_message(text=f"❌ License number {license_number} not found in our system. Please check the number and try again.")
            return []
        
        dispatcher.utter_message(text="✅ License number validated successfully. Please provide your full name for verification.")
        return []
    
    def _is_valid_format(self, license_number: str) -> bool:
        """Validate license number format."""
        # Basic format validation - can be customized based on actual format
        if not license_number or len(license_number) < 6:
            return False
        
        # Remove common separators
        clean_number = re.sub(r'[-_\s]', '', license_number)
        
        # Check if it contains alphanumeric characters
        return bool(re.match(r'^[A-Za-z0-9]+$', clean_number))
    
    @trace_stuff.trace_stuff("license_exists")
    def _license_exists(self, license_number: str, headers: Dict[str, str]) -> bool:
        """Check if license exists using API."""
        try:
            # Call the API to check if license exists
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                params={"licenseNumber": license_number},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionAuthenticateUser(Action):
    """Action to authenticate user with name verification using API."""
    
    def name(self) -> Text:
        return "action_authenticate_user"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        license_number = tracker.get_slot("license_number")
        full_name = tracker.get_slot("full_name")
        
        if not license_number or not full_name:
            dispatcher.utter_message(text="❌ Both license number and name are required for authentication.")
            return []
        
        # Authenticate using API
        if self._authenticate_user(license_number, full_name, headers):
            # Get license details to show user after successful authentication
            license_info = self._get_license_info(license_number, headers)
            
            if license_info:
                # Mask license number for security
                masked_license = mask_sensitive_data(license_info['licenseNumber'])
                
                dispatcher.utter_message(
                    text=f"✅ Authentication successful! Here are your license details:\n\n"
                         f"👤 Name: {license_info['firstName']} {license_info['lastName']}\n"
                         f"🔢 License #: {masked_license}\n"
                         f"🚗 Vehicle Type: {license_info['vehicleType']}\n"
                         f"🚗 Vehicle Make: {license_info['vehicleMake']}\n"
                         f"📅 Issue Date: {parse_api_date(license_info['issueDate'])}\n"
                         f"📅 Expiry Date: {parse_api_date(license_info['expirationDate'])}\n"
                         f"📍 Address: {license_info['address']}"
                )
            else:
                dispatcher.utter_message(
                    text="✅ Authentication successful! However, I couldn't retrieve your license details at the moment."
                )
            
            return [SlotSet("authenticated", True)]
        else:
            dispatcher.utter_message(text="❌ Authentication failed. The name doesn't match the license number. Please try again.")
            return [SlotSet("authenticated", False)]
    
    @trace_stuff.trace_stuff("authenticate_user")
    def _authenticate_user(self, license_number: str, full_name: str, headers: Dict[str, str]) -> bool:
        """Authenticate user using API."""
        try:
            # Call the API to get license details and verify name
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                timeout=APIConfig.TIMEOUT
            )
            print(response.json())
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    license_data = data["data"]
                    api_first_name = license_data.get("firstName", "")
                    api_last_name = license_data.get("lastName", "")
                    api_full_name = f"{api_first_name} {api_last_name}".strip()
                    
                    # Compare names (case-insensitive)
                    return full_name.strip().lower() == api_full_name.lower()
            
            return False
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False
    
    @trace_stuff.trace_stuff("get_license_info")
    def _get_license_info(self, license_number: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get comprehensive license information from API."""
        try:
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                params={"licenseNumber": license_number},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    return data["data"]
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None

class ActionCheckLicenseStatus(Action):
    """Action to check and display license status using API."""
    
    def name(self) -> Text:
        return "action_check_license_status"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        # Get license number from user's session/profile (you'll need to implement this)
        # license_number = get_user_license_number(tracker)
        # if not license_number:
        #     dispatcher.utter_message(text="❌ Unable to retrieve your license information. Please contact support.")
        #     return []
        
        status_info = self._get_license_status( headers)
        
        if status_info["status"] == "active":
            dispatcher.utter_message(
                text=f"✅ Great news! Your license is currently ACTIVE and valid until {status_info['expiry_date']}. You're all set to drive!"
            )
        elif status_info["status"] == "expired":
            dispatcher.utter_message(
                text=f"⚠️ Your license has EXPIRED on {status_info['expiry_date']}. You'll need to renew it before you can drive legally. Would you like me to help you with the renewal process?"
            )
        elif status_info["status"] == "suspended":
            dispatcher.utter_message(
                text="🚫 Your license is currently SUSPENDED. Please contact our support team at 1-800-LICENSE for assistance with reinstatement."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to determine license status. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("get_license_status")
    def _get_license_status(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Get license status from API."""
        try:
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                timeout=APIConfig.TIMEOUT
            )
            print(response.json())
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    license_data = data["data"]
                    expiration_date = license_data.get("expirationDate", "")
                    
                    # Parse expiration date and determine status
                    try:
                        exp_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                        current_date = datetime.now(exp_date.tzinfo)
                        
                        if exp_date > current_date:
                            return {
                                "status": "active",
                                "expiry_date": exp_date.strftime("%Y-%m-%d")
                            }
                        else:
                            return {
                                "status": "expired",
                                "expiry_date": exp_date.strftime("%Y-%m-%d")
                            }
                    except ValueError:
                        logger.error(f"Invalid date format: {expiration_date}")
                        return {"status": "unknown", "expiry_date": "N/A"}
            
            return {"status": "unknown", "expiry_date": "N/A"}
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return {"status": "unknown", "expiry_date": "N/A"}
    


class ActionViewLicenseInfo(Action):
    """Action to display comprehensive license information using API."""
    
    def name(self) -> Text:
        return "action_view_license_info"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        license_number = get_user_license_number(tracker)
        if not license_number:
            dispatcher.utter_message(text="❌ Unable to retrieve your license information. Please contact support.")
            return []
        
        license_info = self._get_license_info(license_number, headers)
        
        if license_info:
            # Mask license number for security
            masked_license = mask_sensitive_data(license_info['licenseNumber'])
            
            dispatcher.utter_message(
                text=f"📋 Here are your license details:\n\n"
                     f"👤 Name: {license_info['firstName']} {license_info['lastName']}\n"
                     f"🔢 License #: {masked_license}\n"
                     f"🚗 Vehicle Type: {license_info['vehicleType']}\n"
                     f"🚗 Vehicle Make: {license_info['vehicleMake']}\n"
                     f"📅 Issue Date: {parse_api_date(license_info['issueDate'])}\n"
                     f"📅 Expiry Date: {parse_api_date(license_info['expirationDate'])}\n"
                     f"📍 Address: {license_info['address']}"
            )
        else:
            dispatcher.utter_message(text="❌ Unable to retrieve license information. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("get_license_info")
    def _get_license_info(self, license_number: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get comprehensive license information from API."""
        try:
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                params={"licenseNumber": license_number},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    return data["data"]
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
    


class ActionRenewLicense(Action):
    """Action to process license renewal requests using API."""
    
    def name(self) -> Text:
        return "action_renew_license"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        # Process renewal using API
        renewal_result = self._process_renewal(headers)
        
        if renewal_result["success"]:
            dispatcher.utter_message(
                text="🔄 Your license renewal has been initiated! "
                     "You'll receive a confirmation email with payment instructions. "
                     "The new license will be mailed to your registered address."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to process renewal. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("process_renewal")
    def _process_renewal(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Process license renewal using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("renew_license"),
                headers=headers,
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"success": data.get("success", False)}
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return {"success": False}
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return {"success": False}

class ActionRequestDuplicate(Action):
    """Action to process duplicate license requests using API."""
    
    def name(self) -> Text:
        return "action_request_duplicate"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        # Process duplicate request using API
        request_result = self._process_duplicate_request(headers)
        
        if request_result["success"]:
            dispatcher.utter_message(
                text="📋 Your duplicate license request has been submitted! "
                     "You'll receive a confirmation email with tracking information. "
                     "The duplicate license will be mailed within 3-5 business days."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to process duplicate request. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("process_duplicate_request")
    def _process_duplicate_request(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Process duplicate license request using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("duplicate_license"),
                headers=headers,
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return {"success": data.get("success", False)}
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return {"success": False}
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return {"success": False}

class ActionAddVehicleType(Action):
    """Action to add vehicle type to license using API."""
    
    def name(self) -> Text:
        return "action_add_vehicle_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        vehicle_type = tracker.get_slot("vehicle_type")
        if not vehicle_type:
            dispatcher.utter_message(text="❌ Vehicle type not specified. Please try again.")
            return []
        
        # Process vehicle type addition using API
        success = self._add_vehicle_type(vehicle_type, headers)
        
        if success:
            dispatcher.utter_message(
                text=f"✅ {vehicle_type.title()} authorization has been added to your license! "
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to add vehicle type. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("add_vehicle_type")
    def _add_vehicle_type(self, vehicle_type: str, headers: Dict[str, str]) -> bool:
        """Add vehicle type to license using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("add_vehicle_type"),
                headers=headers,
                json={"vehicleType": vehicle_type},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionRemoveVehicleType(Action):
    """Action to remove vehicle type from license using API."""
    
    def name(self) -> Text:
        return "action_remove_vehicle_type"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        vehicle_type = tracker.get_slot("vehicle_type")
        if not vehicle_type:
            dispatcher.utter_message(text="❌ Vehicle type not specified. Please try again.")
            return []
        
        # Process vehicle type removal using API
        success = self._remove_vehicle_type(vehicle_type, headers)
        
        if success:
            dispatcher.utter_message(
                text=f"✅ {vehicle_type.title()} authorization has been removed from your license! "
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to remove vehicle type. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("remove_vehicle_type")
    def _remove_vehicle_type(self, vehicle_type: str, headers: Dict[str, str]) -> bool:
        """Remove vehicle type from license using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("remove_vehicle_type"),
                headers=headers,
                json={"vehicleType": vehicle_type},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionChangeAddress(Action):
    """Action to update license address using API."""
    
    def name(self) -> Text:
        return "action_change_address"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        new_address = tracker.get_slot("new_address")
        if not new_address:
            dispatcher.utter_message(text="❌ New address not specified. Please try again.")
            return []
        
        # Process address change using API
        print("New address processing ----",new_address)
        success = self._update_address(new_address, headers)
        
        if success:
            dispatcher.utter_message(
                text="✅ Your address has been updated successfully! "
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to update address. Please contact our support team.")
        
        return []

    @trace_stuff.trace_stuff("update_address")
    def _update_address(self, new_address: str, headers: Dict[str, str]) -> bool:
        """Update license address using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("change_address"),
                headers=headers,
                params={"address": new_address},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionChangeContact(Action):
    """Action to update license contact information using API."""
    
    def name(self) -> Text:
        return "action_change_contact"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        new_contact = tracker.get_slot("new_contact")
        if not new_contact:
            dispatcher.utter_message(text="❌ New contact information not specified. Please try again.")
            return []
        
        # Process contact change using API
        success = self._update_contact(new_contact, headers)
        
        if success:
            dispatcher.utter_message(
                text="✅ Your contact information has been updated successfully! "
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to update contact information. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("update_contact")
    def _update_contact(self, new_contact: str, headers: Dict[str, str]) -> bool:
        """Update license contact information using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("update_contact"),
                headers=headers,
                json={"newContact": new_contact},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionUpdateLicenseStatus(Action):
    """Action to update license status."""
    
    def name(self) -> Text:
        return "action_update_license_status"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        # license_number = get_user_license_number(tracker)
        # if not license_number:
        #     dispatcher.utter_message(text="❌ Unable to retrieve your license information. Please contact support.")
        #     return []
        
        new_status = tracker.get_slot("new_status")
        
        if not new_status:
            # Show available status options
            dispatcher.utter_message(
                text="🔄 What status would you like to update your license to?\n\n"
                     "Available statuses:\n"
                     "• PENDING - Application is being processed\n"
                     "• SUBMITTED - Application has been submitted\n"
                     "• PRINTED - License has been printed\n"
                     "• DISPATCHED - License has been dispatched\n"
                     "• DELIVERED - License has been delivered\n"
                     "• CANCELLED - Application has been cancelled\n\n"
                     "Please specify which status you want to set."
            )
            return []
        
        # Validate status
        valid_statuses = ["PENDING", "SUBMITTED", "PRINTED", "DISPATCHED", "DELIVERED", "CANCELLED"]
        if new_status.upper() not in valid_statuses:
            dispatcher.utter_message(
                text=f"❌ Invalid status '{new_status}'. Please choose from:\n"
                     f"{', '.join(valid_statuses)}"
            )
            return []
        
        # Update license status
        success = self._update_license_status(new_status.upper(), headers)
        
        if success:
            dispatcher.utter_message(
                text=f"✅ Your license status has been updated to {new_status.upper()} successfully!\n\n"
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to update license status. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("update_license_status")
    def _update_license_status(self, new_status: str, headers: Dict[str, str]) -> bool:
        """Update license status using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("update_license_status"),
                headers=headers,
                params={"status": new_status},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionLicenseNotReceived(Action):
    """Action to handle license not received complaints and update status to delivered."""
    
    def name(self) -> Text:
        return "action_license_not_received"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        # First, get current license status
        current_status = self._get_current_license_status(headers)
        
        if current_status:
            dispatcher.utter_message(
                text=f"📋 I can see your current license status is: **{current_status}**\n\n"
                     f"Let me update your status to DELIVERED since you haven't received your license yet."
            )
            
            # Update status to DELIVERED
            success = self._update_license_status("DELIVERED", headers)
            
            if success:
                dispatcher.utter_message(
                    text="✅ I've updated your license status to DELIVERED!\n\n"
                         "This indicates that your license should have been delivered. "
                         "If you still haven't received it within 2-3 business days, "
                         "please contact our support team at 1-800-LICENSE for assistance.\n\n"
                         "📧 You'll also receive a confirmation email about this status update."
                )
            else:
                dispatcher.utter_message(
                    text="❌ I couldn't update your status at the moment. "
                         "Please contact our support team at 1-800-LICENSE for immediate assistance."
                )
        else:
            dispatcher.utter_message(
                text="❌ I couldn't retrieve your current license status. "
                     "Please contact our support team at 1-800-LICENSE for assistance."
            )
        
        return []
    
    @trace_stuff.trace_stuff("get_current_license_status")
    def _get_current_license_status(self, headers: Dict[str, str]) -> str:
        """Get current license status from API."""
        try:
            response = requests.get(
                APIConfig.get_endpoint_url("get_license_details"),
                headers=headers,
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    license_data = data["data"]
                    # Check if there's a licenseStatus field in the response
                    if license_data.get("licenseStatus"):
                        return license_data["licenseStatus"]
                    else:
                        # If no specific status field, return a default
                        return "PROCESSING"
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
    
    @trace_stuff.trace_stuff("update_license_status")
    def _update_license_status(self, new_status: str, headers: Dict[str, str]) -> bool:
        """Update license status using API."""
        try:
            response = requests.post(
                APIConfig.get_endpoint_url("update_license_status"),
                headers=headers,
                params={"status": new_status},
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False

class ActionFallback(Action):
    """Action to handle fallback scenarios."""
    
    def name(self) -> Text:
        return "action_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            text="I'm not sure I understood that. Could you please rephrase or ask for help to see what I can assist you with?"
        )
        return []


class ActionGPTFallback(Action):
    """Action to handle queries using DeepSeek via OpenRouter when Rasa cannot understand or when specifically requested."""
    
    def name(self) -> Text:
        return "action_gpt_fallback"
    
    def __init__(self):
        super().__init__()
        # Initialize OpenRouter client for DeepSeek
        api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.warning("OPENROUTER_API_KEY or DEEPSEEK_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")
                self.client = None
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not self.client:
            dispatcher.utter_message(
                text="I'm sorry, but I'm having trouble accessing the advanced AI assistant right now. "
                     "Let me help you with the driving license services I can provide. "
                     "You can ask me about license status, renewals, duplicates, and more!"
            )
            return []
        
        # Get the user's message
        user_message = tracker.latest_message.get('text', '')
        
        # Get conversation context (last few messages)
        context = self._get_conversation_context(tracker)
        
        try:
            # Call GPT with context about the chatbot's purpose
            response = self._call_gpt(user_message, context)
            
            if response:
                dispatcher.utter_message(text=response)
            else:
                # Fallback if GPT fails
                dispatcher.utter_message(
                    text="I'm having trouble understanding that right now. Let me help you with "
                         "driving license services like checking status, renewals, or duplicate requests. "
                         "What can I assist you with?"
                )
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            dispatcher.utter_message(
                text="I apologize, but I'm experiencing some technical difficulties. "
                     "However, I can still help you with all your driving license needs! "
                     "What would you like to do today?"
            )
        
        return []
    
    def _get_conversation_context(self, tracker: Tracker) -> str:
        """Get recent conversation history for context."""
        messages = []
        events = tracker.events
        
        # Get last 10 user messages and bot responses
        for event in events[-20:]:
            if event.get('event') == 'user':
                messages.append(f"User: {event.get('text', '')}")
            elif event.get('event') == 'bot' and event.get('text'):
                messages.append(f"Bot: {event.get('text', '')}")
        
        return "\n".join(messages[-10:]) if messages else ""
    
    @trace_stuff.trace_stuff("gpt_api_call")
    def _call_gpt(self, user_message: str, context: str) -> str:
        """Call OpenAI GPT API with proper context."""
        try:
            # Create a system prompt that maintains the chatbot's identity
            system_prompt = """You are an AI assistant for a Driving License Management System. 
            Your primary role is to help users with driving license related queries including:
            - Checking license status
            - License renewals
            - Duplicate license requests
            - Adding/removing vehicle types
            - Address and contact updates
            - General license information

            When users ask questions outside of driving license topics, politely redirect them back to license-related services while being helpful.
            
            Keep your responses concise, helpful, and professional. Always maintain the helpful and friendly tone of the license management system.
            
            If users ask for specific license actions (like checking status, renewals, etc.), let them know that you can help them navigate to the right service, but the actual processing will be handled by the official system.
            
            Context from recent conversation:
            """ + context
            
            # Prepare messages for GPT
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Call DeepSeek via OpenRouter API
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                timeout=10,
                extra_headers={
                    "HTTP-Referer": "https://localhost:5005",  # Your chatbot URL
                    "X-Title": "Rasa License Chatbot",  # Your app name
                }
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return None
                
        except openai.APITimeoutError:
            logger.error("OpenRouter API timeout")
            return None
        except openai.APIError as e:
            logger.error(f"OpenRouter API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter/DeepSeek: {e}")
            return None


class ActionGPTQuery(Action):
    """Action to handle direct DeepSeek queries via OpenRouter when users explicitly ask for AI assistance."""
    
    def name(self) -> Text:
        return "action_gpt_query"
    
    def __init__(self):
        super().__init__()
        # Initialize OpenRouter client for DeepSeek
        api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.warning("OPENROUTER_API_KEY or DEEPSEEK_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")
                self.client = None
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if not self.client:
            dispatcher.utter_message(
                text="The AI assistant is currently unavailable. However, I can still help you with "
                     "all your driving license needs! What would you like to do?"
            )
            return []
        
        user_message = tracker.latest_message.get('text', '')
        context = self._get_conversation_context(tracker)
        
        try:
            response = self._call_gpt(user_message, context)
            
            if response:
                # Add a note about available services
                response += "\n\n💡 Remember, I can also help you with specific license services like status checks, renewals, and more!"
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(
                    text="I'm having trouble processing that request right now. "
                         "Let me help you with driving license services instead. What do you need?"
                )
        except Exception as e:
            logger.error(f"DeepSeek query failed: {e}")
            dispatcher.utter_message(
                text="I'm experiencing some technical difficulties with the AI assistant. "
                     "But I'm still here to help with all your license-related needs!"
            )
        
        return []
    
    def _get_conversation_context(self, tracker: Tracker) -> str:
        """Get recent conversation history for context."""
        messages = []
        events = tracker.events
        
        for event in events[-20:]:
            if event.get('event') == 'user':
                messages.append(f"User: {event.get('text', '')}")
            elif event.get('event') == 'bot' and event.get('text'):
                messages.append(f"Bot: {event.get('text', '')}")
        
        return "\n".join(messages[-10:]) if messages else ""
    
    @trace_stuff.trace_stuff("gpt_query_call")
    def _call_gpt(self, user_message: str, context: str) -> str:
        """Call OpenAI GPT API for general queries."""
        try:
            system_prompt = """You are a helpful AI assistant integrated into a Driving License Management System. 
            You can answer general questions and provide information on various topics.
            
            However, always remember your context - you're part of a driving license system, so when appropriate, 
            relate your answers back to driving, licenses, or transportation topics.
            
            Keep responses helpful, concise, and conversational.
            
            Recent conversation context:
            """ + context
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=messages,
                max_tokens=250,
                temperature=0.8,
                timeout=10,
                extra_headers={
                    "HTTP-Referer": "https://localhost:5005",  # Your chatbot URL
                    "X-Title": "Rasa License Chatbot",  # Your app name
                }
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek query call failed: {e}")
            return None
