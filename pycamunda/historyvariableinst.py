# -*- coding: utf-8 -*-

"""This module provides access to the external task REST api of Camunda."""

from __future__ import annotations
import dataclasses
import typing

import pycamunda
import pycamunda.base
import pycamunda.variable
import pycamunda.batch
from pycamunda.request import QueryParameter

URL_SUFFIX = '/history/variable-instance'


__all__ = [
    'GetList'
]


@dataclasses.dataclass
class HistoryVariableInstance:
    """Data class of HistoryVariableInstance returned by the REST api of Camunda."""
    id_: str
    name: str
    type_: str
    value: str
    value_info: str
    process_definition_key: str
    process_definition_id: str
    process_instance_id: str
    execution_id: str
    activity_instance_id: str
    case_definition_key: str
    case_definition_id: str
    case_instance_id: str
    case_execution_id: str
    task_id: str
    tenant_id: str
    error_message: str
    state: str
    root_process_instance_id: str
    create_time: dt.datetime = None
    removal_time: dt.datetime = None

    @classmethod
    def load(cls, data: typing.Mapping[str, typing.Any]) -> HistoryVariableInstance:
        history_variable_instance = cls(
            id_=data['id'],
            name=data['name'],
            type_=data['type'],
            value=data['value'],
            value_info=data['valueInfo'],
            process_definition_key=data['processDefinitionKey'],
            process_definition_id=data['processDefinitionId'],
            process_instance_id=data['processInstanceId'],
            execution_id=data['executionId'],
            activity_instance_id=data['activityInstanceId'],
            case_definition_key=data['caseDefinitionKey'],
            case_definition_id=data['caseDefinitionId'],
            case_instance_id=data['caseInstanceId'],
            case_execution_id=data['caseExecutionId'],
            task_id=data['taskId'],
            tenant_id=data['tenantId'],
            error_message=data['errorMessage'],
            state=data['state'],
            create_time=data['createTime'],
            removal_time =data['removalTime'],
            root_process_instance_id=data['rootProcessInstanceId']
        )
        return history_variable_instance


class Get(pycamunda.base.CamundaRequest):
    variable_name = QueryParameter('variableName')
    variable_name_like = QueryParameter('variableNameLike')
    variable_value = QueryParameter('variableValue')
    variable_names_ignore_case = QueryParameter('variableNamesIgnoreCase')
    variable_values_ignore_case = QueryParameter('variableValuesIgnoreCase')
    variable_type_in = QueryParameter('variableTypeIn')
    include_deleted = QueryParameter('includeDeleted')
    process_instance_id = QueryParameter('processInstanceId')
    process_instance_id_in = QueryParameter('processInstanceIdIn')
    process_definition_id = QueryParameter('processDefinitionId')
    process_definition_key = QueryParameter('processDefinitionKey')
    execution_id_in = QueryParameter('executionIdIn')
    case_instance_id = QueryParameter('caseInstanceId')
    case_execution_id_in = QueryParameter('caseExecutionIdIn')
    case_activity_id_in = QueryParameter('caseActivityIdIn')
    task_id_in = QueryParameter('taskIdIn')
    activity_instance_id_in = QueryParameter('activityInstanceIdIn')
    tenant_id_in = QueryParameter('tenantIdIn')
    without_tenant_id = QueryParameter('withoutTenantId')
    variable_name_in = QueryParameter('variableNameIn')
    first_result = QueryParameter('firstResult')
    max_results = QueryParameter('maxResults')
    deserialize_values = QueryParameter('deserializeValues')

    sort_by = QueryParameter(
        'sortBy',
        mapping={
            'instance_id': 'instanceId',
            'variable_name': 'variableName',
            'tenant_id': 'tenantIOd'
        }
    )
    ascending = QueryParameter(
        'sortOrder',
        mapping={True: 'asc', False: 'desc'},
        provide=lambda self, obj, obj_type: vars(obj).get('sort_by', None) is not None
    )

    def __init__(
        self,
        url: str,
        variable_name: str = None,
        variable_name_like: str = None,
        variable_value: str = None,
        variable_names_ignore_case: str = None,
        variable_values_ignore_case: str = None,
        variable_type_in: str = None,
        include_deleted: str = None,
        process_instance_id: str = None,
        process_instance_id_in: str = None,
        process_definition_id: str = None,
        process_definition_key: str = None,
        execution_id_in: str = None,
        case_instance_id: str = None,
        case_execution_id_in: str = None,
        case_activity_id_in: str = None,
        task_id_in: str = None,
        activity_instance_id_in: str = None,
        tenant_id_in: str = None,
        without_tenant_id: str = None,
        variable_name_in: str = None,
        first_result: str = None,
        max_results: str = None,
        deserialize_values: str = None,
        sort_by: str = None,
        ascending: bool = None,
        timeout: int = 5
    ):
        """Query for a list of external tasks using a list of parameters. The size of the result set
        can be retrieved by using the Get Count request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the external task.
        :param process_instance_id: Filter by the process_instance_id
        """
        super().__init__(url=url + URL_SUFFIX)
        self.variable_name = variable_name
        self.variable_name_like = variable_name_like
        self.variable_value = variable_value
        self.variable_names_ignore_case = variable_names_ignore_case
        self.variable_values_ignore_case = variable_values_ignore_case
        self.variable_type_in = variable_type_in
        self.include_deleted = include_deleted
        self.process_instance_id = process_instance_id
        self.process_instance_id_in = process_instance_id_in
        self.process_definition_id = process_definition_id
        self.process_definition_key = process_definition_key
        self.execution_id_in = execution_id_in
        self.case_instance_id = case_instance_id
        self.case_execution_id_in = case_execution_id_in
        self.case_activity_id_in = case_activity_id_in
        self.task_id_in = task_id_in
        self.activity_instance_id_in = activity_instance_id_in
        self.tenant_id_in = tenant_id_in
        self.without_tenant_id = without_tenant_id
        self.variable_name_in = variable_name_in
        self.first_result = first_result
        self.max_results = max_results
        self.deserialize_values = deserialize_values
        self.sort_by = sort_by
        self.ascending = ascending
        self.timeout = timeout

    def __call__(self, *args, **kwargs) -> typing.Tuple[HistoryVariableInstance]:
        """Send the request."""
        response = super().__call__(pycamunda.base.RequestMethod.GET, *args, **kwargs, timeout=self.timeout)
        return tuple(HistoryVariableInstance.load(instance_json) for instance_json in response.json())
