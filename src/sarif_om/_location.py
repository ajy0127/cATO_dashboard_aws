# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class Location(object):
    """A location within a programming artifact."""

    annotations = attr.ib(
        default=None, metadata={"schema_property_name": "annotations"}
    )
    id = attr.ib(default=-1, metadata={"schema_property_name": "id"})
    logical_locations = attr.ib(
        default=None, metadata={"schema_property_name": "logicalLocations"}
    )
    message = attr.ib(default=None, metadata={"schema_property_name": "message"})
    physical_location = attr.ib(
        default=None, metadata={"schema_property_name": "physicalLocation"}
    )
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    relationships = attr.ib(
        default=None, metadata={"schema_property_name": "relationships"}
    )
