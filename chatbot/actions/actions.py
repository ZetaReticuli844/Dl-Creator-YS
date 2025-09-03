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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api_config import APIConfig, APIResponse, APIError, format_license_number, parse_api_date, mask_sensitive_data

@trace_stuff.trace_stuff("get_user_license_number")
def get_user_license_number(tracker: Tracker) -> str:
    license_number = tracker.get_slot("license_number")
    if license_number:
        return license_number
    
    try:
        metadata = (tracker.latest_message or {}).get("metadata", {}) if hasattr(tracker, "latest_message") else {}
        license_from_metadata = metadata.get("license_number")
        if license_from_metadata:
            return license_from_metadata
    except Exception:
        pass
    
    return None

@trace_stuff.trace_stuff("build_auth_headers_from_tracker")
def build_auth_headers_from_tracker(tracker: Tracker) -> Dict[str, str]:
    try:
        metadata = (tracker.latest_message or {}).get("metadata", {}) if hasattr(tracker, "latest_message") else {}
        user_token = metadata.get("token")
        if user_token:
            return {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }
    except Exception:
        pass
    return APIConfig.get_auth_headers()


class ActionSessionStarted(Action):
    
    @trace_stuff.trace_stuff("action_session_started_name")
    def name(self) -> Text:
        return "action_session_started"
    
    @trace_stuff.trace_stuff("action_session_started_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("authenticated", False)]

class ActionResetAuthentication(Action):
    
    @trace_stuff.trace_stuff("action_reset_authentication_name")
    def name(self) -> Text:
        return "action_reset_authentication"
    
    @trace_stuff.trace_stuff("action_reset_authentication_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("authenticated", False)]

class ActionValidateLicense(Action):
    
    @trace_stuff.trace_stuff("action_validate_license_name")
    def name(self) -> Text:
        return "action_validate_license"
    
    @trace_stuff.trace_stuff("action_validate_license_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        license_number = tracker.get_slot("license_number")
        
        if not license_number:
            dispatcher.utter_message(text="❌ Please provide a valid license number.")
            return []
        
        if not self._is_valid_format(license_number):
            dispatcher.utter_message(text="❌ Invalid license number format. Please provide a valid license number.")
            return []
        
        if not self._license_exists(license_number, headers):
            dispatcher.utter_message(text=f"❌ License number {license_number} not found in our system. Please check the number and try again.")
            return []
        
        dispatcher.utter_message(text="✅ License number validated successfully. Please provide your full name for verification.")
        return []
    
    @trace_stuff.trace_stuff("is_valid_format")
    def _is_valid_format(self, license_number: str) -> bool:
        if not license_number or len(license_number) < 6:
            return False
        
        clean_number = re.sub(r'[-_\s]', '', license_number)
        
        return bool(re.match(r'^[A-Za-z0-9]+$', clean_number))
    
    @trace_stuff.trace_stuff("license_exists")
    def _license_exists(self, license_number: str, headers: Dict[str, str]) -> bool:
        try:
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
    
    @trace_stuff.trace_stuff("action_authenticate_user_name")
    def name(self) -> Text:
        return "action_authenticate_user"
    
    @trace_stuff.trace_stuff("action_authenticate_user_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        license_number = tracker.get_slot("license_number")
        full_name = tracker.get_slot("full_name")
        
        if not license_number or not full_name:
            dispatcher.utter_message(text="❌ Both license number and name are required for authentication.")
            return []
        
        if self._authenticate_user(license_number, full_name, headers):
            license_info = self._get_license_info(license_number, headers)
            
            if license_info:
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
                    api_first_name = license_data.get("firstName", "")
                    api_last_name = license_data.get("lastName", "")
                    api_full_name = f"{api_first_name} {api_last_name}".strip()
                    
                    return full_name.strip().lower() == api_full_name.lower()
            
            return False
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False
    
    @trace_stuff.trace_stuff("get_license_info")
    def _get_license_info(self, license_number: str, headers: Dict[str, str]) -> Dict[str, Any]:
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
    
    @trace_stuff.trace_stuff("action_check_license_status_name")
    def name(self) -> Text:
        return "action_check_license_status"
    
    @trace_stuff.trace_stuff("action_check_license_status_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
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
    
    @trace_stuff.trace_stuff("action_view_license_info_name")
    def name(self) -> Text:
        return "action_view_license_info"
    
    @trace_stuff.trace_stuff("action_view_license_info_run")
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
    
    @trace_stuff.trace_stuff("action_renew_license_name")
    def name(self) -> Text:
        return "action_renew_license"
    
    @trace_stuff.trace_stuff("action_renew_license_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
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
    
    @trace_stuff.trace_stuff("action_request_duplicate_name")
    def name(self) -> Text:
        return "action_request_duplicate"
    
    @trace_stuff.trace_stuff("action_request_duplicate_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
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
    
    @trace_stuff.trace_stuff("action_add_vehicle_type_name")
    def name(self) -> Text:
        return "action_add_vehicle_type"
    
    @trace_stuff.trace_stuff("action_add_vehicle_type_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        vehicle_type = tracker.get_slot("vehicle_type")
        if not vehicle_type:
            dispatcher.utter_message(text="❌ Vehicle type not specified. Please try again.")
            return []
        
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
    
    @trace_stuff.trace_stuff("action_remove_vehicle_type_name")
    def name(self) -> Text:
        return "action_remove_vehicle_type"
    
    @trace_stuff.trace_stuff("action_remove_vehicle_type_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        vehicle_type = tracker.get_slot("vehicle_type")
        if not vehicle_type:
            dispatcher.utter_message(text="❌ Vehicle type not specified. Please try again.")
            return []
        
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
    
    @trace_stuff.trace_stuff("action_change_address_name")
    def name(self) -> Text:
        return "action_change_address"
    
    @trace_stuff.trace_stuff("action_change_address_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        new_address = tracker.get_slot("new_address")
        if not new_address:
            dispatcher.utter_message(text="❌ New address not specified. Please try again.")
            return []
        
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
    
    @trace_stuff.trace_stuff("action_change_contact_name")
    def name(self) -> Text:
        return "action_change_contact"
    
    @trace_stuff.trace_stuff("action_change_contact_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        new_contact = tracker.get_slot("new_contact")
        if not new_contact:
            dispatcher.utter_message(text="❌ New contact information not specified. Please try again.")
            return []
        
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

class ActionChangeVehicle(Action):
    
    @trace_stuff.trace_stuff("action_change_vehicle_name")
    def name(self) -> Text:
        return "action_change_vehicle"
    
    @trace_stuff.trace_stuff("action_change_vehicle_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        raw_vehicle_type = tracker.get_slot("vehicle_type")
        raw_vehicle_brand = tracker.get_slot("vehicle_brand")
        
        vehicle_type = self._extract_and_validate_vehicle_type(raw_vehicle_type)
        vehicle_brand = self._extract_and_validate_vehicle_brand(raw_vehicle_brand)
        
        if not vehicle_type:
            dispatcher.utter_message(text="❌ Vehicle type not specified or not recognized. Please specify the vehicle type (e.g., car, motorcycle, truck).")
            return []
        
        if not vehicle_brand:
            dispatcher.utter_message(text="❌ Vehicle brand not specified or not recognized. Please specify the vehicle brand (e.g., Toyota, Honda, Ford).")
            return []
        
        success, updated_license = self._change_vehicle(vehicle_type, vehicle_brand, headers)
        
        if success and updated_license:
            dispatcher.utter_message(
                text=f"✅ Your vehicle has been updated successfully!\n\n"
                     f"📋 Updated License Details:\n"
                     f"👤 Name: {updated_license.get('firstName', '')} {updated_license.get('lastName', '')}\n"
                     f"🔢 License #: {mask_sensitive_data(updated_license.get('licenseNumber', ''))}\n"
                     f"🚗 Vehicle Type: {updated_license.get('vehicleType', '')}\n"
                     f"🚗 Vehicle Make: {updated_license.get('vehicleMake', '')}\n"
                     f"📍 Address: {updated_license.get('address', '')}\n\n"
                     f"You'll receive a confirmation email within 24 hours."
            )
        elif success:
            dispatcher.utter_message(
                text=f"✅ Your vehicle has been updated to {vehicle_type.title()} - {vehicle_brand.title()} successfully! "
                     "You'll receive a confirmation email within 24 hours."
            )
        else:
            dispatcher.utter_message(text="❌ Unable to update vehicle information. Please contact our support team.")
        
        return []
    
    @trace_stuff.trace_stuff("extract_and_validate_vehicle_type")
    def _extract_and_validate_vehicle_type(self, raw_input: str) -> str:
        if not raw_input:
            return None
        
        input_lower = raw_input.lower().strip()
        
        vehicle_type_mapping = {
            'car': 'car',
            'automobile': 'car',
            'vehicle': 'car',
            'sedan': 'car',
            'suv': 'car',
            'hatchback': 'car',
            'motorcycle': 'motorcycle',
            'bike': 'motorcycle',
            'motorbike': 'motorcycle',
            'scooter': 'motorcycle',
            'truck': 'truck',
            'pickup': 'truck',
            'lorry': 'truck',
            'van': 'truck',
            'bus': 'bus',
            'coach': 'bus'
        }
        
        for term, vehicle_type in vehicle_type_mapping.items():
            if term in input_lower:
                return vehicle_type
        
        if len(input_lower.split()) > 3:
            if any(word in input_lower for word in ['bike', 'motorcycle', 'motorbike']):
                return 'motorcycle'
            elif any(word in input_lower for word in ['car', 'automobile', 'vehicle']):
                return 'car'
            elif any(word in input_lower for word in ['truck', 'pickup']):
                return 'truck'
            return None
        
        return raw_input if raw_input.lower() in vehicle_type_mapping.values() else None
    
    @trace_stuff.trace_stuff("extract_and_validate_vehicle_brand")
    def _extract_and_validate_vehicle_brand(self, raw_input: str) -> str:
        if not raw_input:
            return None
        
        input_lower = raw_input.lower().strip()
        
        known_brands = {
            'toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'volkswagen', 'vw',
            'nissan', 'hyundai', 'kia', 'mazda', 'subaru', 'mitsubishi', 'suzuki',
            'chevrolet', 'chevy', 'gmc', 'cadillac', 'buick', 'lincoln', 'jeep',
            'ram', 'dodge', 'chrysler', 'volvo', 'jaguar', 'landrover', 'porsche',
            'ferrari', 'lamborghini', 'maserati', 'bentley', 'rollsroyce',
            'yamaha', 'kawasaki', 'ducati', 'harley', 'indian', 'triumph',
            'aprilia', 'ktm', 'husqvarna'
        }
        
        if len(input_lower.split()) > 3:
            words = input_lower.split()
            for word in words:
                cleaned_word = word.strip('.,!?;:')
                if cleaned_word in known_brands:
                    return cleaned_word.title()
            return None
        
        cleaned_input = input_lower.strip('.,!?;:')
        if cleaned_input in known_brands:
            return cleaned_input.title()
        
        if cleaned_input == 'vw':
            return 'Volkswagen'
        elif cleaned_input == 'chevy':
            return 'Chevrolet'
        elif 'harley' in cleaned_input:
            return 'Harley'
        elif 'rolls' in cleaned_input:
            return 'RollsRoyce'
        elif 'land' in cleaned_input and 'rover' in cleaned_input:
            return 'LandRover'
        
        return raw_input.title() if len(raw_input.split()) == 1 else None
    
    @trace_stuff.trace_stuff("change_vehicle")
    def _change_vehicle(self, vehicle_type: str, vehicle_brand: str, headers: Dict[str, str]) -> tuple[bool, dict]:
        try:
            base_url = APIConfig.get_endpoint_url("change_vehicle")
            params = {
                "vehicleType": vehicle_type,
                "vehicleBrand": vehicle_brand
            }
            
            response = requests.post(
                base_url,
                headers=headers,
                params=params,
                timeout=APIConfig.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                license_data = data.get("data", {}) if success else {}
                return success, license_data
            else:
                logger.warning(f"API call failed with status {response.status_code}")
                return False, {}
                
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return False, {}

class ActionValidateVehicleSlots(Action):
    
    @trace_stuff.trace_stuff("action_validate_vehicle_slots_name")
    def name(self) -> Text:
        return "action_validate_vehicle_slots"
    
    @trace_stuff.trace_stuff("action_validate_vehicle_slots_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        entities = tracker.latest_message.get('entities', [])
        user_text = tracker.latest_message.get('text', '')
        
        vehicle_type = None
        vehicle_brand = None
        
        for entity in entities:
            if entity['entity'] == 'vehicle_type':
                vehicle_type = entity['value']
            elif entity['entity'] == 'vehicle_brand':
                vehicle_brand = entity['value']
        
        if not vehicle_type or not vehicle_brand:
            extracted_type, extracted_brand = self._extract_from_text(user_text)
            if not vehicle_type:
                vehicle_type = extracted_type
            if not vehicle_brand:
                vehicle_brand = extracted_brand
        
        events = []
        if vehicle_type:
            events.append(SlotSet("vehicle_type", vehicle_type))
        if vehicle_brand:
            events.append(SlotSet("vehicle_brand", vehicle_brand))
        
        return events
    
    @trace_stuff.trace_stuff("extract_from_text")
    def _extract_from_text(self, text: str) -> tuple[str, str]:
        if not text:
            return None, None
        
        text_lower = text.lower()
        
        vehicle_type = None
        if any(word in text_lower for word in ['bike', 'motorcycle', 'motorbike']):
            vehicle_type = 'motorcycle'
        elif any(word in text_lower for word in ['car', 'automobile', 'vehicle']):
            vehicle_type = 'car'
        elif any(word in text_lower for word in ['truck', 'pickup']):
            vehicle_type = 'truck'
        elif 'bus' in text_lower:
            vehicle_type = 'bus'
        
        vehicle_brand = None
        known_brands = [
            'toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'volkswagen',
            'nissan', 'hyundai', 'kia', 'mazda', 'subaru', 'mitsubishi', 'suzuki',
            'chevrolet', 'gmc', 'cadillac', 'buick', 'lincoln', 'jeep',
            'ram', 'dodge', 'chrysler', 'volvo', 'jaguar', 'porsche',
            'ferrari', 'lamborghini', 'maserati', 'bentley',
            'yamaha', 'kawasaki', 'ducati', 'harley', 'indian', 'triumph',
            'aprilia', 'ktm', 'husqvarna'
        ]
        
        for brand in known_brands:
            if brand in text_lower:
                vehicle_brand = brand.title()
                break
        
        return vehicle_type, vehicle_brand

class ActionUpdateLicenseStatus(Action):
    
    @trace_stuff.trace_stuff("action_update_license_status_name")
    def name(self) -> Text:
        return "action_update_license_status"
    
    @trace_stuff.trace_stuff("action_update_license_status_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        new_status = tracker.get_slot("new_status")
        
        if not new_status:
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
        
        valid_statuses = ["PENDING", "SUBMITTED", "PRINTED", "DISPATCHED", "DELIVERED", "CANCELLED"]
        if new_status.upper() not in valid_statuses:
            dispatcher.utter_message(
                text=f"❌ Invalid status '{new_status}'. Please choose from:\n"
                     f"{', '.join(valid_statuses)}"
            )
            return []
        
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
    
    @trace_stuff.trace_stuff("action_license_not_received_name")
    def name(self) -> Text:
        return "action_license_not_received"
    
    @trace_stuff.trace_stuff("action_license_not_received_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        headers = build_auth_headers_from_tracker(tracker)
        
        current_status = self._get_current_license_status(headers)
        
        if current_status:
            dispatcher.utter_message(
                text=f"📋 I can see your current license status is: **{current_status}**\n\n"
                     f"Let me update your status to DELIVERED since you haven't received your license yet."
            )
            
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
                    if license_data.get("licenseStatus"):
                        return license_data["licenseStatus"]
                    else:
                        return "PROCESSING"
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
    
    @trace_stuff.trace_stuff("update_license_status")
    def _update_license_status(self, new_status: str, headers: Dict[str, str]) -> bool:
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
    
    @trace_stuff.trace_stuff("action_fallback_name")
    def name(self) -> Text:
        return "action_fallback"
    
    @trace_stuff.trace_stuff("action_fallback_run")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            text="I'm not sure I understood that. Could you please rephrase or ask for help to see what I can assist you with?"
        )
        return []


class ActionGPTFallback(Action):
    
    @trace_stuff.trace_stuff("action_gpt_fallback_name")
    def name(self) -> Text:
        return "action_gpt_fallback"
    
    @trace_stuff.trace_stuff("action_gpt_fallback_init")
    def __init__(self):
        super().__init__()
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
    
    @trace_stuff.trace_stuff("action_gpt_fallback_run")
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
        
        user_message = tracker.latest_message.get('text', '')
        
        context = self._get_conversation_context(tracker)
        
        try:
            response = self._call_gpt(user_message, context)
            
            if response:
                dispatcher.utter_message(text=response)
            else:
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
    
    @trace_stuff.trace_stuff("get_conversation_context")
    def _get_conversation_context(self, tracker: Tracker) -> str:
        messages = []
        events = tracker.events
        
        for event in events[-20:]:
            if event.get('event') == 'user':
                messages.append(f"User: {event.get('text', '')}")
            elif event.get('event') == 'bot' and event.get('text'):
                messages.append(f"Bot: {event.get('text', '')}")
        
        return "\n".join(messages[-10:]) if messages else ""
    
    @trace_stuff.trace_stuff("gpt_api_call")
    def _call_gpt(self, user_message: str, context: str) -> str:
        try:
            system_prompt = """You are an AI assistant for a Driving License Management System. 
            Your primary role is to help users with driving license related queries including:
            - Checking license status
            - License renewals
            - Duplicate license requests
            - Adding/removing vehicle types
            - Address and contact updates
            - General license information
            - Vehicle type changes and vehicle brand changes

            When users ask questions outside of driving license topics, politely redirect them back to license-related services while being helpful.
            
            Keep your responses concise, helpful, and professional. Always maintain the helpful and friendly tone of the license management system.
            
            If users ask for specific license actions (like checking status, renewals, etc.), let them know that you can help them navigate to the right service, but the actual processing will be handled by the official system.
            
            Context from recent conversation:
            """ + context
     
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
      
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                timeout=10,
                extra_headers={
                    "HTTP-Referer": "https://localhost:5005",  
                    "X-Title": "Rasa License Chatbot", 
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
    
    @trace_stuff.trace_stuff("action_gpt_query_name")
    def name(self) -> Text:
        return "action_gpt_query"
    
    @trace_stuff.trace_stuff("action_gpt_query_init")
    def __init__(self):
        super().__init__()
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
    
    @trace_stuff.trace_stuff("action_gpt_query_run")
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
    
    @trace_stuff.trace_stuff("get_conversation_context")
    def _get_conversation_context(self, tracker: Tracker) -> str:
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
                    "HTTP-Referer": "https://localhost:5005",
                    "X-Title": "Rasa License Chatbot",
                }
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek query call failed: {e}")
            return None