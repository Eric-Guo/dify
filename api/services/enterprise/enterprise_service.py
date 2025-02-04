import logging
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

from services.enterprise.base import EnterpriseRequest

logger = logging.getLogger(__name__)


class WebAppSettings(BaseModel):
    access_mode: str = Field(
        description="Access mode for the web app. Can be 'public', 'private', 'private_all', 'sso_verified'",
        default="private",
        alias="accessMode",
    )


class EnterpriseService:
    @classmethod
    def get_info(cls):
        return EnterpriseRequest.send_request("GET", "/info")

    @classmethod
    def get_workspace_info(cls, tenant_id: str):
        return EnterpriseRequest.send_request("GET", f"/workspace/{tenant_id}/info")

    @classmethod
    def get_app_sso_settings_last_update_time(cls) -> datetime:
        data = EnterpriseRequest.send_request("GET", "/sso/app/last-update-time")
        if not data:
            raise ValueError("No data found.")
        try:
            # parse the UTC timestamp from the response
            return datetime.fromisoformat(data)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {data}") from e

    @classmethod
    def get_workspace_sso_settings_last_update_time(cls) -> datetime:
        data = EnterpriseRequest.send_request("GET", "/sso/workspace/last-update-time")
        if not data:
            raise ValueError("No data found.")
        try:
            # parse the UTC timestamp from the response
            return datetime.fromisoformat(data)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {data}") from e

    class WebAppAuth:
        @classmethod
        def is_user_allowed_to_access_webapp(cls, user_id: str, app_id: str):
            params = {"userId": user_id, "appId": app_id}
            try:
                data = EnterpriseRequest.send_request("GET", "/webapp/permission", params=params)
            except (ValueError, httpx.HTTPError) as exc:
                logger.warning("Failed to fetch enterprise webapp permission for %s: %s", app_id, exc)
                return False

            if not isinstance(data, dict):
                logger.warning("Unexpected enterprise webapp permission payload: %r", data)
                return False

            result = data.get("result")
            return bool(result)

        @classmethod
        def batch_is_user_allowed_to_access_webapps(cls, user_id: str, app_ids: list[str]):
            if not app_ids:
                return {}
            body = {"userId": user_id, "appIds": app_ids}
            try:
                data = EnterpriseRequest.send_request("POST", "/webapp/permission/batch", json=body)
            except (ValueError, httpx.HTTPError) as exc:
                logger.warning("Failed to fetch enterprise webapp permissions for %s: %s", app_ids, exc)
                return {}

            if not isinstance(data, dict):
                logger.warning("Unexpected enterprise webapp permissions payload: %r", data)
                return {}

            permissions: Any = data.get("permissions")
            if not isinstance(permissions, dict):
                logger.warning("Enterprise webapp permissions missing 'permissions': %r", data)
                return {}

            return permissions

        @classmethod
        def get_app_access_mode_by_id(cls, app_id: str) -> WebAppSettings:
            if not app_id:
                raise ValueError("app_id must be provided.")
            params = {"appId": app_id}
            try:
                data = EnterpriseRequest.send_request("GET", "/webapp/access-mode/id", params=params)
            except (ValueError, httpx.HTTPError) as exc:
                logger.warning("Failed to fetch enterprise webapp access mode for %s: %s", app_id, exc)
                return WebAppSettings()

            if not isinstance(data, dict):
                logger.warning("Unexpected enterprise access mode payload for %s: %r", app_id, data)
                return WebAppSettings()

            try:
                return WebAppSettings.model_validate(data)
            except ValueError as exc:
                logger.warning("Invalid enterprise access mode payload for %s: %r (%s)", app_id, data, exc)
                return WebAppSettings()

        @classmethod
        def batch_get_app_access_mode_by_id(cls, app_ids: list[str]) -> dict[str, WebAppSettings]:
            if not app_ids:
                return {}
            body = {"appIds": app_ids}
            try:
                data = EnterpriseRequest.send_request("POST", "/webapp/access-mode/batch/id", json=body)
            except (ValueError, httpx.HTTPError) as exc:
                logger.warning("Failed to fetch enterprise webapp access modes for %s: %s", app_ids, exc)
                return {}

            if not isinstance(data, dict):
                logger.warning("Unexpected enterprise access modes payload: %r", data)
                return {}

            access_modes: Any = data.get("accessModes")
            if not isinstance(access_modes, dict):
                logger.warning("Enterprise access modes missing 'accessModes': %r", data)
                return {}

            ret: dict[str, WebAppSettings] = {}
            for key, value in access_modes.items():
                curr = WebAppSettings()
                curr.access_mode = value
                ret[key] = curr

            return ret

        @classmethod
        def update_app_access_mode(
            cls,
            app_id: str,
            access_mode: str,
            subjects: list[dict] | None = None,
        ):
            if not app_id:
                raise ValueError("app_id must be provided.")
            if access_mode not in ["public", "private", "private_all", "sso_verified"]:
                raise ValueError(
                    "access_mode must be one of 'public', 'private', 'private_all', or 'sso_verified'"
                )

            data: dict = {"appId": app_id, "accessMode": access_mode}
            if subjects:
                data["subjects"] = subjects

            response = EnterpriseRequest.send_request("POST", "/webapp/access-mode", json=data)

            return response.get("result", False)

        @classmethod
        def cleanup_webapp(cls, app_id: str):
            if not app_id:
                raise ValueError("app_id must be provided.")

            body = {"appId": app_id}
            EnterpriseRequest.send_request("DELETE", "/webapp/clean", json=body)

        @classmethod
        def get_app_whitelist_subjects(cls, app_id: str) -> dict:
            if not app_id:
                raise ValueError("app_id must be provided.")
            params = {"appId": app_id}
            return EnterpriseRequest.send_request("GET", "/webapp/app/subjects", params=params)

        @classmethod
        def search_subjects(
            cls,
            keyword: str | None = None,
            group_id: str | None = None,
            results_per_page: int | None = None,
            page_number: int | None = None,
        ) -> dict:
            params: dict = {}
            if keyword:
                params["keyword"] = keyword
            if group_id:
                params["groupId"] = group_id
            if results_per_page is not None:
                params["resultsPerPage"] = results_per_page
            if page_number is not None:
                params["pageNumber"] = page_number
            return EnterpriseRequest.send_request("GET", "/webapp/app/subject/search", params=params)
