# -*- coding: utf-8 -*-

from .functions import Functions
from .github import GithubManager
from .happy import Happy
from .manager import FunctionManager
from .maxim import Maxim
from .todoist import TodoistManager
from .toggl import TogglManager
from .youtube_downloader import YoutubeDownloader
from .weather import Weather

__all__ = ['Functions',
           'FunctionManager',
           'GithubManager',
           'Happy',
           'Maxim',
           'TodoistManager',
           'TogglManager',
           'YoutubeDownloader',
           'Weather']
