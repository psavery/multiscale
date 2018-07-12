"""
Progress Bar.

This is the progress bar that we can use for downloads and uploads.

It was adapted from the GirderCli class in the girder repository.
"""

import click
import types


def progress_bar(*args, **kwargs):
    """Progress bar function taken from GirderCli."""
    bar = click.progressbar(*args, **kwargs)
    bar.bar_template = '[%(bar)s]  %(info)s  %(label)s'
    bar.show_percent = True
    bar.show_pos = True

    def formatSize(length):
        if length == 0:
            return '%.2f' % length
        unit = ''
        # See https://en.wikipedia.org/wiki/Binary_prefix
        units = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
        while True:
            if length <= 1024 or len(units) == 0:
                break
            unit = units.pop(0)
            length /= 1024.
        return '%.2f%s' % (length, unit)

    def formatPos(_self):
        pos = formatSize(_self.pos)
        if _self.length_known:
            pos += '/%s' % formatSize(_self.length)
        return pos

    bar.format_pos = types.MethodType(formatPos, bar)
    return bar
