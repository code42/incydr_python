from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import constr
from pydantic import Field

from incydr._core.models import ResponseModel
from incydr.enums.alert_rules import FileCategory
from incydr.enums.alert_rules import GroupingOperator
from incydr.enums.alert_rules import NotificationType
from incydr.enums.alert_rules import Severity
from incydr.enums.alert_rules import UsersToAlertOn


class WatchConfig(ResponseModel):
    public_via_link: bool = Field(
        None,
        description="Boolean indicating whether to alert on public via link shares.",
        example="FALSE",
        alias="publicViaLink",
    )
    outside_trusted_domains: Optional[bool] = Field(
        None,
        description="Boolean indicating whether to alert on outside trusted domains shares.",
        example="TRUE",
        alias="outsideTrustedDomains",
    )


class WatchConfigGoogleDrive(WatchConfig):
    public_on_the_web: bool = Field(
        None,
        description="Boolean indicating whether to alert on public on the web shares.",
        example="TRUE",
        alias="publicOnTheWeb",
    )


class FileBelongsTo(ResponseModel):
    users_to_alert_on: UsersToAlertOn = Field(
        None,
        description="Indicates setting of how to interact with user list.",
        alias="usersToAlertOn",
    )
    user_list: Optional[List[str]] = Field(
        None,
        description="List of users who's activity is specified as either watching or excluding from watching.",
        example=["user1", "user2"],
        alias="userList",
    )


class SyncedToCloudServiceAlertRules(ResponseModel):
    watch_box: bool = Field(
        None,
        description="Boolean indicating if we are watching for box cloud sync activity.",
        example="TRUE",
        alias="watchBox",
    )
    watch_box_drive: bool = Field(
        None,
        description="Boolean indicating if we are watching for box drive cloud sync activity.",
        example="FALSE",
        alias="watchBoxDrive",
    )
    watch_dropbox: bool = Field(
        None,
        description="Boolean indicating if we are watching for drop box cloud sync activity.",
        example="TRUE",
        alias="watchDropBox",
    )
    watch_google_backup_and_sync: bool = Field(
        None,
        description="Boolean indicating if we are watching for google backup and sync cloud sync activity.",
        example="FALSE",
        alias="watchGoogleBackupAndSync",
    )
    watch_apple_icloud: bool = Field(
        None,
        description="Boolean indicating if we are watching for apple iCloud sync activity.",
        example="TRUE",
        alias="watchAppleIcLoud",
    )
    watch_microsoft_one_drive: bool = Field(
        None,
        description="Boolean indicating if we are watching for microsoft one drive cloud sync activity.",
        example="TRUE",
        alias="watchMicrosoftOneDrive",
    )


class AssignedUsersList(ResponseModel):
    """
    A model representing a list of users assigned to a rule.

    **Fields**:

    * **users**: `List[AssignedUser]` - List of users to being watched in the rule.
    * **users_to_alert_on**: `UsersToAlertOn` - Indicates the setting for how the rule will interact with user list. Values include: "ALL_USERS",  "ALL_USERS_NOT_SPECIFIED", and "SPECIFIED_USERS"
    """

    users: Optional[List[AssignedUser]] = Field(
        None,
        description='List of users to being watched in the rule.\nNote that a userIdFromAuthority value of "Null UserIdFromAuthority.  These usernames must be edited in the web app."indicates that the user alias must be edited via the Code42 console or the Code42 CLI.',
    )
    users_to_alert_on: UsersToAlertOn = Field(None, alias="usersToAlertOn")


# TODO - suggestions for what to call this model

class AssignedUser(ResponseModel):
    """
    A model representing a user assigned to a rule.

    **Fields**:

    * **user_id_from_authority**: `str` - A unique Code42 user ID.
    * **user_alias_list**: `List[str]` - List of user aliases associated with the user.
    """

    user_id_from_authority: str = Field(
        None,
        description="User ID from authority.",
        example="userIdFromAuthority",
        alias="userIdFromAuthority",
    )
    user_alias_list: List[str] = Field(
        None,
        description="List of user aliases corresponding to the user ID from the authority.",
        example=["userAlias1", "userAlias2"],
        alias="userAliasList",
    )


