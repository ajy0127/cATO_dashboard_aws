# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class SarifLog(object):
    """Static Analysis Results Format (SARIF) Version 2.1.0-rtm.4 JSON Schema: a standard format for the output of static analysis tools."""

    runs = attr.ib(metadata={"schema_property_name": "runs"})
    version = attr.ib(metadata={"schema_property_name": "version"})
    schema_uri = attr.ib(default=None, metadata={"schema_property_name": "$schema"})
    inline_external_properties = attr.ib(
        default=None, metadata={"schema_property_name": "inlineExternalProperties"}
    )
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
