from enum import Enum

from twitchdrives.caractions.base import ActionBase


class VoteTypes(Enum):
    ANARCHY = "ANARCHY"
    DEMOCRACY = "DEMOCRACY"
    AVERAGE = "AVERAGE"


class VoteAction(ActionBase):
    ACTION_NAME = "vote"

    async def handle(self, vote: str):
        """
        Throws KeyError if vote does not exist.
        """
        print(vote)
        vote_type = VoteTypes[vote.upper()]
        vote_backoff = await self.redis.exists("tesla:votebackoff")
        if vote_backoff:
            return

        print(vote_backoff)
        print(await self.get_state())
        print(vote_type)
