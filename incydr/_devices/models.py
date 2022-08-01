from datetime import datetime
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from incydr._core.models import ResponseModel
from incydr._core.util import SortDirection


class SortKeys(str, Enum):
    NAME = "name"
    OS_HOSTNAME = "osHostname"
    OS = "os"
    LAST_CONNECTED = "lastConnected"


class Device(ResponseModel):
    device_id: Optional[str] = Field(
        allow_mutation=False,
        alias="deviceId",
        description="A globally unique ID (guid) for this device.",
    )
    legacy_device_id: Optional[str] = Field(
        allow_mutation=False,
        alias="legacyDeviceId",
        description="The device ID to use for older console-based APIs that require a device Id.",
    )
    name: Optional[str] = Field(None, description="Device name.")
    os_hostname: Optional[str] = Field(
        allow_mutation=False,
        alias="osHostname",
        description="Device Hostname according to the device's OS.",
    )
    status: Optional[str] = Field(
        allow_mutation=False,
        description="Device status. Values: Active, Deactivated, Blocked, Deauthorized (Active/Deactivated followed by optional Blocked and/or Deauthorized)",
    )
    active: Optional[bool] = Field(
        allow_mutation=False,
        description="True means the device will show up on reports, etc.",
    )
    blocked: Optional[bool] = Field(
        allow_mutation=False,
        description="True means device continues backing up, but restores and logins are disabled.",
    )
    alert_state: Optional[int] = Field(
        allow_mutation=False,
        alias="alertState",
        description="0=ok, 1=connection warning, 2=connection critical",
    )
    user_id: Optional[str] = Field(
        allow_mutation=False,
        alias="userId",
        description="A globally unique ID for this user.",
    )
    legacy_user_id: Optional[str] = Field(
        allow_mutation=False,
        alias="legacyUserId",
        description='The user ID to use for older console-based APIs that require a user Id.\r\nIf your endpoint domain starts with "console" instead of "api", use this Id for endpoints that require a userId.',
    )
    org_id: Optional[str] = Field(
        allow_mutation=False,
        alias="orgId",
        description="An ID for the Code42 organization of the user owning this device.",
    )
    legacy_org_id: Optional[str] = Field(
        allow_mutation=False,
        alias="legacyOrgId",
        description='The org ID to use for older console-based APIs that require an org Id.\r\nIf your endpoint domain starts with "console" instead of "api", use this Id for endpoints that require an orgId.',
    )
    org_guid: Optional[str] = Field(
        allow_mutation=False, alias="orgGuid", description="The globally unique org ID."
    )
    external_reference: Optional[str] = Field(
        allow_mutation=False,
        alias="externalReferenceInfo",
        description="Optional external reference information, such as a serial number, asset tag, employee ID, or help desk issue ID.",
    )
    notes: Optional[str] = Field(None, description="Optional descriptive information.")
    last_connected: Optional[datetime] = Field(
        allow_mutation=False,
        alias="lastConnected",
        description="The last day and time this device was connected to the server.",
    )
    os_name: Optional[str] = Field(
        allow_mutation=False,
        alias="osHostname",
        description="Operating system name. Values: Windows*, Mac OS X, Linux, Android, iOS, SunOS, etc",
    )
    os_version: Optional[str] = Field(
        allow_mutation=False,
        alias="osVersion",
        description="Operating system version. Values: 10.5.1, 6.2, etc",
    )
    os_arch: Optional[str] = Field(
        allow_mutation=False,
        alias="osArch",
        description="Hardware architecture. Values: i386, amd64, sparc, x86, etc",
    )
    address: Optional[str] = Field(
        allow_mutation=False,
        description="Internal IP address and port. Example: 192.168.42.1:4282",
    )
    remote_address: Optional[str] = Field(
        allow_mutation=False,
        alias="remoteAddress",
        description="External IP address and port. Example: 171.22.110.41:13958",
    )
    time_zone: Optional[str] = Field(
        allow_mutation=False,
        alias="timeZone",
        description="Examples: Australia/Canberra, Asia/Calcutta",
    )
    version: Optional[str] = Field(None, description="Device product display version.")
    build: Optional[int] = Field(
        allow_mutation=False,
        description="Device build version long number, will only be applicable to CP4/SP devices.",
    )
    creation_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="creationDate",
        description="Date and time this device was created.",
    )
    modification_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="modificationDate",
        description="Date and time this device was last modified.",
    )
    login_date: Optional[datetime] = Field(
        allow_mutation=False,
        alias="loginDate",
        description="Date and time this device was last logged in.",
    )

    class Config:
        validate_assignment = True


class DevicesPage(ResponseModel):
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
