# Can also use http://stackoverflow.com/questions/34556679/geodjango-serialize-geojson-skipping-id-field to import
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from django.utils.encoding import is_protected_type
from django.core.urlresolvers import reverse

from django.utils.encoding import smart_text
from core.models import FocalSiteData


class FocalSiteJSONSerializer(GeoJSONSerializer):
    # http://stackoverflow.com/questions/5453237/override-django-object-serializer-to-get-rid-of-specified-model
    def end_object(self, obj):
        # This whole class can ONLY be used on our Focal Site data because we're using explicit objects in this bit
        additions = {'pk': smart_text(obj.pk, strings_only=True),
                     'has_data': FocalSiteData.objects.filter(focal_site__pk=obj.pk).exists(),
                     'data_view_url': reverse('focal_site_data', kwargs={'pk': obj.project.pk,
                                                                         'focal_site_pk': obj.pk}),
                     'data_upload_url': reverse('focal_site_data_create', kwargs={'project_pk': obj.project.pk,
                                                                                  'focal_site_pk': obj.pk}),
                     'centroid': obj.location.centroid.coords}
        self._current.update(additions)
        super(FocalSiteJSONSerializer, self).end_object(obj)


class CustomGeoJSONSerializer(GeoJSONSerializer):
    # Taken from https://groups.google.com/forum/#!topic/django-users/u2L1_BAtFM0
    def handle_field(self, obj, field):
        if field.name == self.geometry_field:
            self._geometry = field._get_val_from_obj(obj)
        else:
            value = field._get_val_from_obj(obj)

            # If the object has a get_field_display() method, use it.
            display_method = "get_%s_display" % field.name
            if hasattr(obj, display_method):
                self._current[field.name] = getattr(obj, display_method)()
            # I added this else just to pass it to the generic handler
            else:
                super(CustomGeoJSONSerializer, self).handle_field(obj, field)

            '''# Protected types (i.e., primitives like None, numbers, dates,
            # and Decimals) are passed through as is. All other values are
            # converted to string first.
            elif is_protected_type(value):
                self._current[field.name] = value
            else:
                self._current[field.name] = field.value_to_string(obj)'''


        # Just in case, the default geojson serializer in geodjango does this:
            #         if field.name == self.geometry_field:
            #             self._geometry = field._get_val_from_obj(obj)
            #         else:
            #             super(Serializer, self).handle_field(obj, field)
