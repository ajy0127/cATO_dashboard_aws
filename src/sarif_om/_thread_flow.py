# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class ThreadFlow(object):
    """Describes a sequence of code locations that specify a path through a single thread of execution such as an operating system or fiber."""

    locations = attr.ib(metadata={"schema_property_name": "locations"})
    id = attr.ib(default=None, metadata={"schema_property_name": "id"})
    immutable_state = attr.ib(
        default=None, metadata={"schema_property_name": "immutableState"}
    )
    initial_state = attr.ib(
        default=None, metadata={"schema_property_name": "initialState"}
    )
    message = attr.ib(default=None, metadata={"schema_property_name": "message"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
