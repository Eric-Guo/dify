from typing import Literal

from flask_login import current_user
from flask_restx import Resource
from pydantic import BaseModel, Field, JsonValue

from controllers.common.schema import query_params_from_model, register_response_schema_models, register_schema_models
from controllers.console import console_ns
from controllers.console.wraps import (
    account_initialization_required,
    enterprise_license_required,
    setup_required,
    validate_request,
)
from extensions.ext_database import db
from fields.base import ResponseModel
from libs.helper import dump_response
from libs.login import login_required
from services.app_service import AppService
from services.enterprise.enterprise_service import EnterpriseService
from services.system_feature_service import SystemFeatureService


class WebAppQuery(BaseModel):
    appId: str = Field(min_length=1)


class WebAppAccessModePayload(WebAppQuery):
    accessMode: Literal["public", "private", "private_all", "sso_verified"]
    subjects: list[dict[str, JsonValue]] | None = None


class WebAppSubjectQuery(BaseModel):
    keyword: str | None = None
    groupId: str | None = None
    resultsPerPage: int | None = Field(default=None, ge=1)
    pageNumber: int | None = Field(default=None, ge=1)


class WebAppResultResponse(ResponseModel):
    result: bool


register_schema_models(console_ns, WebAppQuery, WebAppAccessModePayload, WebAppSubjectQuery)
register_response_schema_models(console_ns, WebAppResultResponse)


@console_ns.route("/enterprise/webapp/app/access-mode")
class AppAccessModeApi(Resource):
    @console_ns.expect(console_ns.models[WebAppAccessModePayload.__name__])
    @console_ns.response(200, "Access mode updated", console_ns.models[WebAppResultResponse.__name__])
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def post(self):
        payload = validate_request(WebAppAccessModePayload)
        result = EnterpriseService.WebAppAuth.update_app_access_mode(
            app_id=payload.appId, access_mode=payload.accessMode, subjects=payload.subjects
        )
        return dump_response(WebAppResultResponse, {"result": bool(result)})


@console_ns.route("/enterprise/webapp/app/subjects")
class AppWhiteListSubjectsApi(Resource):
    @console_ns.doc(params=query_params_from_model(WebAppQuery))
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        query = validate_request(WebAppQuery)
        return EnterpriseService.WebAppAuth.get_app_whitelist_subjects(app_id=query.appId)


@console_ns.route("/enterprise/webapp/app/subject/search")
class AppSubjectSearchApi(Resource):
    @console_ns.doc(params=query_params_from_model(WebAppSubjectQuery))
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        query = validate_request(WebAppSubjectQuery)
        return EnterpriseService.WebAppAuth.search_subjects(
            keyword=query.keyword,
            group_id=query.groupId,
            results_per_page=query.resultsPerPage,
            page_number=query.pageNumber,
        )


@console_ns.route("/enterprise/webapp/permission")
class AppConsoleWebAuthPermissionApi(Resource):
    @console_ns.doc(params=query_params_from_model(WebAppQuery))
    @console_ns.response(200, "Webapp permission", console_ns.models[WebAppResultResponse.__name__])
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        if not SystemFeatureService.is_webapp_auth_enabled():
            return dump_response(WebAppResultResponse, {"result": True})

        query = validate_request(WebAppQuery)
        app_code = AppService.get_app_code_by_id(query.appId, session=db.session())
        result = EnterpriseService.WebAppAuth.is_user_allowed_to_access_webapp(str(current_user.id), app_code)
        return dump_response(WebAppResultResponse, {"result": bool(result)})