class NotificationInfo(ResponseModel):
    notification_type: NotificationType = Field(
        None, description="Type of notification.", alias="notificationType"
    )
    notification_address: Optional[str] = Field(
        None,
        description="Address notifications are configured to send to.",
        example="myUsername@company.com",
        alias="notificationAddress",
    )


class FileCategoryWatch(ResponseModel):
    watch_all_files: bool = Field(
        None,
        description="Boolean indicating if rule is watching all file categories.",
        example="FALSE",
        alias="watchAllFiles",
    )
    file_category_list: Optional[List[FileCategory]] = Field(
        None, description="List of file categories to watch.", alias="fileCategoryList"
    )


class FileInfo(ResponseModel):
    file_count_greater_than: Optional[int] = Field(
        None,
        description="Number of files exfiltrated within time window for alert to trigger.",
        example="15",
    )
    total_size_greater_than_in_bytes: Optional[int] = Field(
        None,
        description="Size of total files exfiltrated within time window for alert to trigger.",
        example="5000",
        alias="totalSizeGreaterThanInBytes",
    )
    operator: Optional[GroupingOperator] = Field(
        None, description="Operator to use to combine size and count threshold."
    )


class FileActivity(ResponseModel):
    synced_to_cloud_service: Optional[SyncedToCloudServiceAlertRules] = Field(
        None,
        description="Cloud services to watch for alerts.",
        alias="syncedToCloudService",
    )
    uploaded_on_removable_media: bool = Field(
        None,
        description="Boolean indicating if we are watching removable media uploads.",
        example="TRUE",
        alias="uploadedOnRemovableMedia",
    )
    read_by_browser_or_other: bool = Field(
        None,
        description="Boolean indicating if we are watching browser read activity.",
        example="FALSE",
        alias="readByBrowserOrOther",
    )


class NotificationConfig(ResponseModel):
    enabled: bool = Field(
        None,
        description="Boolean indicating if the notifications are turned on.",
        example="TRUE",
    )
    notification_info: Optional[List[NotificationInfo]] = Field(
        None,
        description="Config information for notifications.",
        alias="notificationInfo",
    )


class RuleDetails(ResponseModel):
    id: Optional[str] = Field(
        None, description="Unique ID of the rule.", example="RuleId"
    )
    created_at: datetime = Field(
        None,
        description="The timestamp when the rule was created.",
        example="2020-02-18T01:00:45.006683Z",
        alias="createdAt",
    )
    created_by: Optional[str] = Field(
        None,
        description="Username of the individual who created the rule.",
        example="UserWhoCreatedTheRule",
        alias="createdBy",
    )
    modified_at: datetime = Field(
        None,
        description="Timestamp of when the rule was last modified.",
        example="2020-02-19T01:57:45.006683Z",
        alias="modifiedAt",
    )
    modified_by: Optional[str] = Field(
        None,
        description="Username of the individual who last modified the rule.",
        example="UserWhoMostRecentlyModifiedTheRule",
        alias="modifiedBy",
    )
    is_system: bool = Field(
        None,
        description="Boolean indicator of if the rule is a system rule.",
        example="FALSE",
        alias="isSystem",
    )
    tenant_id: constr(max_length=100) = Field(
        None,
        description="The unique identifier representing the tenant.",
        example="MyExampleTenant",
        alias="tenantId",
    )
    name: Optional[str] = Field(
        None,
        description="The name of the rule.",
        example="Removable Media Exfiltration Rule",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the rule.",
        example="Alert me on all removable media exfiltration.",
    )
    severity: Optional[Severity] = Field(
        None, description="Indicates severity of the rule."
    )
    is_enabled: bool = Field(
        None,
        description="Boolean indicating if the rule is currently enabled.",
        example="TRUE",
        alias="isEnabled",
    )
    file_belongs_to: Optional[FileBelongsTo] = Field(None, alias="fileBelongsTo")
    notification_config: Optional[NotificationConfig] = Field(
        None, alias="notificationConfig"
    )
    file_category_watch: Optional[FileCategoryWatch] = Field(
        None, alias="fileCategoryWatch"
    )
    rule_source: Optional[str] = Field(
        None,
        description="Indicates source of rule creation.  Either alerting or lens application name.",
        example="alerting",
        alias="ruleSource",
    )

