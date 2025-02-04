from flask_login import current_user
from flask_restx import Resource, reqparse

from controllers.console import api
from controllers.console.wraps import (
    account_initialization_required,
    enterprise_license_required,
    setup_required,
)
from libs.login import login_required
from services.app_service import AppService
from services.enterprise.enterprise_service import EnterpriseService
from services.feature_service import FeatureService


class AppAccessModeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("appId", type=str, required=True, location="json")
        parser.add_argument(
            "accessMode",
            type=str,
            required=True,
            choices=["public", "private", "private_all", "sso_verified"],
            location="json",
        )
        parser.add_argument("subjects", type=list, required=False, location="json")
        args = parser.parse_args()

        result = EnterpriseService.WebAppAuth.update_app_access_mode(
            app_id=args["appId"], access_mode=args["accessMode"], subjects=args.get("subjects")
        )

        return {"result": bool(result)}


class AppWhiteListSubjectsApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("appId", type=str, required=True, location="args")
        args = parser.parse_args()

        data = EnterpriseService.WebAppAuth.get_app_whitelist_subjects(app_id=args["appId"])
        return data


class AppSubjectSearchApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("keyword", type=str, required=False, location="args")
        parser.add_argument("groupId", type=str, required=False, location="args")
        parser.add_argument("resultsPerPage", type=int, required=False, location="args")
        parser.add_argument("pageNumber", type=int, required=False, location="args")
        args = parser.parse_args()

        data = EnterpriseService.WebAppAuth.search_subjects(
            keyword=args.get("keyword"),
            group_id=args.get("groupId"),
            results_per_page=args.get("resultsPerPage"),
            page_number=args.get("pageNumber"),
        )
        return data


class AppConsoleWebAuthPermissionApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    def get(self):
        # If webapp auth feature is disabled, allow access
        features = FeatureService.get_system_features()
        if not features.webapp_auth.enabled:
            return {"result": True}

        parser = reqparse.RequestParser()
        parser.add_argument("appId", type=str, required=True, location="args")
        args = parser.parse_args()

        app_id = args["appId"]
        app_code = AppService.get_app_code_by_id(app_id)

        user_id = current_user.id
        res = EnterpriseService.WebAppAuth.is_user_allowed_to_access_webapp(str(user_id), app_code)
        return {"result": bool(res)}


api.add_resource(AppAccessModeApi, "/enterprise/webapp/app/access-mode")
api.add_resource(AppWhiteListSubjectsApi, "/enterprise/webapp/app/subjects")
api.add_resource(AppSubjectSearchApi, "/enterprise/webapp/app/subject/search")
api.add_resource(AppConsoleWebAuthPermissionApi, "/enterprise/webapp/permission")


