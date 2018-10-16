# coding=utf-8

import StringIO

from autocomplete_light.forms import ModelForm
from django.contrib import admin
from django.contrib.admin import helpers
from django.core.management import call_command
from django.template.response import TemplateResponse
from modeltranslation.admin import TranslationAdmin

from geonode.base.models import Backup


# Admin overrides
class MediaTranslationAdmin(TranslationAdmin):
    class Media:
        js = (
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class BackupAdminForm(ModelForm):

    class Meta:
        model = Backup
        fields = '__all__'


def run(self, request, queryset):
    """
    Running a Backup
    """
    if request.POST.get('_selected_action'):
        id = request.POST.get('_selected_action')
        siteObj = self.model.objects.get(pk=id)
        if request.POST.get("post"):
            for siteObj in queryset:
                self.message_user(request, "Executed Backup: " + siteObj.name)
                out = StringIO.StringIO()
                call_command(
                    'backup_geosafe',
                    force_exec=True,
                    backup_dir=siteObj.base_folder,
                    stdout=out)
                value = out.getvalue()
                if value:
                    siteObj.location = value
                    siteObj.save()
                else:
                    self.message_user(
                        request, siteObj.name + " backup failed!")
        else:
            context = {
                "objects_name": "Backups",
                'title': "Confirm run of Backups:",
                'action_exec': "run",
                'cancellable_backups': [siteObj],
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }
            return TemplateResponse(
                request,
                'admin/backups/confirm_cancel.html',
                context,
                current_app=self.admin_site.name)


def restore(self, request, queryset):
    """
    Running a Restore
    """
    if request.POST.get('_selected_action'):
        id = request.POST.get('_selected_action')
        siteObj = self.model.objects.get(pk=id)
        if request.POST.get("post"):
            for siteObj in queryset:
                self.message_user(request, "Executed Restore: " + siteObj.name)
                out = StringIO.StringIO()
                if siteObj.location:
                    call_command(
                        'restore_geosafe', force_exec=True, backup_file=str(
                            siteObj.location).strip(), stdout=out)
                else:
                    self.message_user(
                        request, siteObj.name + " backup not ready!")
        else:
            context = {
                "objects_name": "Restores",
                'title': "Confirm run of Restores:",
                'action_exec': "restore",
                'cancellable_backups': [siteObj],
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            }
            return TemplateResponse(
                request,
                'admin/backups/confirm_cancel.html',
                context,
                current_app=self.admin_site.name)


run.short_description = "Run GeoSAFE Backup"
restore.short_description = "Run GeoSAFE Restore"


class BackupAdmin(MediaTranslationAdmin):
    list_display = ('id', 'name', 'date', 'location')
    list_display_links = ('name',)
    date_hierarchy = 'date'
    form = BackupAdminForm
    actions = [run, restore]


admin.site.unregister(Backup)
admin.site.register(Backup, BackupAdmin)
