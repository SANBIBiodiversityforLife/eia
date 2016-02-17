from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from core import models
from django.core.urlresolvers import reverse
from django.db.models.base import ObjectDoesNotExist
import requests
from mptt.admin import MPTTModelAdmin
from django.conf import settings

class MyUserAdmin(UserAdmin):
    l = list(UserAdmin.list_filter)
    l.remove('is_superuser')
    list_filter = tuple(l)
    actions = UserAdmin.actions
    actions.append('add_to_trusted_group')
    actions.append('add_to_contributor_group')
    actions.append('remove_from_trusted_group')
    actions.append('remove_from_contributor_group')
    actions.append('disable_user')

    list_display = UserAdmin.list_display + ('is_trusted', 'is_contributor', 'is_active', 'last_login')
    l = list(list_display)
    l.remove('username')
    list_display = tuple(l)
    '''
    def get_actions(self, request):
        # Disable delete
        actions = super(MyUserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False'''

    def is_trusted(self, obj):
        if obj.groups.count():
            trusted_group = Group.objects.get(name='trusted')
            request_trusted_group = Group.objects.get(name='request_trusted')
            if trusted_group in obj.groups.all():
                return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
            elif request_trusted_group in obj.groups.all():
                return 'Requested'
            else:
                return '<img src="/static/admin/img/icon-no.gif" alt="False">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    is_trusted.short_description = "Trusted"
    is_trusted.allow_tags = True

    def is_contributor(self, obj):
        if obj.groups.count():
            contributor_group = Group.objects.get(name='contributor')
            request_contributor_group = Group.objects.get(name='request_contributor')
            if contributor_group in obj.groups.all():
                return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
            elif request_contributor_group in obj.groups.all():
                return 'Requested'
            else:
                return '<img src="/static/admin/img/icon-no.gif" alt="False">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    is_contributor.short_description = "Contributor"
    is_contributor.allow_tags = True

    # Actions
    def add_to_trusted_group(self, request, queryset):
        trusted_group = Group.objects.get(name='trusted')
        for user in queryset:
            user.groups.add(trusted_group)
    add_to_trusted_group.short_description = "Add user(s) to trusted group"

    def add_to_contributor_group(self, request, queryset):
        contributor_group = Group.objects.get(name='contributor')
        for user in queryset:
            user.groups.add(contributor_group)
    add_to_contributor_group.short_description = "Add user(s) to contributor group"

    def remove_from_trusted_group(self, request, queryset):
        trusted_group = Group.objects.get(name='trusted')
        request_trusted_group = Group.objects.get(name='request_trusted')
        for user in queryset:
            if trusted_group in user.groups.all():
                user.groups.remove(trusted_group)
            if request_trusted_group in user.groups.all():
                user.groups.remove(request_trusted_group)
    remove_from_trusted_group.short_description = "Remove user(s) from trusted group"

    def remove_from_contributor_group(self, request, queryset):
        contributor_group = Group.objects.get(name='contributor')
        request_contributor_group = Group.objects.get(name='request_contributor')
        for user in queryset:
            if contributor_group in user.groups.all():
                user.groups.remove(contributor_group)
            if request_contributor_group in user.groups.all():
                user.groups.remove(request_contributor_group)
    remove_from_contributor_group.short_description = "Remove user(s) from contributor group"

    def disable_user(self, request, queryset):
        for user in queryset:
            user.is_active = False
            user.save()
    disable_user.short_description = 'Disable user(s)'

    #list_filter = UserAdmin.list_filter + ('is_active',)

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

# Projects
admin.site.register(models.Project, admin.ModelAdmin)

# Focal sites
admin.site.register(models.FocalSite, admin.ModelAdmin)

# Adminsite customisation
admin.site.site_header = "Administration"

