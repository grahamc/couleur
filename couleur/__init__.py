# -*- coding: utf-8 -*-
# <Couleur - fancy shell output for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import re
import sys
import uuid
import platform
import six

version = '0.5.0'

from six import StringIO


SUPPORTS_ANSI = False
for handle in [sys.stdout, sys.stderr]:
    if (hasattr(handle, "isatty") and handle.isatty()) or \
        ('TERM' in os.environ and os.environ['TERM'] == 'ANSI'):
        if platform.system() == 'Windows' and not (
            'TERM' in os.environ and os.environ['TERM'] == 'ANSI'):
            SUPPORTS_ANSI = False
        else:
            SUPPORTS_ANSI = True

if os.getenv('COULEUR_DISABLE'):
    SUPPORTS_ANSI = False

if os.getenv('FORCE_COULEUR'):
    SUPPORTS_ANSI = True


def minify(string):
    regex_items = re.compile('(\033\[(\d+)m)')
    regex_main = re.compile('(?P<main>(\033\[(\d+)m){2,})')

    replaced = string
    main_found = regex_main.search(string)

    if main_found:
        existent = main_found.group('main')
        found = ";".join(x[1] for x in regex_items.findall(existent))
        if found:
            replaced = string.replace(existent, '\033[%sm' % found)

    return replaced

def maybe_unicode(text):
    try:
        text = six.u(text)
    except TypeError:
        True
    finally:
        return text


def translate_colors(string):
    string = maybe_unicode(string)
    for attr in re.findall("[#][{]on[:](\w+)[}]", string):
        string = string.replace(
            six.u("#{on:%s}") % attr,
            getattr(backcolors, attr)
        )

    for attr in re.findall("[#][{](\w+)[}]", string):
        string = string.replace(
            six.u("#{%s}") % attr,
            getattr(forecolors, attr, "#{%s}" % attr)
        ).replace(
            six.u("#{%s}") % attr,
            getattr(modifiers, attr, "#{%s}" % attr)
        )

    return minify(string)


def ignore_colors(string):
    string = maybe_unicode(string)
    up_count_regex = re.compile(r'[#][{]up[}]')
    up_count = len(up_count_regex.findall(string)) or 1

    expression = six.u('^(?P<start>.*)([#][{]up[}])+(.*\\n){%d}') % up_count
    up_supress_regex = re.compile(expression, re.MULTILINE)
    string = up_supress_regex.sub('\g<start>', string)

    for attr in re.findall("[#][{]on[:](\w+)[}]", string):
        string = string.replace(six.u("#{on:%s}") % attr, six.u(""))

    for attr in re.findall("[#][{](\w+)[}]", string):
        string = (string
                  .replace(six.u("#{%s}") % attr, six.u(""))
                  .replace(six.u("#{%s}") % attr, six.u("")))

    return string


class Writer(StringIO):
    original = None
    translate = True

    def write(self, string):
        f = self.translate and translate_colors or ignore_colors
        self.original.write(f(string))


class StdOutMocker(Writer):
    original = sys.__stdout__


class StdErrMocker(Writer):
    original = sys.__stderr__


class Proxy(object):
    def __init__(self, output):
        self.old_write = output.write

        if output is sys.__stdout__:
            output = StdOutMocker()

        elif output is sys.__stderr__:
            output = StdErrMocker()

        self.output = output

    def ignore(self):
        self.output.translate = False
        if not isinstance(self.output, (StdErrMocker, StdOutMocker)):
            self.output.write = lambda x: self.old_write(ignore_colors(x))

    def enable(self):
        self.disable()

        self.output.translate = True
        if isinstance(self.output, StdOutMocker):
            sys.stdout = self.output
        elif isinstance(self.output, StdErrMocker):
            sys.stderr = self.output
        else:
            self.output.write = lambda x: self.old_write(translate_colors(x))

    def disable(self):
        if isinstance(self.output, StdOutMocker):
            sys.stdout = self.output.original
        elif isinstance(self.output, StdErrMocker):
            sys.stderr = self.output.original
        else:
            self.output.write = self.old_write

