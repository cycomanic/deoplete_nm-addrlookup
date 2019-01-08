import re
import subprocess
from subprocess import CalledProcessError
from .base import Base


class Source(Base):
    COLON_PATTERN = re.compile(r':\s?')
    COMMA_PATTERN = re.compile(r'.+,\s?')
    HEADER_PATTERN = re.compile(r'^(Bcc|Cc|From|Reply-To|To):(\s?.+\s?)')

    def __init__(self, vim):
        super().__init__(vim)

        self.rank = 80  # default is 100, give deoplete-abook priority
        self.name = 'nm-addrlookup'
        self.mark = '[nm-addrlookup]'
        self.min_pattern_length = 0
        self.filetypes = ['mail']
        self.matchers = ['matcher_full_fuzzy', 'matcher_length']

    def on_init(self, context):
        self.command = ["notmuch-addrlookup", "-m"]

    def get_complete_position(self, context):
        colon = self.COLON_PATTERN.search(context['input'])
        comma = self.COMMA_PATTERN.search(context['input'])
        return max(colon.end() if colon is not None else -1,
                   comma.end() if comma is not None else -1)

    def gather_candidates(self, context):
        ret = self.HEADER_PATTERN.search(context['input'])
        if ret is None:
            return
        retn = ret[2].strip()
        if len(retn) < 2:
            return 
        try:
            cmd = self.command + [retn]
            command_results = subprocess.check_output(cmd, universal_newlines=True).split('\n')
        except CalledProcessError:
            return

        results = []
        for row in command_results[1:]:
            try:
                name, mail, *rem = row.split('\t')
            except ValueError:
                continue
            #results.append({'word': mail, 'info': name + ' ' + ', '.join(rem)})
            results.append({'word': mail, 'info': name })
        return results
