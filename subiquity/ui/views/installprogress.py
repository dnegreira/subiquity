# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from urwid import (Text, Filler,
                   Pile)

from subiquitycore.view import BaseView
from subiquitycore.ui.buttons import confirm_btn
from subiquitycore.ui.utils import Padding, Color
from subiquitycore import utils

log = logging.getLogger("subiquity.views.installprogress")


class ProgressView(BaseView):
    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.text = Text("Installing Ubuntu ...", align="left")
        self.body = [
            Padding.center_79(self.text),
            Padding.line_break(""),
        ]
        self.pile = Pile(self.body)
        super().__init__(Filler(self.pile, valign="middle"))

    def set_log_tail(self, text):
        self.text.set_text(text)

    def set_error(self, text):
        self.text.set_text(text)

    def show_complete(self):
        self.text.set_text("Finished install!")
        w = Padding.fixed_20(
            Color.button(confirm_btn(label="Reboot now",
                                     on_press=self.reboot),
                         focus_map='button focus'))

        z = Padding.fixed_20(
            Color.button(confirm_btn(label="Quit Installer",
                                     on_press=self.quit),
                         focus_map='button focus'))

        self.pile.contents.append((w, self.pile.options()))
        self.pile.contents.append((z, self.pile.options()))
        self.pile.focus_position = 2

    def reboot(self, btn):
        self.controller.reboot()

    def quit(self, btn):
        self.controller.quit()
