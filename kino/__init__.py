# coding: UTF-8

# import sys
# sys.path.append('./kino')
# sys.path.append('./nlp')
# sys.path.append('./notifier')
# sys.path.append('./skills')
# sys.path.append('./slack')
# sys.path.append('./utils')


from .bot import KinoBot
from .management import write_skills

__all__ = ['KinoBot', 'write_skills']
