# !/usr/bin/env python3
import sys

class ProgressBar:
    def __init__(self, max_hop, line_number=0, total_lines=5):
        self.max_hop = max_hop
        self.is_hop = 0
        self.bar_length = 30
        self.total_lines = total_lines
        self.line_number = 14 + (total_lines + line_number)

    def create(self):
        self._update_bar()

    def update(self, is_hop, max_hop=None, text="", additional_text=""):
        self.is_hop = is_hop
        if max_hop is not None:
            self.max_hop = max_hop
        self._update_bar(text, additional_text)

    def destroy(self):
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _update_bar(self, text="", additional_text=""):
        percent = (self.is_hop / self.max_hop) * 100 if self.max_hop else 0
        if self.is_hop == self.max_hop:
            filled_length = self.bar_length
        else:
            filled_length = int(self.bar_length * self.is_hop // self.max_hop)
        bar = "#" * filled_length + "-" * (self.bar_length - filled_length)
        sys.stdout.write(f"\033[{self.line_number};0H")
        sys.stdout.write(
            f"\r{text} [{bar}] {percent:.2f}% {self.is_hop}/{self.max_hop} | {additional_text}"
        )
        sys.stdout.flush()
