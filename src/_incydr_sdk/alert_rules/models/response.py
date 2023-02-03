from __future__ import annotations

from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums.alerts import MessagingMethod


class RuleUser(ResponseModel):
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
    aliases: List[str] = Field(
        None,
        description="List of user aliases corresponding to the user ID from the authority.",
        example=["userAlias1", "userAlias2"],
    )


class RuleUsersList(ResponseModel):
    """
    A model representing a list of users associated with a rule, as well as the rule's configuration mode to `INCLUDE` or `EXCLUDE` those users.

    **Fields**:

    * **id**: `str` - Unique ID of the rule.
    * **users**: `List[RuleUser]` - A list of users in the rule's username filter.
    * **mode**: `str` - Indicates how to filter on the user list. Specifies whether to `INCLUDE` or `EXCLUDE` the listed users from the rule.
    """

    id: Optional[str] = Field(
        None,
        description="The id of the rule.",
        example="669bb117-d07a-4bd9-9f19-f1d85102cf55",
    )
    users: Optional[List[RuleUser]] = Field(
        None, description="A list of users in the rule's username filter."
    )
    mode: Optional[str] = Field(
        None,
        description="Indicates how to filter on the user list. INCLUDE or EXCLUDE.",
        table=lambda x: "INCLUDE" if x == "0" else "EXCLUDE",
    )


class CloudSharingDetails(Model):
    observe_all: bool = Field(
        None,
        description="Indicates whether we are watching the cloud sharing connector or not.",
        example=True,
        alias="observeAll",
    )
    public_link_share: bool = Field(None, alias="publicLinkShare")
    direct_share: bool = Field(None, alias="directShare")


class DownloadVector(Model):
    observe_all: Optional[bool] = Field(None, alias="observeAll")
    salesforce: Optional[bool] = None
    box: Optional[bool] = None
    google_drive: Optional[bool] = Field(None, alias="googleDrive")
    microsoft_one_drive: Optional[bool] = Field(None, alias="microsoftOneDrive")
    criteria_order: int = Field(None, alias="criteriaOrder")


class EmailVector(Model):
    observe_all: Optional[bool] = Field(None, alias="observeAll")
    gmail: Optional[bool] = None
    microsoft365: Optional[bool] = None
    criteria_order: int = Field(None, alias="criteriaOrder")


class FileUploadCategory(Model):
    observe_all: bool = Field(
        None,
        description="Indicates whether we are watching all of the destinations in the category.",
        example=True,
        alias="observeAll",
    )
    destinations: Optional[List[str]] = Field(
        None,
        description="A list of specific destinations to watch within the category.",
        example=[],
    )


class AdvancedSettings(Model):
    observe_uncategorized: bool = Field(None, alias="observeUncategorized")


