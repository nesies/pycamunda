# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.processinst
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_delete_params(engine_url, delete_input, delete_output):
    delete_user = pycamunda.processinst.Delete(url=engine_url, **delete_input)

    assert delete_user.url == engine_url + '/process-instance/anId'
    assert delete_user.query_parameters() == delete_output
    assert delete_user.body_parameters() == {}


@unittest.mock.patch('requests.delete')
def test_delete_calls_requests(mock, engine_url, delete_input):
    delete_instance = pycamunda.processinst.Delete(url=engine_url, **delete_input)
    delete_instance()

    assert mock.called


@unittest.mock.patch('requests.delete', raise_requests_exception_mock)
def test_delete_raises_pycamunda_exception(engine_url, delete_input):
    delete_instance = pycamunda.processinst.Delete(url=engine_url, **delete_input)
    with pytest.raises(pycamunda.PyCamundaException):
        delete_instance()


@unittest.mock.patch('requests.delete', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
def test_delete_raises_for_status(mock, engine_url, delete_input):
    delete_instance = pycamunda.processinst.Delete(url=engine_url, **delete_input)
    delete_instance()

    assert mock.called


@unittest.mock.patch('requests.delete', unittest.mock.MagicMock())
def test_delete_returns_none(engine_url, delete_input):
    delete_instance = pycamunda.processinst.Delete(url=engine_url, **delete_input)
    result = delete_instance()

    assert result is None
