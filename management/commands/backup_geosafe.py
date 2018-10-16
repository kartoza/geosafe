# coding=utf-8
import os

from geonode.base.management.commands import backup


class Command(backup.Command):

    help = 'Backup the GeoSAFE application data'

    def handle(self, **options):

        settings_dir = os.path.abspath(os.path.dirname(__file__))
        settings_path = os.path.join(settings_dir, 'settings.ini')

        options['config'] = options.get('config', None) or settings_path

        return super(Command, self).handle(**options)
