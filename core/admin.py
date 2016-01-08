from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from core import models
from django.core.urlresolvers import reverse
from django.db.models.base import ObjectDoesNotExist

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

# Adminsite customisation
admin.site.site_header = "Administration"

# Flagged metadata/datasets
class RemovalFlagAdmin(admin.ModelAdmin):
    list_display = admin.ModelAdmin.list_display + ('project', 'data', 'data_uploaded_by', 'removal_requested_by', 'reason', 'requested_on')
    l = list(list_display)
    l.remove('__str__')
    list_display = tuple(l)
    actions = admin.ModelAdmin.actions

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

    def data(self, obj):
        url = reverse('project_detail', args=(obj.metadata.project.pk,))

        # We need to work out what type of data it is
        data = False
        if models.PopulationData.objects.filter(metadata=obj.metadata).exists():
            data = 'population_data'
        elif models.FatalityData.objects.filter(metadata=obj.metadata).exists():
            data = 'fatality_data'
        elif models.FocalSiteData.objects.filter(metadata=obj.metadata).exists():
            data = 'focal_site_data'

        # Return the correct URL
        return '<a href="%s">%s</a>' % (reverse(data, args=(obj.metadata.project.pk, obj.metadata.pk)), obj.metadata)
    data.allow_tags = True

admin.site.register(models.RemovalFlag, RemovalFlagAdmin)
