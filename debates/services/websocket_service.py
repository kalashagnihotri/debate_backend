"""
WebSocket service for real-time updates in debate sessions.

Provides real-time broadcasting functionality for:
- Vote updates
- Participant changes
- Session status changes
"""

import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def broadcast_vote_update(session, vote):
    """
    Broadcast voting update to all participants in a debate session.
    
    Args:
        session: DebateSession instance
        vote: Vote instance that was just cast
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("No channel layer configured for WebSocket broadcasting")
            return
        
        # Get vote statistics
        from ..models import Vote
        votes = Vote.objects.filter(debate_session=session)
        best_argument_votes = votes.filter(vote_type='BEST_ARGUMENT').count()
        winning_side_votes = votes.filter(vote_type='WINNING_SIDE').count()
        
        message_data = {
            'type': 'vote_update',
            'data': {
                'session_id': session.id,
                'best_argument_votes': best_argument_votes,
                'winning_side_votes': winning_side_votes,
                'total_votes': votes.count(),
                'new_vote': {
                    'user': vote.user.username,
                    'vote_type': vote.vote_type,
                    'timestamp': vote.created_at.isoformat()
                }
            }
        }
        
        # Broadcast to session group
        async_to_sync(channel_layer.group_send)(
            f"debate_session_{session.id}",
            {
                'type': 'send_update',
                'message': json.dumps(message_data)
            }
        )
        
        logger.info(f"Vote update broadcasted for session {session.id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting vote update: {str(e)}")


def broadcast_notification(user_ids, notification_data):
    """
    Broadcast notification to specific users.
    
    Args:
        user_ids: List of user IDs to notify
        notification_data: Dictionary containing notification information
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("No channel layer configured for notification broadcasting")
            return
        
        message_data = {
            'type': 'notification',
            'data': notification_data
        }
        
        # Send to each user's personal channel
        for user_id in user_ids:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    'type': 'send_notification',
                    'message': json.dumps(message_data)
                }
            )
        
        logger.info(f"Notification broadcasted to {len(user_ids)} users")
        
    except Exception as e:
        logger.error(f"Error broadcasting notification: {str(e)}")


def broadcast_session_update(session, update_type, data=None):
    """
    Broadcast session status updates to all participants.
    
    Args:
        session: DebateSession instance
        update_type: Type of update (status_change, participant_joined, etc.)
        data: Additional data to include in the broadcast
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("No channel layer configured for session broadcasting")
            return
        
        message_data = {
            'type': 'session_update',
            'update_type': update_type,
            'session_id': session.id,
            'session_status': session.status,
            'data': data or {}
        }
        
        # Broadcast to session group
        async_to_sync(channel_layer.group_send)(
            f"debate_session_{session.id}",
            {
                'type': 'send_update',
                'message': json.dumps(message_data)
            }
        )
        
        logger.info(f"Session update broadcasted for session {session.id}: {update_type}")
        
    except Exception as e:
        logger.error(f"Error broadcasting session update: {str(e)}")
