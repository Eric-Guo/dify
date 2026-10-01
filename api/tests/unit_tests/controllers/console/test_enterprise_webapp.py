from inspect import unwrap
from unittest.mock import Mock

import pytest
from flask import Flask

from controllers.console import enterprise_webapp
from models import Account
from services.enterprise.base import EnterpriseRequest


@pytest.mark.parametrize("allowed", [False, True])
@pytest.mark.usefixtures("app_query_services")
def test_permission_uses_app_id_through_current_access_service(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
    allowed: bool,
) -> None:
    account = Account(name="User", email="user@example.com")
    account.id = "account-1"
    monkeypatch.setattr(enterprise_webapp, "current_user", account)
    monkeypatch.setattr(enterprise_webapp.SystemFeatureService, "is_webapp_auth_enabled", lambda: True)
    request = Mock(return_value={"result": allowed})
    monkeypatch.setattr(EnterpriseRequest, "send_request", request)

    with app.test_request_context("/enterprise/webapp/permission?appId=app-1"):
        result = unwrap(enterprise_webapp.AppConsoleWebAuthPermissionApi.get)(
            enterprise_webapp.AppConsoleWebAuthPermissionApi()
        )

    assert result == {"result": allowed}
    request.assert_called_once_with("GET", "/webapp/permission", params={"userId": "account-1", "appId": "app-1"})


def test_permission_skips_enterprise_when_webapp_auth_is_disabled(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(enterprise_webapp.SystemFeatureService, "is_webapp_auth_enabled", lambda: False)
    request = Mock()
    monkeypatch.setattr(EnterpriseRequest, "send_request", request)

    with app.test_request_context("/enterprise/webapp/permission"):
        result = unwrap(enterprise_webapp.AppConsoleWebAuthPermissionApi.get)(
            enterprise_webapp.AppConsoleWebAuthPermissionApi()
        )

    assert result == {"result": True}
    request.assert_not_called()
