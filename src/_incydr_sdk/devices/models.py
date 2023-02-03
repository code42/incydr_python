from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.devices import SortKeys


class Device(ResponseModel):
    """
    A model representing a device.

    **Fields**:

    * **device_id**: `str` - The globally unique ID (guid) for this device.
    * **legacy_device_id**: `str` - The device ID to use for older console-based APIs that require a device ID.
    * **name**: `str` - The device name.
    * **os_hostname**: `str` - The device hostname according to the device's OS.
    * **status**: `str` - The device status. One of [Active, Deactivated, Blocked, Deauthorized (Active/Deactivated followed by optional Blocked and/or Deauthorized).
    * **active**: `bool` - Whether or not the device is active. If true, the device will show up on reports, etc.
    * **blocked**: `bool` - Whether or not the device is blocked.  If true, restores and logins are disabled.
    * **alert_state**: `int` - The device's alert state. One of [0=ok, 1=connection warning, 2=connection critical].
    * **user_id**: `str` - The globally unique ID for this user.
    * **legacy_user_id**: `str` - The user ID to use for older console-based APIs that require a user ID.
    * **org_id**: `str` - An ID for the Code42 organization of the user owning this device.
    * **legacy_org_id**: `str` - The org ID to use for older console-based APIs that require an org ID.
    * **org_guid**: `str` - The globally unique org ID.  This is the org identifier that should be used for all org-related API actions.
    * **external_reference**: `str` - Optional external reference information, such as a serial number, asset tag, employee ID, or help desk issue ID.
    * **notes**: `str` - Optional descriptive information for the device.
    * **last_connected**: `datetime` - The last day and time this device was connected to the server.
    * **os_name**: `str` - The device's operating system name. Ex: Windows*, Mac OS X, Linux, Android, iOS, SunOS, etc.
    * **os_version**: `str` - The device's operating system version. Ex: 10.5.1, 6.2, etc.
    * **address: `str` - The device's internal IP address and port. Ex: 192.168.42.1:4282
    * **remote_address**: `str` - The device's external IP address and port. Example: 171.22.110.41:13958
    * **time_zone**: `str` - The device's time zone. Ex: Asia/Calcutta
    * **version**: `str` - The device product display version.
    * **build**: `int` - The device build version long number, will only be applicable to CP4/SP devices.
    * **creation_date**: `datetime` - The date and time this device was created.
    * **modification_date**: `datetime` - The date and time this device was last modified.
    * **login_date**: `datetime` - The date and time this device was last logged in.
    """

    device_id: Optional[str] = Field(
        alias="deviceId",
        description="A globally unique ID (guid) for this device.",
    )
    legacy_device_id: Optional[str] = Field(
        alias="legacyDeviceId",
        description="The device ID to use for older console-based APIs that require a device Id.",
    )
    name: Optional[str] = Field(None, description="Device name.")
    os_hostname: Optional[str] = Field(
        alias="osHostname",
        description="Device Hostname according to the device's OS.",
    )
    status: Optional[str] = Field(
        description="Device status. Values: Active, Deactivated, Blocked, Deauthorized (Active/Deactivated followed by optional Blocked and/or Deauthorized)",
    )
    active: Optional[bool] = Field(
        description="True means the device will show up on reports, etc.",
    )
    blocked: Optional[bool] = Field(
        description="True means device continues backing up, but restores and logins are disabled.",
    )
    alert_state: Optional[int] = Field(
        alias="alertState",
        description="0=ok, 1=connection warning, 2=connection critical",
    )
    user_id: Optional[str] = Field(
        alias="userId",
        description="A globally unique ID for this user.",
    )
    legacy_user_id: Optional[str] = Field(
        alias="legacyUserId",
        description='The user ID to use for older console-based APIs that require a user Id.\r\nIf your endpoint domain starts with "console" instead of "api", use this Id for endpoints that require a userId.',
    )
    org_id: Optional[str] = Field(
        alias="orgId",
        description="An ID for the Code42 organization of the user owning this device.",
    )
    legacy_org_id: Optional[str] = Field(
        alias="legacyOrgId",
        description='The org ID to use for older console-based APIs that require an org Id.\r\nIf your endpoint domain starts with "console" instead of "api", use this Id for endpoints that require an orgId.',
    )
    org_guid: Optional[str] = Field(
        alias="orgGuid", description="The globally unique org ID."
    )
    external_reference: Optional[str] = Field(
        alias="externalReferenceInfo",
        description="Optional external reference information, such as a serial number, asset tag, employee ID, or help desk issue ID.",
    )
    notes: Optional[str] = Field(None, description="Optional descriptive information.")
    last_connected: Optional[datetime] = Field(
        alias="lastConnected",
        description="The last day and time this device was connected to the server.",
    )
    os_name: Optional[str] = Field(
        alias="osHostname",
        description="Operating system name. Values: Windows*, Mac OS X, Linux, Android, iOS, SunOS, etc",
    )
    os_version: Optional[str] = Field(
        alias="osVersion",
        description="Operating system version. Values: 10.5.1, 6.2, etc",
    )
    os_arch: Optional[str] = Field(
        alias="osArch",
        description="Hardware architecture. Values: i386, amd64, sparc, x86, etc",
    )
    address: Optional[str] = Field(
        description="Internal IP address and port. Example: 192.168.42.1:4282",
    )
    remote_address: Optional[str] = Field(
        alias="remoteAddress",
        description="External IP address and port. Example: 171.22.110.41:13958",
    )
    time_zone: Optional[str] = Field(
        alias="timeZone",
        description="Examples: Australia/Canberra, Asia/Calcutta",
    )
    version: Optional[str] = Field(None, description="Device product display version.")
    build: Optional[int] = Field(
        description="Device build version long number, will only be applicable to CP4/SP devices.",
    )
    creation_date: Optional[datetime] = Field(
        alias="creationDate",
        description="Date and time this device was created.",
    )
    modification_date: Optional[datetime] = Field(
        alias="modificationDate",
        description="Date and time this device was last modified.",
    )
    login_date: Optional[datetime] = Field(
        alias="loginDate",
        description="Date and time this device was last logged in.",
    )


class DevicesPage(ResponseModel):
    """
    A model representing a page of `Device` objects.

    **Fields**:

    * **devices**: `List[Device]` - The list of `n` number of devices retrieved from the query, where `n=page_size`.
    * **total_count**: `int` - Total count of devices found by query.
    """

    total_count: Optional[int] = Field(
        alias="totalCount", description="The total number of devices"
    )
    devices: Optional[List[Device]] = Field(description="A list of devices")


class QueryDevicesRequest(BaseModel):
    active: Optional[bool]
    blocked: Optional[bool]
    page: Optional[int] = 1
    pageSize: Optional[int] = 100
    sortDirection: SortDirection = SortDirection.ASC
    sortKey: SortKeys = SortKeys.NAME

    class Config:
        use_enum_values = True
