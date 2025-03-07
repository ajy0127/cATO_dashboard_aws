# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class Conversion(object):
    """Describes how a converter transformed the output of a static analysis tool from the analysis tool's native output format into the SARIF format."""

    tool = attr.ib(metadata={"schema_property_name": "tool"})
    analysis_tool_log_files = attr.ib(
        default=None, metadata={"schema_property_name": "analysisToolLogFiles"}
    )
    invocation = attr.ib(default=None, metadata={"schema_property_name": "invocation"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
