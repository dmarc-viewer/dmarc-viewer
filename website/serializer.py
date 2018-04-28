"""
<Program Name>
    serializers.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    April, 2018

<Copyright>
    See LICENSE for licensing information.

<Purpose>
   Methods for custom de-/serialization for e.g. demo, backup or data exchange
   purposes.

"""
import logging

from django.core import serializers
from django.db import transaction

from website import models

logger = logging.getLogger(__name__)


def import_views_from_json(filepath):
    """
    <Purpose>
        Deserialize JSON formatted fixture file and insert contained analysis
        views to database. Non-view related objects are ignored.

        This is similar to using the django command `python manage.py loaddata
        <filepath>`. However, while the django command might override existing
        db entries with the same primary keys, this function restores the
        relationship of the flattened fixture entires, ignoring absolute
        primary keys and adds the resulting objects to the database creating
        new keys.

        Views in the database may be written to a fixture file using the
        the following command:

        ```
        python manage.py dumpdata website.View website.FilterSet \
            website.ReportType website.DateRange website.ReportSender \
            website.ReportReceiverDomain website.SourceIP website.RawDkimDomain
            website.RawDkimResult website.MultipleDkim website.RawSpfDomain \
            website.RawSpfResult website.AlignedDkimResult \
            website.AlignedSpfResult website.Disposition > demo/views.json
        ```

        See https://docs.djangoproject.com/en/1.8/howto/initial-data/ and
        https://docs.djangoproject.com/en/1.8/topics/serialization/ for more
        infos about fixtures and serialization.

    <Arguments>
        filepath:
                Path to JSON formatted fixture file containing views

    <Exceptions>
        IOError if filepath can't be read.

    <Returns>
        None.

    """
    with open(filepath) as fp:
        deserialized_objects = serializers.deserialize("json", fp)

        pk_class_object_mapping = {}
        # All or nothing. Views are complex objects, and we only want to store
        # a view if all related objects can be stored as well.
        # TODO: This could become smarter in the future, so that we define
        # transactions per view.
        with transaction.atomic():
            for deserialized_object in deserialized_objects:
                # Extract model object from deserialization object
                obj = deserialized_object.object

                # Cache object by old primary key and class name tuple, which
                # must be unique, to restore foreign key relationship below
                pk_class_key = (obj.pk, obj.__class__)
                pk_class_object_mapping[pk_class_key] = obj

                # Removing the primary key lets db create a new entry when
                # storing to db
                obj.pk = None

                # Restore foreign key relationships by assigning the
                # corresponding object as identified by the fk id (old pk) and
                # class name, as new foreign key object
                # Except Views, which don't have foreign keys. We still list
                # it here, so that we can catch non related classes with the
                # default clause below
                # TODO: Sanitize deserialized data. Maybe we can make re-use
                # the view form validator?
                if isinstance(obj, models.View):
                    pass

                elif isinstance(obj, models.ViewFilterField):
                    obj.foreign_key = pk_class_object_mapping[
                            (obj.foreign_key_id, models.View)]

                elif isinstance(obj, models.FilterSet):
                    obj.view = pk_class_object_mapping[
                            (obj.view_id, models.View)]

                elif isinstance(obj, models.FilterSetFilterField):
                    obj.foreign_key = pk_class_object_mapping[
                            (obj.foreign_key_id, models.FilterSet)]

                else:
                    logger.info("Ignoring non-View related object of class: "
                            " '{}'".format(obj.__class__))

                obj.save()