# Flagged metadata/datasets
class RemovalFlagAdmin(admin.ModelAdmin):
    list_display = admin.ModelAdmin.list_display + ('project', 'data', 'data_uploaded_by', 'removal_requested_by', 'reason', 'requested_on')
    l = list(list_display)
    l.remove('__str__')
    list_display = tuple(l)
    actions = admin.ModelAdmin.actions
    actions.append('remove_dataset')

    def remove_dataset(self, request, queryset):
        # Retrieve a list of all of the unique metadatas associated with these removal flags
        metadata_pks = queryset.order_by().values_list("metadata", flat=True).distinct()

        # Delete the metadatas. This should cascade:
        # RemovalFlag, PopulationData, FocalSiteData, FatalityData all have fks to metadata
        # So all of these objects should be deleted
        models.MetaData.objects.filter(pk__in=metadata_pks).delete()
    remove_dataset.short_description = "Delete reported datasets (permanent)"

    def project(self, obj):
        url = reverse('project_detail', args=(obj.metadata.project.pk,))
        return '<a href="%s">%s</a>' % (url, obj.metadata.project)
    project.allow_tags = True

    def data_uploaded_by(self, obj):
        url = reverse('profile_detail', args=(obj.metadata.uploader.pk,))
        return '<a href="%s">%s</a>' % (url, obj.metadata.uploader)
    data_uploaded_by.allow_tags = True

    def removal_requested_by(self, obj):
        url = reverse('profile_detail', args=(obj.requested_by.pk,))
        return '<a href="%s">%s</a>' % (url, obj.requested_by)
    removal_requested_by.allow_tags = True

    def _get_data_type(self, metadata):
        if models.PopulationData.objects.filter(metadata=metadata).exists():
            return 'population_data'
        elif models.FatalityData.objects.filter(metadata=metadata).exists():
            return 'fatality_data'
        elif models.FocalSiteData.objects.filter(metadata=metadata).exists():
            return 'focal_site_data'
        elif models.FatalityRate.objects.filter(metadata=metadata).exists():
            return 'fatality_rates'
        else:
            return False

    def data(self, obj):
        url = reverse('project_detail', args=(obj.metadata.project.pk,))

        # We need to work out what type of data it is
        data = self._get_data_type(obj.metadata)

        # Return the correct URL
        return '%s | <a href="%s">%s</a>' % (data.replace('_', ' ').capitalize(),
                                             reverse(data, args=(obj.metadata.project.pk, obj.metadata.pk)),
                                             obj.metadata)
    data.allow_tags = True

admin.site.register(models.RemovalFlag, RemovalFlagAdmin)


class TaxonAdmin(MPTTModelAdmin):
    change_list_template = 'admin/core/taxon/change_list.html'
    search_fields = ('name', 'vernacular_name')
    actions = admin.ModelAdmin.actions
    actions.append('set_sensitive')
    actions.append('remove_sensitive')

    def set_sensitive(self, request, queryset):
        # Set all in queryset to be sensitive
        for taxon in queryset:
            taxon.sensitive = True
            taxon.save()
    set_sensitive.short_description = "Set taxa to 'sensitive' (not visible to anybody without trusted status)"

    def remove_sensitive(self, request, queryset):
        # Set all in queryset to be sensitive
        for taxon in queryset:
            taxon.sensitive = False
            taxon.save()
    remove_sensitive.short_description = "Remove 'sensitive' status (taxa will be visible to anybody without trusted " \
                                         "status)"

    def get_actions(self, request):
        # Disable delete
        actions = super(TaxonAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(models.Taxon, TaxonAdmin)


# Documents
class DocumentAdmin(admin.ModelAdmin):
    # Below controls the table display in the change_list in the admin site (list of all documents)
    list_display = admin.ModelAdmin.list_display + ('project', 'metadata', 'uploaded', 'uploader', 'document', 'document_type')
    l = list(list_display)
    l.remove('__str__')
    list_display = tuple(l)

    # Add search ability to it
    search_fields = ('document', 'project')
admin.site.register(models.Document, DocumentAdmin)