class FileTypeMismatchRuleDetails(RuleDetails):
    """
    A model representing the details of any exfiltration rule.

    **Fields**:
    '
    * **id**: `id` - Unique ID of the rule.
    * **created_at**: `datetime` - Timestamp of when the rule was created.
    * **created_by**: `datetime` - Username of the individual who created the rule.
    * **modified_at**: `datetime` - Timestamp of when the rule was last modified.
    * **modified_by**: `str` - Username of the individual who last modified the rule.
    * **is_system**: `bool` - Boolean indicator of if the rule is a system rule.
    * **tenant_id**: `str` - Tenant ID.
    * **name**: `str` - Name of the rule.
    * **description**: `str` - Description of the rule.
    * **severity**: `Severity` - Severity of the rule. `HIGH`, `MEDIUM` or `LOW`.
    * **is_enabled**: `bool` - Boolean indicating if the rule is currently enabled.
    * **file_belongs_to**: `FileBelongsTo` - User list configuration.
    * **notification_config**: `NotificationConfig` - Notification configuration.
    * **file_category_watch**: `FileCategoryWatch` - File category watch configuration.
    * **rule_source**: `str` - Indicates source of rule creation.  Either alerting or lens application name.
    """
    pass

class EndpointExfiltrationRuleDetails(RuleDetails):
    """
    A model representing a the details of a file name rule.

    **Fields**:

    * **id**: `id` - Unique ID of the rule.
    * **created_at**: `datetime` - Timestamp of when the rule was created.
    * **created_by**: `datetime` - Username of the individual who created the rule.
    * **modified_at**: `datetime` - Timestamp of when the rule was last modified.
    * **modified_by**: `str` - Username of the individual who last modified the rule.
    * **is_system**: `bool` - Boolean indicator of if the rule is a system rule.
    * **tenant_id**: `str` - Tenant ID.
    * **name**: `str` - Name of the rule.
    * **description**: `str` - Description of the rule.
    * **severity**: `Severity` - Severity of the rule. `HIGH`, `MEDIUM` or `LOW`.
    * **is_enabled**: `bool` - Boolean indicating if the rule is currently enabled.
    * **file_belongs_to**: `FileBelongsTo` - User list configuration.
    * **notification_config**: `NotificationConfig` - Notification configuration.
    * **file_category_watch**: `FileCategoryWatch` - File category watch configuration.
    * **rule_source**: `str` - Indicates source of rule creation.  Either alerting or lens application name.
    * **file_size_and_count**: `FileInfo` - File size and count watch configuration.
    * **file_activity_is**: `FileActivity` - Type of file activity the rule is watching.
    * **time_window**: `int` - Length of the period for the activity to aggregate to hit the specified file size and count thresholds.
    """

    file_size_and_count: Optional[FileInfo] = Field(
        None,
        description="File size and count watch configuration.",
        alias="fileSizeAndCount",
    )
    file_activity_is: Optional[FileActivity] = Field(
        None,
        description="Type of file activity the rule is watching.",
        alias="fileActivityIs",
    )
    time_window: int = Field(
        None,
        description="How long of a period for the activity to aggregate to hit the specified file size and count thresholds.",
        example="60",
        alias="timeWindow",
    )


class FileNameRuleDetails(RuleDetails):
    """
    A model representing a the details of a file name rule.

    **Fields**:

    * **id**: `id` - Unique ID of the rule.
    * **created_at**: `datetime` - Timestamp of when the rule was created.
    * **created_by**: `datetime` - Username of the individual who created the rule.
    * **modified_at**: `datetime` - Timestamp of when the rule was last modified.
    * **modified_by**: `str` - Username of the individual who last modified the rule.
    * **is_system**: `bool` - Boolean indicator of if the rule is a system rule.
    * **tenant_id**: `str` - Tenant ID.
    * **name**: `str` - Name of the rule.
    * **description**: `str` - Description of the rule.
    * **severity**: `Severity` - Severity of the rule. `HIGH`, `MEDIUM` or `LOW`.
    * **is_enabled**: `bool` - Boolean indicating if the rule is currently enabled.
    * **file_belongs_to**: `FileBelongsTo` - User list configuration.
    * **notification_config**: `NotificationConfig` - Notification configuration.
    * **file_category_watch**: `FileCategoryWatch` - File category watch configuration.
    * **rule_source**: `str` - Indicates source of rule creation.  Either alerting or lens application name.
    * **file_name_patterns**: `List[str]` - List of file name patterns being watched by the rule.
    """

    file_name_patterns: Optional[List[str]] = Field(
        None,
        description="List of file name patterns being watched by the rule.",
        example=["Q?ProductPlan.*", "*.cs"],
        alias="fileNamePatterns",
    )


