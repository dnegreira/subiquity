# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
from typing import Set

import attr

from subiquity.common.resources import resource_path
from subiquity.common.types import IdentityData
from subiquity.server.controllers.identity import IdentityController

log = logging.getLogger("system_setup.server.controllers.identity")


def _existing_user_names(path: str) -> Set[str]:
    names = set()
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            names.add(line.split(":")[0])

    return names


class WSLIdentityController(IdentityController):
    autoinstall_schema = {
        "type": "object",
        "properties": {
            "realname": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["username", "password"],
        "additionalProperties": False,
    }

    def __init__(self, app):
        super().__init__(app)
        self.existing_usernames = _existing_user_names(self._passwd_path())
        if app.prefillInfo is None or self.interactive() is False:
            return

        # Only applies when interactive and prefill Info is set.
        idata = app.prefillInfo.get("WSLIdentity", None)
        if idata is None:
            return

        # Cannot call load_autoinstall_data because password is
        # required in that context, but not here.
        identity_data = IdentityData(
            realname=idata.get("realname", ""),
            username=idata.get("username", ""),
            hostname="",
            crypted_password="",
        )

        self.model.add_user(identity_data)
        log.debug("Prefilled Identity: {}".format(self.model.user))

    def _passwd_path(self) -> str:
        if self.app.opts.dry_run:
            return resource_path("passwd")
        else:
            return os.path.join(self.app.base_model.target, "etc/passwd")

    def load_autoinstall_data(self, data):
        if data is not None:
            identity_data = IdentityData(
                realname=data.get("realname", ""),
                username=data["username"],
                crypted_password=data["password"],
            )
            self.model.add_user(identity_data)

    def make_autoinstall(self):
        if self.model.user is None:
            return {}
        r = attr.asdict(self.model.user)
        return r

    async def GET(self) -> IdentityData:
        data = IdentityData()
        if self.model.user is not None:
            data.username = self.model.user.username
            data.realname = self.model.user.realname
        return data
