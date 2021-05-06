# encoding: utf-8
from robot.libraries.BuiltIn import BuiltIn
from rshell.tools.context.decorators import under_context

DOT = '.'


@under_context
def _get_current_testsuite_name():
    suite_name = str(BuiltIn().get_variable_value("${SUITE_NAME}"))
    return suite_name.replace(" ", "_").replace(".", "-")

@under_context
def _get_suite_source():
    return str(BuiltIn().get_variable_value("${SUITE_SOURCE}"))

@under_context
def _get_test_suite_name():
    return str(BuiltIn().get_variable_value("${SUITE_NAME}")).split(DOT)[-1].replace(" ", "_")