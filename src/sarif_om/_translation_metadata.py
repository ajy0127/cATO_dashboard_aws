# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class TranslationMetadata(object):
    """Provides additional metadata related to translation."""

    name = attr.ib(metadata={"schema_property_name": "name"})
    download_uri = attr.ib(
        default=None, metadata={"schema_property_name": "downloadUri"}
    )
    full_description = attr.ib(
        default=None, metadata={"schema_property_name": "fullDescription"}
    )
    full_name = attr.ib(default=None, metadata={"schema_property_name": "fullName"})
    information_uri = attr.ib(
        default=None, metadata={"schema_property_name": "informationUri"}
    )
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    short_description = attr.ib(
        default=None, metadata={"schema_property_name": "shortDescription"}
    )
