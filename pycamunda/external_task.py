# -*- coding: utf-8 -*-

"""This module provides access to the external task REST api of Camunda."""

import dataclasses
import typing

import requests

import pycamunda
import pycamunda.request
import pycamunda.variable
from pycamunda.request import PathParameter, QueryParameter, BodyParameter, BodyParameterContainer


URL_SUFFIX = '/external-task'


@dataclasses.dataclass
class ExternalTask:
    activity_id: str
    activity_instance_id: str
    error_message: str
    error_details: str
    execution_id: str
    id_: str
    lock_expiration_time: str
    process_definition_id: str
    process_definition_key: str
    process_instance_id: str
    tenant_id: str
    retries: int
    worker_id: str
    priority: str
    topic_name: str
    suspended: bool = None
    business_key: str = None
    variables: typing.Dict[str, pycamunda.variable.Variable] = None

    @classmethod
    def load(cls, data):
        external_task =  ExternalTask(
            activity_id=data['activityId'],
            activity_instance_id=data['activityInstanceId'],
            error_message=data['errorMessage'],
            error_details=data['errorDetails'],
            execution_id=data['executionId'],
            id_=data['id'],
            lock_expiration_time=data['lockExpirationTime'],
            process_definition_id=data['processDefinitionId'],
            process_definition_key=data['processDefinitionKey'],
            process_instance_id=data['processInstanceId'],
            tenant_id=data['tenantId'],
            retries=data['retries'],
            worker_id=data['workerId'],
            priority=data['priority'],
            topic_name=data['topicName']
        )
        try:
            external_task.suspended = data['suspended']
        except KeyError:
            pass
        try:
            external_task.business_key = data['businessKey']
        except KeyError:
            pass
        try:
            variables = data['variables']
        except KeyError:
            pass
        else:
            external_task.variables = {
                var_name: pycamunda.variable.Variable(
                    type=var['type'], value=var['value'],value_info=var['valueInfo']
                )
                for var_name, var in variables.items()
            }
        return external_task


