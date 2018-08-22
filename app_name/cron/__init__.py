# -*- coding: utf-8 -*-
import inspect
import os
from itertools import chain
from flask_script import Command, Option


class cron(Command):
    """Used to run and display crons."""

    @staticmethod
    def find_modules(directory, module_root=None):
        _module_root = os.path.basename(directory)
        if module_root:
            _module_root = module_root
        for module in os.listdir(directory):
            # skip this file and any other non-python file
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            yield __import__('%s.%s' % (_module_root, module[:-3]),
                             locals(), globals(), ['object'], 0)

    @staticmethod
    def find_subclasses(module, clazz, cron=None):
        for name in inspect.getmembers(module):
            o = getattr(module, list(name)[0])
            if (o != clazz) and inspect.isclass(o) and issubclass(o, clazz) \
                    and not inspect.isabstract(o):
                if cron is None:
                    yield o.__name__,
                elif cron == o.__name__:
                    o().run()

    def get_options(self):
        return [Option('-n', '--name', dest='name', default=None)]

    def run(self, name):
        current_directory = os.path.dirname(__file__)

        subclasses = [self.find_subclasses(module, Command, name) for module in self.find_modules(
            current_directory, 'app_name.cron')]

        subclasses = list(chain.from_iterable(subclasses))
        for classes in subclasses:
            print(list(classes)[0])