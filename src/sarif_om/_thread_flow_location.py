# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class ThreadFlowLocation(object):
    """A location visited by an analysis tool while simulating or monitoring the execution of a program."""

    execution_order = attr.ib(
        default=-1, metadata={"schema_property_name": "executionOrder"}
    )
    execution_time_utc = attr.ib(
        default=None, metadata={"schema_property_name": "executionTimeUtc"}
    )
    importance = attr.ib(
        default="important", metadata={"schema_property_name": "importance"}
    )
    index = attr.ib(default=-1, metadata={"schema_property_name": "index"})
    kinds = attr.ib(default=None, metadata={"schema_property_name": "kinds"})
    location = attr.ib(default=None, metadata={"schema_property_name": "location"})
    module = attr.ib(default=None, metadata={"schema_property_name": "module"})
    nesting_level = attr.ib(
        default=None, metadata={"schema_property_name": "nestingLevel"}
    )
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    stack = attr.ib(default=None, metadata={"schema_property_name": "stack"})
    state = attr.ib(default=None, metadata={"schema_property_name": "state"})
    taxa = attr.ib(default=None, metadata={"schema_property_name": "taxa"})
    web_request = attr.ib(default=None, metadata={"schema_property_name": "webRequest"})
    web_response = attr.ib(
        default=None, metadata={"schema_property_name": "webResponse"}
    )