_proxy_registry = {}


def proxy(output):
    if output not in _proxy_registry.keys():
        _proxy_registry[output] = Proxy(output)

    return _proxy_registry[output]


def ansify(number):
    """Wraps the given ansi code to a proper escaped python output

    Arguments:
    - `number`: the code in question
    """
    number = str(number)
    return '\033[%sm' % number


class modifiers:
    reset = ansify(0)
    bold = ansify(1)
    blink = ansify(5)
    italic = ansify(3)
    underline = ansify(4)
    inverse = ansify(7)
    strikethrough = ansify(9)
    up = '\r\033[A'


class forecolors:
    black = ansify(30)
    red = ansify(31)
    green = ansify(32)
    yellow = ansify(33)
    blue = ansify(34)
    magenta = ansify(35)
    cyan = ansify(36)
    white = ansify(37)
    normal = ansify(39)


class backcolors:
    black = ansify(40)
    red = ansify(41)
    green = ansify(42)
    yellow = ansify(43)
    blue = ansify(44)
    magenta = ansify(45)
    cyan = ansify(46)
    white = ansify(47)
    normal = ansify(49)


class empty(object):
    def __getattr__(self, attr):
        if attr != 'up':
            return ''
        else:
            return modifiers.up

_sep1 = '_on_'
_sep2 = '_and_'


class Shell(object):
    def __init__(self, output=None, indent=2, linebreak=False, bold=False,
                 disabled=not SUPPORTS_ANSI):
        self._indentation_factor = indent
        self._indent = 0
        self._linebreak = linebreak
        self._bold = bold
        self._in_format = False
        self._disabled = disabled
        self.output = output or sys.stdout

        if disabled:
            self._backcolors = empty()
            self._forecolors = empty()
            self._modifiers = empty()
        else:
            self._backcolors = backcolors()
            self._forecolors = forecolors()
            self._modifiers = modifiers()

    def indent(self):
        self._indent += self._indentation_factor

    def dedent(self):
        self._indent -= self._indentation_factor

    def _fore(self, color):
        def get(what):
            try:
                r = getattr(self._modifiers, what)
            except AttributeError:
                r = getattr(self._forecolors, what)
            return r

        args = list(map(get, color.split("_")))
        return "".join(args)

    def _back(self, color):
        return getattr(self._backcolors, color)

    def _printer_for(self, color):
        colors = color.split(_sep1)

        parts = [
            self._fore(colors.pop(0)),
            "%s",
            self._modifiers.reset
        ]

        if colors:
            parts.insert(0, self._back(colors[0]))

        if not self._in_format:
            if self._bold:
                parts.insert(0, self._modifiers.bold)

            if self._indent:
                parts.insert(0, ' ' * self._indent)

            if self._linebreak:
                parts.append("\n")

        string = "".join(map(str, parts))

        def dec(z, replace=False):
            pre = six.u(replace and self._modifiers.up or '')
            self.output.write(maybe_unicode(pre))
            self.output.write(maybe_unicode(string % z))

        return dec

    def __getattr__(self, attr):
        if not attr.startswith("_"):
            if _sep2 in attr:
                self._in_format = True
                printers = list(map(self._printer_for, attr.split(_sep2)))

                def dec(string, replace=False):
                    unique = str(uuid.uuid4())
                    string = string.replace(r'\|', unique)
                    parts = string.split(r"|")
                    if replace:
                        self.output.write(six.u(self._modifiers.up))

                    if self._indent:
                        self.output.write(six.u(' ') * self._indent)

                    if self._bold:
                        self.output.write(six.u(self._modifiers.bold))

                    for part, output in zip(parts, printers):
                        output(part.replace(unique, r"|"))

                    if self._linebreak:
                        self.output.write(six.u("\n"))

                    self._in_format = False

                return dec

            return self._printer_for(attr)

        return super(Shell, self).__getattribute__(attr)
