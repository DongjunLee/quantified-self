# -*- coding: utf-8 -*-

from .functions import Functions
from .github import GithubManager
from .manager import FunctionManager
from .maxim import Maxim
from .todoist import TodoistManager
from .toggl import TogglManager
from .youtube_downloader import YoutubeDownloader
from .weather import Weather

__all__ = ['Functions',
           'GithubManager',
           'FunctionManager',
           'Maxim',
           'TodoistManager',
           'TogglManager',
           'YoutubeDownloader',
           'Weather']