class CloudSharePermissionsRuleDetails(RuleDetails):
    """
    A model representing a the details of a cloud share permissions rule.

    **Fields**:

    * **id**: `id` - Unique ID of the rule.
    * **created_at**: `datetime` - Timestamp of when the rule was created.
    * **created_by**: `datetime` - Username of the individual who created the rule.
    * **modified_at**: `datetime` - Timestamp of when the rule was last modified.
    * **modified_by**: `str` - Username of the individual who last modified the rule.
    * **is_system**: `bool` - Boolean indicator of if the rule is a system rule.
    * **tenant_id**: `str` - Tenant ID.
    * **name**: `str` - Name of the rule.
    * **description**: `str` - Description of the rule.
    * **severity**: `Severity` - Severity of the rule. `HIGH`, `MEDIUM` or `LOW`.
    * **is_enabled**: `bool` - Boolean indicating if the rule is currently enabled.
    * **file_belongs_to**: `FileBelongsTo` - User list configuration.
    * **notification_config**: `NotificationConfig` - Notification configuration.
    * **file_category_watch**: `FileCategoryWatch` - File category watch configuration.
    * **rule_source**: `str` - Indicates source of rule creation.  Either alerting or lens application name.
    * **watch_google_drive**: `WatchConfigGoogleDrive` - Watch configuration for Google Drive.
    * **watch_microsoft_one_drive**: `WatchConfig` - Watch configuration for Microsoft OneDrive.
    * **watch_box**: `WatchConfig` - Watch configuration for Box.
    """

    watch_google_drive: Optional[WatchConfigGoogleDrive] = Field(
        None, description="Watch configuration for google.", alias="watchGoogleDrive"
    )
    watch_microsoft_one_drive: Optional[WatchConfig] = Field(
        None,
        description="Watch configuration for microsoft one drive.",
        alias="watchMicrosoftOneDrive",
    )
    watch_box: Optional[WatchConfig] = Field(
        None, description="Watch configuration for box.", alias="watchBox"
    )


class EndpointExfiltrationRuleDetailsList(ResponseModel):
    """
    A model representing a page of `EndpointExfiltrationRuleDetails` objects.

    **Fields**:

    * **rules**: `List[EndpointExfiltrationRuleDetails]` - The list of details about a set of endpoint exfiltration rules.
    """

    rules: Optional[List[EndpointExfiltrationRuleDetails]] = Field(
        None, description="List of rule details returned from the query."
    )


class FileTypeMismatchRuleDetailsList(ResponseModel):
    """
    A model representing a page of `FileTypeMismatchRuleDetailsList` objects.

    **Fields**:

    * **rules**: `List[FileTypeMismatchRuleDetailsList]` - The list of details about a set of file type mismatch rules.
    """

    rules: Optional[List[FileTypeMismatchRuleDetails]] = Field(
        None, description="List of rule details returned from the query."
    )


class FileNameRuleDetailsList(ResponseModel):
    """
    A model representing a page of `FileNameRuleDetailsList` objects.

    **Fields**:

    * **rules**: `List[FileNameRuleDetailsList]` - The list of details about a set of file name rules.
    """

    rules: Optional[List[FileNameRuleDetails]] = Field(
        None, description="List of rule details returned from the query."
    )


class CloudSharePermissionsRuleDetailsList(ResponseModel):
    """
    A model representing a page of `CloudSharePermissionsRuleDetails` objects.

    **Fields**:

    * **rules**: `List[CloudSharePermissionsRuleDetails]` - The list of details about a set of cloud share permissions rules.
    """

    rules: Optional[List[CloudSharePermissionsRuleDetails]] = Field(
        None, description="List of rule details returned from the query."
    )
