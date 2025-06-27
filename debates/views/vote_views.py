"""
Voting API views for the debates app.

Provides voting functionality as per requirements:
- POST /api/v1/debates/sessions/{id}/vote/: Submit a vote
- GET /api/v1/debates/sessions/{id}/votes/: Retrieve voting results
"""

import logging
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import DebateSession, Vote
from ..serializers import VoteSerializer

logger = logging.getLogger(__name__)


class DebateVoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing debate votes.
    
    Provides CRUD operations for votes with proper filtering.
    """
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return votes filtered by user or session"""
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return Vote.objects.filter(debate_session_id=session_id)
        return Vote.objects.filter(user=self.request.user)


class VoteSubmissionViewSet(viewsets.ViewSet):
    """
    ViewSet for handling vote submissions.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='vote')
    def submit_vote(self, request, pk=None):
        """
        Submit a vote for a debate session.
        
        POST /api/v1/debates/sessions/{id}/vote/
        
        Request body: 
        {
            "vote_type": "BEST_ARGUMENT" or "WINNING_SIDE"
        }
        
        Requirements:
        - Only students can vote
        - User can vote only once per debate session
        - Debate session must be active
        """
        try:
            # Get the debate session
            session = get_object_or_404(DebateSession, id=pk)
            
            # Validate that only students can vote
            if request.user.role != 'student':
                return Response({
                    'error': 'Only students can vote'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validate that the session allows voting
            if session.status not in ['voting', 'online']:
                return Response({
                    'error': 'Voting is not currently active for this session'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already voted
            existing_vote = Vote.objects.filter(
                debate_session=session, 
                user=request.user
            ).first()
            
            if existing_vote:
                return Response({
                    'error': 'You have already voted in this session'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate vote_type
            vote_type = request.data.get('vote_type')
            if vote_type not in ['BEST_ARGUMENT', 'WINNING_SIDE']:
                return Response({
                    'error': 'vote_type must be either "BEST_ARGUMENT" or "WINNING_SIDE"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the vote
            with transaction.atomic():
                vote = Vote.objects.create(
                    debate_session=session,
                    user=request.user,
                    vote_type=vote_type
                )
                
                # Broadcast voting update via WebSocket
                try:
                    from ..services.websocket_service import broadcast_vote_update
                    broadcast_vote_update(session, vote)
                except ImportError:
                    logger.warning("WebSocket service not available for vote broadcasting")
            
            return Response({
                'message': 'Vote submitted successfully',
                'vote': VoteSerializer(vote).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error submitting vote: {str(e)}")
            return Response({
                'error': 'An error occurred while submitting your vote'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='votes')
    def get_voting_results(self, request, pk=None):
        """
        Retrieve voting results for a debate session.
        
        GET /api/v1/debates/sessions/{id}/votes/
        
        Response:
        {
            "best_argument_votes": 10,
            "winning_side_votes": 15,
            "total_votes": 25,
            "user_voted": true
        }
        """
        try:
            # Get the debate session
            session = get_object_or_404(DebateSession, id=pk)
            
            # Get vote statistics
            votes = Vote.objects.filter(debate_session=session)
            
            best_argument_votes = votes.filter(vote_type='BEST_ARGUMENT').count()
            winning_side_votes = votes.filter(vote_type='WINNING_SIDE').count()
            total_votes = votes.count()
            
            # Check if current user has voted
            user_voted = votes.filter(user=request.user).exists()
            
            return Response({
                'best_argument_votes': best_argument_votes,
                'winning_side_votes': winning_side_votes,
                'total_votes': total_votes,
                'user_voted': user_voted
            })
            
        except Exception as e:
            logger.error(f"Error retrieving voting results: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving voting results'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
