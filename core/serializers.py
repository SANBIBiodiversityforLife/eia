# Can also use http://stackoverflow.com/questions/34556679/geodjango-serialize-geojson-skipping-id-field to import
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from django.utils.encoding import is_protected_type

from django.utils.encoding import smart_text
from core.models import FocalSiteData

class CustomGeoJSONSerializer(GeoJSONSerializer):
    '''def get_dump_object(self, obj):
        data = super(CustomGeoJSONSerializer, self).get_dump_object(obj)
        print(data)
        return data'''

    # http://stackoverflow.com/questions/5453237/override-django-object-serializer-to-get-rid-of-specified-model
    def end_object(self, obj):
        # This can ONLY be used on our Focal Site data because we're using explicit objects
        additions = {'pk': smart_text(obj.pk, strings_only=True),
                     'has_data': FocalSiteData.objects.filter(focal_site__pk=obj.pk).exists(),
                     'centroid': obj.location.centroid.coords}
        self._current.update(additions)
        super(CustomGeoJSONSerializer, self).end_object(obj)

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
