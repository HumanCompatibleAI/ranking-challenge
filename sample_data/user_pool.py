import hashlib
import random
import string
from dataclasses import dataclass, field

import numpy as np

SALT = b"9vB8nz93vD5T7Khw"

DEFAULT_PLATFORMS = ["facebook", "reddit", "twitter"]

from ranking_challenge.request import Session


@dataclass
class User:
    """
    Dataclass for the user in the user pool.
    """

    username: str
    user_id: str
    user_name_hash: str
    cohort: str
    activity_level: int
    platforms: list[str]

    @classmethod
    def generate_random(cls, platform, username=None, seed=None):
        random.seed(seed)
        if username is None:
            username = "".join(
                random.choices(string.ascii_lowercase, k=8)
                + random.choices(string.digits, k=3)
            )
        hashed_user = hashlib.sha256(username.encode()).hexdigest()
        # let's make user id deterministic from username
        user_id = hashlib.sha256(username.encode() + SALT).hexdigest()
        return cls(
            username=username,
            user_id=user_id,
            user_name_hash=hashed_user,
            cohort="XX",
            activity_level=1,
            platforms=[platform],
        )

    def get_session(self, platform, current_time):
        if platform not in self.platforms:
            raise ValueError(
                f"User {self.username} is not registered on platform {platform}"
            )
        return Session(
            user_id=self.user_id,
            user_name_hash=self.user_name_hash,
            cohort=self.cohort,
            platform=platform,
            current_time=current_time,
        )


@dataclass
class FeedParams:
    """
    Dataclass to store parameters for a feed.

    Attributes:
        n_users (int): The number of users to generate.
        baseline_sessions_per_day (int): Number of sessions per user per day.
        items_per_session (int): Number of items per session.
        activity_distribution (dict|None): A dictionary mapping activity level values
            to the number of users with that activity level. This distribution will be
            normalized, so the numbers may be floats representing probabilities
            or unnormalized relative numbers, etc.
            If None, all users will have activity level 1.
        platform_distribution (dict|None): Relative number of users for each platform.
            If None, we'll evenly distribute users across all platforms.
            Specifying a distribution is helpful when data volumes per platform are
            different. We employ a simplifying assumption that a user belongs to
            one platform only, which allows us to easily specify the distribution
            and sample from it.
    """

    n_users: int
    baseline_sessions_per_day: int
    items_per_session: int
    activity_distribution: dict = field(default_factory=lambda: {1: 1})
    platform_distribution: dict = field(
        default_factory=lambda: {platform: 1 for platform in DEFAULT_PLATFORMS}
    )


class UserPool:

    def __init__(self, feed_params: FeedParams, seed=None):
        """
        Container class for the user pool that defines basic helper methods
        and accessors.

        Args:
            feed_params (FeedParams): number of users, activity/platform distributions, etc.
            seed (int|None): A seed for the random number generator.
        """
        self.n = feed_params.n_users
        self.activity_distribution = self._normalize_distribution(
            feed_params.activity_distribution
        )
        self.platform_distribution = self._normalize_distribution(
            feed_params.platform_distribution
        )
        self.users = self._generate(seed=seed)

    def by_platform(self) -> dict[str, list[User]]:
        """
        Returns:
            dict[str, User]: User lists grouped by associated platform
        """
        platform_users = {}
        for user in self.users:
            for platform in user.platforms:
                platform_users.setdefault(platform, []).append(user)
        return platform_users

    def _normalize_distribution(self, distribution):
        total = sum(distribution.values())
        for key in distribution:
            distribution[key] /= total
        return distribution

    def _sample_outcomes(self, distribution, seed=None):
        rng = np.random.default_rng(seed=seed)
        # we first generate the actual number of users for each activity level
        # by sampling from the multinomial distribution provided
        probabilities = list(distribution.values())
        levels = list(distribution.keys())
        return rng.choice(levels, size=self.n, p=probabilities)

    def _generate(self, seed=None):

        def user_gen():
            while True:
                yield User.generate_random(seed)

        users = []
        activity_levels = self._sample_outcomes(self.activity_distribution, seed=seed)
        platforms = self._sample_outcomes(self.platform_distribution, seed=seed)
        for user, level, platform in zip(user_gen(), activity_levels, platforms):
            user.activity_level = level
            user.platforms = [platform]
            users.append(user)

        return users
