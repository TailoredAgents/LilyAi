import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import structlog
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

from app.core.config import settings

logger = structlog.get_logger()

# Scopes required for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """Google Calendar integration client"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.service = None
        self.credentials_file = f"/tmp/google_calendar_credentials_{tenant_id}.json"
        self.token_file = f"/tmp/google_calendar_token_{tenant_id}.pickle"
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get or refresh Google API credentials for the tenant"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, initiate auth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning("Failed to refresh credentials", error=str(e))
                    creds = None
            
            if not creds:
                # Create credentials file for OAuth flow
                client_config = {
                    "installed": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                    }
                }
                
                if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                    logger.error("Google Calendar credentials not configured")
                    return None
                
                with open(self.credentials_file, 'w') as f:
                    json.dump(client_config, f)
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error("Failed to complete OAuth flow", error=str(e))
                    return None
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def _get_service(self):
        """Get Google Calendar service instance"""
        if self.service:
            return self.service
        
        creds = self._get_credentials()
        if not creds:
            return None
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return self.service
        except Exception as e:
            logger.error("Failed to build Calendar service", error=str(e))
            return None
    
    async def create_event(
        self,
        start: datetime,
        end: datetime,
        summary: str,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Google Calendar event
        
        Args:
            start: Event start time
            end: Event end time  
            summary: Event title
            description: Event description
            attendees: List of attendee email addresses
            location: Event location
            calendar_id: Calendar ID (defaults to primary)
        
        Returns:
            Created event data or None if failed
        """
        service = self._get_service()
        if not service:
            logger.error("Google Calendar service not available")
            return None
        
        try:
            event_body = {
                'summary': summary,
                'start': {
                    'dateTime': start.isoformat(),
                    'timeZone': settings.DEFAULT_TIMEZONE,
                },
                'end': {
                    'dateTime': end.isoformat(),
                    'timeZone': settings.DEFAULT_TIMEZONE,
                },
            }
            
            if description:
                event_body['description'] = description
            
            if location:
                event_body['location'] = location
            
            if attendees:
                event_body['attendees'] = [{'email': email} for email in attendees]
            
            # Create the event
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            
            logger.info(
                "Google Calendar event created",
                event_id=event.get('id'),
                summary=summary,
                start=start.isoformat(),
                tenant_id=self.tenant_id
            )
            
            return event
            
        except Exception as e:
            logger.error(
                "Failed to create Google Calendar event",
                error=str(e),
                summary=summary,
                tenant_id=self.tenant_id
            )
            return None
    
    async def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        calendar_id: str = 'primary'
    ) -> Optional[Dict[str, Any]]:
        """Update an existing Google Calendar event"""
        service = self._get_service()
        if not service:
            logger.error("Google Calendar service not available")
            return None
        
        try:
            # Get existing event
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Apply updates
            event.update(updates)
            
            # Update the event
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(
                "Google Calendar event updated",
                event_id=event_id,
                tenant_id=self.tenant_id
            )
            
            return updated_event
            
        except Exception as e:
            logger.error(
                "Failed to update Google Calendar event",
                error=str(e),
                event_id=event_id,
                tenant_id=self.tenant_id
            )
            return None
    
    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """Delete a Google Calendar event"""
        service = self._get_service()
        if not service:
            logger.error("Google Calendar service not available")
            return False
        
        try:
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(
                "Google Calendar event deleted",
                event_id=event_id,
                tenant_id=self.tenant_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to delete Google Calendar event",
                error=str(e),
                event_id=event_id,
                tenant_id=self.tenant_id
            )
            return False
    
    @staticmethod
    def create_booking_event(
        tenant_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        service_type: str,
        start_time: datetime,
        duration_minutes: int = 60,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a booking event with standard formatting
        
        Args:
            tenant_id: Tenant ID
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            service_type: Type of service
            start_time: Appointment start time
            duration_minutes: Duration in minutes
            location: Service location
        
        Returns:
            Created event data or None
        """
        client = GoogleCalendarClient(tenant_id)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        summary = f"{service_type} - {customer_name}"
        
        description_parts = [
            f"Customer: {customer_name}",
            f"Phone: {customer_phone}",
            f"Email: {customer_email}",
            f"Service: {service_type}",
            "",
            "Created by Lily AI"
        ]
        
        description = "\n".join(description_parts)
        
        attendees = [customer_email] if customer_email else None
        
        return client.create_event(
            start=start_time,
            end=end_time,
            summary=summary,
            description=description,
            attendees=attendees,
            location=location
        )