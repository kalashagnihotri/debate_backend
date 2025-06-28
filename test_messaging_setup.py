#!/usr/bin/env python
"""
Quick test script to verify WebSocket messaging setup.
Run this to check if session 1 is properly configured for messaging.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineDebatePlatform.settings')
django.setup()

from debates.models import DebateSession, Participation
from django.contrib.auth import get_user_model

User = get_user_model()

def test_messaging_setup():
    """Test if session 1 is ready for messaging"""
    
    try:
        # Check session exists and is online
        session = DebateSession.objects.get(id=1)
        print(f"✓ Session 1 found: '{session.topic.title}'")
        print(f"✓ Session status: {session.status}")
        
        if session.status != 'online':
            print(f"✗ Session must be 'online' for messaging (currently '{session.status}')")
            return False
        
        # Check participants
        participants = Participation.objects.filter(session=session, role='participant')
        print(f"✓ Participants found: {participants.count()}")
        
        for p in participants:
            status = "muted" if p.is_muted else "active"
            print(f"  - {p.user.username} ({p.side}): {status}")
        
        if participants.count() == 0:
            print("✗ No participants found. Users must be participants to send messages.")
            return False
        
        print("\n✅ Session 1 is ready for messaging!")
        print("Users can now send messages through WebSocket connection.")
        return True
        
    except DebateSession.DoesNotExist:
        print("✗ Session 1 not found")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_messaging_setup()