class Get(pycamunda.request.CamundaRequest):

    id_ = PathParameter('id')

    def __init__(self, url, id_):
        """Query for an external task.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the external task.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}')
        self.id_ = id_

    def send(self):
        """Send the request."""
        try:
            response = requests.get(self.url)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)

        return ExternalTask.load(response.json())


class GetList(pycamunda.request.CamundaRequest):

    id_ = QueryParameter('externalTaskId')
    topic_name = QueryParameter('topicName')
    worker_id = QueryParameter('workerId')
    locked = QueryParameter('locked', provide=pycamunda.request.value_is_true)
    not_locked = QueryParameter('notLocked', provide=pycamunda.request.value_is_true)
    with_retries_left = QueryParameter('withRetriesLeft', provide=pycamunda.request.value_is_true)
    no_retries_left = QueryParameter('noRetriesLeft', provide=pycamunda.request.value_is_true)
    lock_expiration_after = QueryParameter('lockExpirationAfter')
    lock_expiration_before = QueryParameter('lockExpirationBefore')
    activity_id = QueryParameter('activityId')
    actitity_id_in = QueryParameter('activityIdIn')
    execution_id = QueryParameter('executionId')
    process_instance_id = QueryParameter('processInstanceId')
    process_definition_id = QueryParameter('processDefinitionId')
    tenant_id_in = QueryParameter('tenantIdIn')
    active = QueryParameter('active', provide=pycamunda.request.value_is_true)
    priority_higher_equals = QueryParameter('priorityHigherThanOrEquals')
    priority_lower_equals = QueryParameter('priorityLowerThanOrEquals')
    suspended = QueryParameter('suspended', provide=pycamunda.request.value_is_true)
    sort_by = QueryParameter(
        'sortBy',
        mapping={
         'id_': 'id',
         'lock_expiration_time': 'lockExpirationTime',
         'process_instance_id': 'processInstanceId',
         'process_definition_id': 'processDefinitionId',
         'tenant_id': 'tenantId',
         'task_priority': 'taskPriority'
        }
    )
    ascending = QueryParameter(
        'sortOrder',
        mapping={True: 'asc', False: 'desc'},
        provide=lambda self, obj, obj_type: 'sort_by' in vars(self)
    )
    first_result = QueryParameter('firstResult')
    max_results = QueryParameter('maxResults')

    def __init__(self, url, id_=None, topic_name=None, worker_id=None, locked=False,
                 not_locked=False, with_retries_left=False, no_retries_left=False,
                 lock_expiration_after=None, lock_expiration_before=None, activity_id=None,
                 activity_id_in=None, execution_id=None, process_instance_id=None,
                 process_definition_id=None, tenant_id_in=None, active=False,
                 priority_higher_equals=None, priority_lower_equals=None, suspended=False,
                 sort_by=None, ascending=True, first_result=None, max_results=None):
        """Query for a list of external tasks using a list of parameters. The size of the result set
        can be retrieved by using the Get Count request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the external task.
        :param topic_name: Filter by the topic name of the external task.
        :param worker_id: Filter by the id of the worker the task was locked by last.
        :param locked: Include only locked external tasks.
        :param not_locked: Include only unlocked tasks.
        :param with_retries_left: Include only external tasks that have retries left.
        :param no_retries_left: Include only external tasks that have no retries left.
        :param lock_expiration_after: Include only external tasks with a lock that expires after a
                                      date.
        :param lock_expiration_before: Include only external tasks with a lock that expires before a
                                       date.
        :param activity_id: Filter by activity id the external task is created for.
        :param activity_id_in: Filter whether activity id is one of multiple ones.
        :param execution_id: Filter by the execution id the external task belongs to.
        :param process_instance_id: Filter by the process instance id the external task belongs to.
        :param process_definition_id: Filter by the process definition id the external task belongs
                                      to.
        :param tenant_id_in: Filter whether the tenant id is one of multiple ones.
        :param active: Include only external tasks that are active.
        :param priority_higher_equals: Include only external tasks with a priority higher than or
                                       equals to the given value.
        :param priority_lower_equals: Include only external tasks with a priority lower than or
                                      equals to the given value.
        :param suspended: Include only external tasks that are suspended.
        :param sort_by: Sort the results by `id_`, `lock_expiration_time, `process_instance_id`,
                        `process_definition_key`, `tenant_id` or `task_priority`.
        :param ascending: Sort order.
        :param first_result: Pagination of results. Index of the first result to return.
        :param max_results: Pagination of results. Maximum number of results to return.
        """
        super().__init__(url + URL_SUFFIX)
        self.id_ = id_
        self.topic_name = topic_name
        self.worker_id = worker_id
        self.locked = locked
        self.not_locked = not_locked
        self.with_retries_left = with_retries_left
        self.no_retries_left = no_retries_left
        self.lock_expiration_after = lock_expiration_after
        self.lock_expiration_before = lock_expiration_before
        self.activity_id = activity_id
        self.actitity_id_in = activity_id_in
        self.execution_id = execution_id
        self.process_instance_id = process_instance_id
        self.process_definition_id = process_definition_id
        self.tenant_id_in = tenant_id_in
        self.active = active
        self.priority_higher_equals = priority_higher_equals
        self.priority_lower_equals = priority_lower_equals
        self.suspended = suspended
        self.sort_by = sort_by
        self.ascending = ascending
        self.first_result = first_result
        self.max_results = max_results

    def send(self):
        """Send the request."""
        params = self.query_parameters()
        try:
            response = requests.get(self.url, params=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)

        return tuple(ExternalTask.load(task_json) for task_json in response.json())


class Count(GetList):

    def __init__(self, url, id_=None, topic_name=None, worker_id=None, locked=False,
                 not_locked=False, with_retries_left=False, no_retries_left=False,
                 lock_expiration_after=None, lock_expiration_before=None, activity_id=None,
                 activity_id_in=None, execution_id=None, process_instance_id=None,
                 process_definition_id=None, tenant_id_in=None, active=False,
                 priority_higher_equals=None, priority_lower_equals=None, suspended=False,
                 sort_by=None, ascending=True, first_result=None, max_results=None):
        """Get the size of the result returned by the Get List request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the external task.
        :param topic_name: Filter by the topic name of the external task.
        :param worker_id: Filter by the id of the worker the task was locked by last.
        :param locked: Include only locked external tasks.
        :param not_locked: Include only unlocked tasks.
        :param with_retries_left: Include only external tasks that have retries left.
        :param no_retries_left: Include only external tasks that have no retries left.
        :param lock_expiration_after: Include only external tasks with a lock that expires after a
                                      date.
        :param lock_expiration_before: Include only external tasks with a lock that expires before a
                                       date.
        :param activity_id: Filter by activity id the external task is created for.
        :param activity_id_in: Filter whether activity id is one of multiple ones.
        :param execution_id: Filter by the execution id the external task belongs to.
        :param process_instance_id: Filter by the process instance id the external task belongs to.
        :param process_definition_id: Filter by the process definition id the external task belongs
                                      to.
        :param tenant_id_in: Filter whether the tenant id is one of multiple ones.
        :param active: Include only external tasks that are active.
        :param priority_higher_equals: Include only external tasks with a priority higher than or
                                       equals to the given value.
        :param priority_lower_equals: Include only external tasks with a priority lower than or
                                      equals to the given value.
        :param suspended: Include only external tasks that are suspended.
        :param sort_by: Sort the results by `id_`, `lock_expiration_time, `process_instance_id`,
                        `process_definition_key`, `tenant_id` or `task_priority`.
        :param ascending: Sort order.
        :param first_result: Pagination of results. Index of the first result to return.
        :param max_results: Pagination of results. Maximum number of results to return.
        """
        super().__init__(url, id_=id_, topic_name=topic_name, worker_id=worker_id,
                         locked=locked, not_locked=not_locked, with_retries_left=with_retries_left,
                         no_retries_left=no_retries_left,
                         lock_expiration_after=lock_expiration_after,
                         lock_expiration_before=lock_expiration_before, activity_id=activity_id,
                         activity_id_in=activity_id_in, execution_id=execution_id,
                         process_instance_id=process_instance_id,
                         process_definition_id=process_definition_id, tenant_id_in=tenant_id_in,
                         active=active, priority_higher_equals=priority_higher_equals,
                         priority_lower_equals=priority_lower_equals, suspended=suspended,
                         sort_by=sort_by, ascending=ascending, first_result=first_result,
                         max_results=max_results)
        self._url += '/count'

    def send(self):
        """Send the request."""
        params = self.query_parameters()
        try:
            response = requests.get(self.url, params=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)

        return int(response.json()['count'])


class FetchAndLock(pycamunda.request.CamundaRequest):

    worker_id = BodyParameter('workerId')
    max_tasks = BodyParameter('maxTasks')
    use_priority = BodyParameter('usePriority')
    topics = BodyParameter('topics')

    def __init__(self, url, worker_id, max_tasks, use_priority=False):
        """Fetch and lock external tasks for a specific worker. Only external tasks with topics that
        are added to this request are fetched.

        :param url: Camunda Rest engine URL.
        :param worker_id: Id of the worker the external tasks are locked for.
        :param max_tasks: Maximum number of tasks to fetch.
        :param use_priority: Whether the tasks should be fetched based on their priority.
        """
        super().__init__(url + URL_SUFFIX + '/fetchAndLock')
        self.worker_id = worker_id
        self.max_tasks = max_tasks
        self.use_priority = use_priority
        self.topics = []

    def add_topic(self, name, lock_duration, variables=None, deserialize_values=False):
        """Add a topic to this request.

        :param name: Name of the topic.
        :param lock_duration: Duration to lock the fetched external tasks for in milliseconds.
        :param variables: Variables to request from the process instance the external task belongs
                          to. If set to `None` all variables are requested.
        :param deserialize_values: Whether serializable variable values are deserialized on server
                                   side.
        """
        topic = {
            'topicName': name,
            'lockDuration': lock_duration,
            'deserializeValues': deserialize_values
        }
        if variables is not None:
            topic['variables'] = variables
        self.topics.append(topic)

        return self

    def send(self):
        """Send the request"""
        params = self.body_parameters()
        try:
            response = requests.post(self.url, json=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)

        return tuple(ExternalTask.load(task_json) for task_json in response.json())


class Complete(pycamunda.request.CamundaRequest):

    id_ = PathParameter('id')
    worker_id = BodyParameter('workerId')
    variables = BodyParameter('variables')
    local_variables = BodyParameter('localVariables')

    def __init__(self, url, id_, worker_id):
        """Complete an external task that is locked for a worker.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the external task.
        :param worker_id: Id of the worker the external tasks was locked for.
        :param local_variables: Variables to send to the process instance the external task belongs
                                to. Local variables exist only in the scope of the external task.
        """
        super().__init__(url + URL_SUFFIX + '/{id}/complete')
        self.id_ = id_
        self.worker_id = worker_id
        self.variables = {}
        self.local_variables = {}

    def add_variable(self, name, value, type_=None, value_info=None):
        """Add a variable to send to the Camunda process instance.

        :param name: Name of the variable.
        :param value: Value of the variable.
        :param type_: Value type of the variable.
        :param value_info: Additional information regarding the value type.
        """
        self.variables[name] = {'value': value, 'type': type_, 'valueInfo': value_info}

        return self

    def add_local_variable(self, name, value, type_=None, value_info=None):
        """Add a local variable to send to Camunda. Local variables are set only in the scope of an
        external task.

        :param name: Name of the variable.
        :param value: Value of the variable.
        :param type_: Value type of the variable.
        :param value_info: Additional information regarding the value type.
        """
        self.local_variables[name] = {'value': value, 'type': type_, 'valueInfo': value_info}

        return self

    def send(self):
        """Send the request"""
        params = self.body_parameters()
        try:
            response = requests.post(self.url, json=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)


class HandleBPMNError(pycamunda.request.CamundaRequest):

    id_ = PathParameter('id')
    worker_id = BodyParameter('workerId')
    error_code = BodyParameter('errorCode')
    error_message = BodyParameter('errorMessage')
    variables = BodyParameter('variables')

    def __init__(self, url, id_, worker_id, error_code, error_message=None):
        """Report a business error for a running external task.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the external task.
        :param worker_id: Id of the worker that locked the external task.
        :param error_code: Error code that identifies the predefined error.
        :param error_message: Error message that describes the error.
        """
        super().__init__(url + URL_SUFFIX + '/{id}/bpmnError')
        self.id_ = id_
        self.worker_id = worker_id
        self.error_code = error_code
        self.error_message = error_message
        self.variables = {}

    def add_variable(self, name, value, type_=None, value_info=None):
        """Add a variable to send to the Camunda process instance.

        :param name: Name of the variable.
        :param value: Value of the variable.
        :param type_: Value type of the variable.
        :param value_info: Additional information regarding the value type.
        """
        self.variables[name] = {'value': value, 'type': type_, 'valueInfo': value_info}

        return self

    def send(self):
        """Send the request"""
        params = self.body_parameters()
        try:
            response = requests.post(self.url, json=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)


class HandleFailure(pycamunda.request.CamundaRequest):

    id_ = PathParameter('id')
    worker_id = BodyParameter('workerId')
    error_message = BodyParameter('errorMessage')
    error_details = BodyParameter('errorDetails')
    retries = BodyParameter('retries', validate=lambda val: val >= 0)
    retry_timeout = BodyParameter('retryTimeout', validate=lambda val: val >= 0)

    def __init__(self, url, id_, worker_id, error_message, error_details, retries, retry_timeout):
        """Report a failure to execute a running external task.

        A number of retries and a timeout until the external task can be tried can be specified.
        If retries are set to 0, the external task cannot be fetched anymore and an incident is
        created. The message of the incident is set to the value of `error_message`.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the external task.
        :param worker_id: Id of the worker that locked the external task.
        :param error_message: Error message that describes the reason of the failure.
        :param error_details: Error description.
        :param retries: How often the external task can be retried.
        :param retry_timeout: Timeout in milliseconds until the external task becomes available
        again for fetching.
        """
        super().__init__(url + URL_SUFFIX + '/{id}/failure')
        self.id_ = id_
        self.worker_id = worker_id
        self.error_message = error_message
        self.error_details = error_details
        self.retries = retries
        self.retry_timeout = retry_timeout

    def send(self):
        """Send the request"""
        params = self.body_parameters()
        try:
            response = requests.post(self.url, json=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            raise pycamunda.PyCamundaNoSuccess(response.text)
