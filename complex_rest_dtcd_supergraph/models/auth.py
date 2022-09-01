"""
Helper facilities for role model management.
"""

import logging
from typing import Union

from neomodel import IntegerProperty

from rest_auth.authorization import IAuthCovered
from rest_auth.models import KeyChainModel, User


log = logging.getLogger("root.rest_auth")


class RoleModelCoveredMixin(IAuthCovered):
    """Adds role model management to a node.

    See role model docs
    and https://neomodel.readthedocs.io/en/latest/extending.html#mixins
    for more info.
    """

    keychain_id = IntegerProperty()
    owner_id = IntegerProperty()

    @property
    def keychain(self) -> Union[KeyChainModel, None]:
        """Look up and return the keychain if it exists, None otherwise."""

        if self.keychain_id is not None:
            try:
                return KeyChainModel.objects.get(pk=self.keychain_id)
            except KeyChainModel.DoesNotExist:
                log.error(f"KeyChain with id = {self.keychain_id} is missing")

        return None

    @keychain.setter
    def keychain(self, keychain: KeyChainModel):
        self.keychain_id = keychain.pk
        self.save()

    @property
    def owner(self) -> Union[User, None]:
        """Look up and return the owner if it exists, None otherwise."""

        if self.owner_id is not None:
            try:
                return User.objects.get(pk=self.owner_id)
            except User.DoesNotExist:
                log.error(f"User with id = {self.owner_id} is missing")

        return None

    @owner.setter
    def owner(self, user: User):
        self.owner_id = user.pk
        self.save()
