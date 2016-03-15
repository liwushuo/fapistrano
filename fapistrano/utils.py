# -*- coding: utf-8 -*-

from fabric.colors import green, red, white, yellow


def red_alert(msg, bold=True):
    print red('===>', bold=bold), white(msg, bold=bold)


def green_alert(msg, bold=True):
    print green('===>', bold=bold), white(msg, bold=bold)


def yellow_alert(msg, bold=True):
    print yellow('===>', bold=bold), white(msg, bold=bold)
