"""
Service for handling voting logic and winner calculation.
"""

from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()


class VotingService:
    """Service to handle voting logic and results calculation"""

    @staticmethod
    def calculate_winner(session):
        """
        Calculate the winner of a debate session based on votes.
        Returns the user with the most votes, or None if tie/no votes.
        """
        from ..models import ParticipantRole, Participation

        # Get all participants who could receive votes
        participants = session.participants.filter(
            participation__role=ParticipantRole.PARTICIPANT
        )

        if not participants.exists():
            return None

        # Count votes for each participant
        vote_counts = {}
        for participant in participants:
            vote_count = Participation.objects.filter(
                session=session, voted_for=participant, has_voted=True
            ).count()
            vote_counts[participant] = vote_count

        # Find winner (participant with most votes)
        if not vote_counts:
            return None

        max_votes = max(vote_counts.values())
        if max_votes == 0:
            return None

        # Check for ties
        winners = [user for user, votes in vote_counts.items() if votes == max_votes]
        if len(winners) > 1:
            return None  # Tie - no winner

        # Update total votes count
        session.total_votes = sum(vote_counts.values())
        session.save(update_fields=["total_votes"])

        return winners[0]

    @staticmethod
    def update_winner_stats(user):
        """Update user statistics after winning a debate"""
        from users.models import User

        # Get or create user profile for stats tracking
        if hasattr(user, "profile"):
            profile = user.profile
        else:
            from users.models import Profile

            profile, created = Profile.objects.get_or_create(user=user)

        # Update win count (we'll add this field to Profile model)
        if hasattr(profile, "debates_won"):
            profile.debates_won += 1
            profile.save(update_fields=["debates_won"])

    @staticmethod
    def can_user_vote(user, session):
        """Check if a user can vote in the given session"""
        from ..models import DebateStatus, ParticipantRole, Participation

        # Check if session is in voting period
        if session.status != DebateStatus.CLOSED:
            return False, "Voting is not currently active"

        # Check if user is a viewer
        try:
            participation = Participation.objects.get(user=user, session=session)
            if participation.role != ParticipantRole.VIEWER:
                return False, "Only viewers can vote"

            if participation.has_voted:
                return False, "You have already voted"

            return True, "Can vote"

        except Participation.DoesNotExist:
            return False, "You are not part of this session"

    @staticmethod
    def cast_vote(user, session, voted_for_user):
        """Cast a vote for a participant"""
        from django.utils import timezone

        from ..models import ParticipantRole, Participation

        # Validate vote
        can_vote, message = VotingService.can_user_vote(user, session)
        if not can_vote:
            raise ValueError(message)

        # Validate voted_for_user is a participant
        try:
            Participation.objects.get(
                user=voted_for_user, session=session, role=ParticipantRole.PARTICIPANT
            )
        except Participation.DoesNotExist:
            raise ValueError("Can only vote for active participants")

        # Cast vote
        voter_participation = Participation.objects.get(user=user, session=session)
        voter_participation.has_voted = True
        voter_participation.voted_for = voted_for_user
        voter_participation.vote_timestamp = timezone.now()
        voter_participation.save(
            update_fields=["has_voted", "voted_for", "vote_timestamp"]
        )

        return True