class RemovableMediaVector(Model):
    is_enabled: bool = Field(
        None,
        description="Indicates whether to watch removable media destinations or not.",
        example=True,
        alias="isEnabled",
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class FileCategoryFilter(Model):
    categories: Optional[List[str]] = Field(
        None,
        description="List of file categories to alert on.",
        example=["Archive", "Pdf", "SourceCode"],
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class FileNameFilter(Model):
    patterns: Optional[List[str]] = Field(
        None,
        description="List of file name patterns to alert on.",
        example=["*.cs", "*.sh"],
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class FileTypeMismatchFilter(Model):
    is_enabled: bool = Field(
        None,
        description="Indicates whether or not to alert on file type mismatches only.",
        example=True,
        alias="isEnabled",
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class RiskIndicatorFilter(Model):
    categories: Optional[List[str]] = None
    indicators: Optional[List[str]] = None
    criteria_order: int = Field(None, alias="criteriaOrder")


class RiskSeverityFilter(Model):
    low: bool
    moderate: bool
    high: bool
    critical: bool
    criteria_order: int = Field(None, alias="criteriaOrder")


class Watchlist(Model):
    id: Optional[str] = None


class NotificationContact(Model):
    is_enabled: bool = Field(
        None,
        description="Indicates whether the notifications for this contact are enabled.",
        example=True,
        alias="isEnabled",
    )
    type: Optional[str] = Field(
        None, description="Type of notification.", example="EMAIL"
    )
    address: Optional[str] = Field(
        None,
        description="Address notifications are configured to send to.",
        example="myUsername@company.com",
    )


class CloudSharingVector(Model):
    observe_all: Optional[bool] = Field(
        None,
        description="Indicates whether to watch all cloud sharing connectors.",
        example=False,
        alias="observeAll",
    )
    box: Optional[CloudSharingDetails] = Field(
        None,
        description="Configuration for specific cloud sharing monitoring using the Box connector.",
    )
    google_drive: Optional[CloudSharingDetails] = Field(
        None,
        description="Configuration for specific cloud sharing monitoring using the Google Drive connector.",
        alias="googleDrive",
    )
    one_drive: Optional[CloudSharingDetails] = Field(
        None,
        description="Configuration for specific cloud sharing monitoring using the Microsoft OneDrive connector.",
        alias="oneDrive",
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class FileUploadVector(Model):
    cloud_storage: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which cloud storage destinations to monitor.",
        alias="cloudStorage",
    )
    email: Optional[FileUploadCategory] = Field(
        None, description="Configuration for which email destinations to monitor."
    )
    file_conversion_tool: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which file conversion tool destinations to monitor.",
        alias="fileConversionTool",
    )
    messaging: Optional[FileUploadCategory] = Field(
        None, description="Configuration for which messaging destinations to monitor."
    )
    pdf_manager: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which PDF manager destinations to monitor.",
        alias="pdfManager",
    )
    productivity_tool: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which productivity tool destinations to monitor.",
        alias="productivityTool",
    )
    social_media: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which social media destinations to monitor.",
        alias="socialMedia",
    )
    source_code_repository: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which source code repository destinations to monitor.",
        alias="sourceCodeRepository",
    )
    web_hosting: Optional[FileUploadCategory] = Field(
        None,
        description="Configuration for which web hosting destinations to monitor.",
        alias="webHosting",
    )
    advanced_settings: Optional[AdvancedSettings] = Field(
        None,
        description="Advanced settings around alerting off of unknown destinations.",
        alias="advancedSettings",
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class FileVolumeFilter(Model):
    count_greater_than: int = Field(
        None,
        description="File count threshold that must be exceeded to trigger an alert.",
        example=125,
        alias="countGreaterThan",
    )
    operator: Optional[str] = Field(
        None,
        description="Operator to use to combine size and count threshold. AND or OR.",
    )
    size_greater_than_in_bytes: int = Field(
        None,
        description="File size threshold that must be exceeded to trigger an alert.",
        example=1024,
        alias="sizeGreaterThanInBytes",
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class UsernameFilter(Model):
    mode: Optional[str] = Field(
        None, description="Indicates how to filter on the user list. INCLUDE or EXCLUDE"
    )
    usernames: Optional[List[str]] = Field(
        None,
        description="List of usernames.  Will either alert only on these users or on any user not in list.",
        example=["myUsername@company.com", "anotherUsername@company.com"],
    )
    criteria_order: int = Field(
        None,
        description="Order in which this vector was added to the rule.",
        example=3,
        alias="criteriaOrder",
    )


class WatchlistFilter(Model):
    watchlists: Optional[List[Watchlist]] = None
    criteria_order: int = Field(None, alias="criteriaOrder")


class NotificationSettings(Model):
    is_enabled: bool = Field(
        None,
        description="Indicates whether notifications are enabled.",
        example=True,
        alias="isEnabled",
    )
    contacts: Optional[List[NotificationContact]] = Field(
        None, description="List of notifications configured."
    )


class RuleVectors(Model):
    cloud_sharing: Optional[CloudSharingVector] = Field(
        None,
        description="Configuration for cloud sharing vectors to monitor.",
        alias="cloudSharing",
    )
    download: Optional[DownloadVector] = None
    email: Optional[EmailVector] = None
    file_upload: Optional[FileUploadVector] = Field(
        None,
        description="Configuration for what file upload vectors to monitor.",
        alias="fileUpload",
    )
    removable_media: Optional[RemovableMediaVector] = Field(
        None,
        description="Configuration for what removable media vectors to monitor.",
        alias="removableMedia",
    )


class RuleFilters(Model):
    file_category: Optional[FileCategoryFilter] = Field(
        None,
        description="Configuration for what file categories to monitor.",
        alias="fileCategory",
    )
    file_name: Optional[FileNameFilter] = Field(
        None,
        description="Configuration for what file names to monitor.",
        alias="fileName",
    )
    file_type_mismatch: Optional[FileTypeMismatchFilter] = Field(
        None,
        description="Configuration for whether to only alert on file mismatches.",
        alias="fileTypeMismatch",
    )
    file_volume: Optional[FileVolumeFilter] = Field(
        None,
        description="Activity thresholds to exceed for an alert to be generated.",
        alias="fileVolume",
    )
    risk_indicator: Optional[RiskIndicatorFilter] = Field(None, alias="riskIndicator")
    risk_severity: Optional[RiskSeverityFilter] = Field(None, alias="riskSeverity")
    username: Optional[UsernameFilter] = Field(
        None, description="Configuration for which users to monitor."
    )
    watchlist: Optional[WatchlistFilter] = None


class EducationSettings(Model):
    lesson_id: Optional[str] = Field(
        None, description="Instructor lesson ID.", alias="lessonId"
    )
    messaging_method: Optional[MessagingMethod] = Field(
        None, description="Messaging method.", alias="messagingMethod"
    )


class RuleDetails(ResponseModel):
    """
    A model representing the details of an alert rule.

    **Fields**:

    * **name**: `str` - Unique name of the rule.
    * **description**: `str` - Description of the rule.
    * **severity**: `str` - [Deprecated field] Indicates severity of rule.
    * **is_enabled**: `bool` - Indicates if the rule is currently enabled.
    * **source**: `str` - [Deprecated field] Indicates source of rule creation.
    * **notifications**: `NotificationSettings` - Notification configuration settings for this rule.
    * **education**: `EducationSettings` - Instructor settings for a rule.
    * **vectors**: `RuleVectors` - The exfiltration vectors to be watched.
    * **filters**: `RuleFilters` - The filters to limit the scope of activity to alert on.
    * **id**: `id` - Unique ID of the rule.
    * **created_at**: `datetime` - Timestamp of when the rule was created.
    * **created_by**: `str` - Individual or service who who created the rule.
    * **modified_at**: `datetime` - Timestamp of when the rule was last modified.
    * **modified_by**: `str` - Individual or service who who last modified the rule.
    * **is_system_rule**: `bool` - Boolean indicator of whether or not the rule is connected to a lens.
    """

    name: Optional[str] = Field(
        None,
        description="Unique name of the rule.",
        example="Suspicious File Mismatch Rule",
    )
    description: Optional[str] = Field(
        None,
        description="Description of the rule.",
        example="A rule created to trigger alerts on suspicious file mismatch exfiltration",
    )
    severity: Optional[str] = Field(
        None, description="[Deprecated field] Indicates severity of rule.", example=""
    )
    is_enabled: Optional[bool] = Field(
        None,
        description="Indicates whether the rule is enabled or not.",
        example=True,
        alias="isEnabled",
    )
    source: Optional[str] = Field(
        None,
        description="[Deprecated field] Indicates source of rule creation.",
        example="",
    )
    notifications: Optional[NotificationSettings] = Field(
        None, description="Notifications configuration settings for this rule."
    )
    education: Optional[EducationSettings] = Field(
        None, description="Education settings for a rule."
    )
    vectors: Optional[RuleVectors] = Field(
        None, description="The exfiltration vectors to be watched."
    )
    filters: Optional[RuleFilters] = Field(
        None, description="The filters to limit the scope of activity to alert on."
    )
    id: Optional[str] = Field(
        None,
        description="Unique identifier of the rule.",
        example="ecec5037-aedc-4cf9-aad3-57dcafe1f204",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Time when the rule was created.",
        example="2022-10-04T17:53:26.4534999Z",
        alias="createdAt",
    )
    created_by: Optional[str] = Field(
        None,
        description="Individual or service who created the rule.",
        example="my-username@company.com",
        alias="createdBy",
    )
    modified_at: Optional[datetime] = Field(
        None,
        description="Time when the rule was last modified.",
        example="2022-10-04T17:53:26.453532Z",
        alias="modifiedAt",
    )
    modified_by: Optional[str] = Field(
        None,
        description="Individual or service who last modified the rule.",
        example="my-username@company.com",
        alias="modifiedBy",
    )
    is_system_rule: Optional[bool] = Field(
        None,
        description="Boolean indicator of whether or not the rule is connected to a lens.",
        example=True,
        alias="isSystemRule",
    )
