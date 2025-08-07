from datetime import datetime
from typing import List
from typing import Optional
from typing import Union

from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums.file_events import ReportType


class UserJustification(Model):
    reason: Optional[str] = Field(
        None, title="User-select justification for temporarily allowing this action."
    )
    text: Optional[str] = Field(
        None,
        title="User-select justification for temporarily allowing this action. Only applies when reason is 'Other'.",
    )


class ResponseControls(Model):
    preventative_control: Optional[str] = Field(
        None,
        alias="preventativeControl",
        examples=["BLOCKED"],
        title="The preventative action applied to this event",
    )
    user_justification: Optional[UserJustification] = Field(
        None, alias="userJustification"
    )


class AcquiredFromGit(Model):
    repository_email: Optional[str] = Field(
        None,
        alias="repositoryEmail",
        title="The email address specified by the user who performed the Git event. This is a user-defined value and may differ from the credentials used to sign in to Git.",
    )
    repository_uri: Optional[str] = Field(
        None,
        alias="repositoryUri",
        title="Uniform Resource Identifier (URI) for the Git repository.",
    )
    repository_user: Optional[str] = Field(
        None,
        alias="repositoryUser",
        title="The username specified by the user who performed the Git event. This is a user-defined value and may differ from the credentials used to sign in to Git.",
    )


class AcquiredFromSourceUser(Model):
    email: Optional[List[str]] = Field(
        None,
        examples=[["first.last@example.com", "first_last_example_com"]],
        title="For endpoint events where a file in cloud storage is synced to a device, the email address of the user logged in to the cloud storage provider.",
    )


class UntrustedValues(Model):
    account_names: List[str] = Field(
        None,
        alias="accountNames",
        title="Account names that do not match an entry in your list of Trusted activity. Values are obtained from the account name metadata for the event. Only applies to event types that are evaluated for trust.",
    )
    domains: List[str] = Field(
        None,
        title="Domains that do not match an entry in your list of Trusted activity. Values are obtained from the domain section of related metadata for the event. Only applies to event types that are evaluated for trust.",
    )
    git_repository_uris: List[str] = Field(
        None,
        alias="gitRepositoryUris",
        title="Git URIs that do not match an entry in your list of Trusted activity. Values are obtained from the Git URI metadata for the event. Only applies to event types that are evaluated for trust.",
    )
    slack_workspaces: List[str] = Field(
        None,
        alias="slackWorkspaces",
        title="Slack workspaces that do not match an entry in your list of Trusted activity. Values are obtained from the Slack metadata for the event. Only applies to event types that are evaluated for trust.",
    )
    url_paths: List[str] = Field(
        None,
        alias="urlPaths",
        title="URL paths that do not match an entry in your list of Trusted activity. Values are obtained from the URL metadata for the event. Only applies to event types that are evaluated for trust.",
    )


class DestinationEmail(Model):
    recipients: Optional[List[str]] = Field(
        None,
        description="The email addresses of those who received the email. Includes the To, Cc, and Bcc recipients.",
        examples=[["cody@example.com", "theboss@example.com"]],
    )
    subject: Optional[str] = Field(
        None,
        description="The subject of the email message.",
        examples=["Important business documents"],
    )


class DestinationUser(Model):
    email: Optional[List[str]] = Field(
        None,
        description="For endpoint events where a file in cloud storage is synced to a device, the email address of the user logged in to the cloud storage provider. For cloud events, the email addresses of users added as sharing recipients. In some case, OneDrive events may return multiple values, but this is often the same username formatted in different ways.",
        examples=[["first.last@example.com", "first_last_example_com"]],
    )


class FileClassification(Model):
    value: Optional[str] = Field(
        None,
        description="The classification value applied to the file.",
        examples=["Classified"],
    )
    vendor: Optional[str] = Field(
        None,
        description="The name of the vendor that classified the file.",
        examples=["MICROSOFT INFORMATION PROTECTION"],
    )


class Hash(Model):
    md5: Optional[str] = Field(
        None,
        description="The MD5 hash of the file contents.",
        examples=["a162591e78eb2c816a28907d3ac020f9"],
    )
    md5_error: Optional[str] = Field(
        None, alias="md5Error", description="Reason the MD5 hash is unavailable."
    )
    sha256: Optional[str] = Field(
        None,
        description="The SHA-256 hash of the file contents.",
        examples=["ded96d69c63754472efc4aa86fed68d4e17784b38089851cfa84e699e48b4155"],
    )
    sha256_error: Optional[str] = Field(
        None, alias="sha256Error", description="Reason the SHA-256 hash is unavailable."
    )


class Extension(Model):
    browser: Optional[str] = Field(
        None, title="The web browser in which the event occurred."
    )
    version: Optional[str] = Field(
        None,
        title="The version of the Code42 Incydr extension installed when the event occurred.",
    )
    logged_in_user: Optional[str] = Field(
        None,
        alias="loggedInUser",
        title="The user signed in to the active tab where the event occurred. For example, the user signed in to Gmail. This may differ from the user account signed in to the browser itself.",
    )


class Process(Model):
    executable: Optional[str] = Field(
        None,
        description="The name of the process that accessed the file, as reported by the device’s operating system. Depending on your Code42 product plan, this value may be null for some event types.",
        examples=["bash"],
    )
    owner: Optional[str] = Field(
        None,
        description="The username of the process owner, as reported by the device’s operating system. Depending on your Code42 product plan, this value may be null for some event types.",
        examples=["root"],
    )
    extension: Optional[Extension] = None


class RemovableMedia(Model):
    bus_type: Optional[str] = Field(
        None,
        alias="busType",
        description="For events detected on removable media, indicates the communication system used to transfer data between the host and the removable device.",
        examples=["USB 3.0 Bus"],
    )
    capacity: Optional[int] = Field(
        None,
        description="For events detected on removable media, the capacity of the removable device in bytes.",
        examples=[15631122432],
    )
    media_name: Optional[str] = Field(
        None,
        alias="mediaName",
        description="For events detected on removable media, the media name of the device, as reported by the vendor/device. This is usually very similar to the productName, but can vary based on the type of device. For example, if the device is a hard drive in a USB enclosure, this may be the combination of the drive model and the enclosure model.\nThis value is not provided by all devices, so it may be null in some cases.",
        examples=["Cruzer Blade"],
    )
    name: Optional[str] = Field(
        None,
        description="For events detected on removable media, the name of the removable device.",
        examples=["JUMPDRIVE"],
    )
    partition_id: Optional[List[str]] = Field(
        None,
        alias="partitionId",
        description="For events detected on removable media, a unique identifier assigned to the volume/partition when it was formatted. Windows devices refer to this as the VolumeGuid. On Mac devices, this is the Disk / Partition UUID, which appears when running the Terminal command diskUtil info.",
        examples=[["disk0s2", "disk0s3"]],
    )
    serial_number: Optional[str] = Field(
        None,
        alias="serialNumber",
        description="For events detected on removable media, the serial number of the removable device.",
        examples=["4C531001550407108465"],
    )
    vendor: Optional[str] = Field(
        None,
        description="For events detected on removable media, the vendor of the removable device.",
        examples=["SanDisk"],
    )
    volume_name: Optional[List[str]] = Field(
        None,
        alias="volumeName",
        description='For events detected on removable media, the name assigned to the volume when it was formatted, as reported by the device\'s operating system. This is also frequently called the "partition" name.',
        examples=[["MY_FILES"]],
    )


class Report(Model):
    count: Optional[int] = Field(
        None,
        description="The total number of rows returned in the report.",
        examples=[20],
    )
    description: Optional[str] = Field(
        None,
        description="The description of the report.",
        examples=["Top 20 accounts based on annual revenue"],
    )
    headers: Optional[List[str]] = Field(
        None,
        description="The list of column headers that are in the report.",
        examples=[
            [
                "USERNAME",
                "ACCOUNT_NAME",
                "TYPE",
                "DUE_DATE",
                "LAST_UPDATE",
                "ADDRESS1_STATE",
            ]
        ],
    )
    id: Optional[str] = Field(
        None,
        description="The ID of the report associated with this event.",
        examples=["00OB00000042FHdMAM"],
    )
    name: Optional[str] = Field(
        None,
        description="The display name of the report.",
        examples=["Top Accounts Report"],
    )
    type: Optional[Union[ReportType, str]] = Field(
        None,
        description='Indicates if the report is "REPORT_TYPE_AD_HOC" or "REPORT_TYPE_SAVED".',
        examples=["REPORT_TYPE_SAVED"],
    )


class RiskIndicator(Model):
    name: Optional[str] = Field(
        None,
        description="Name of the risk indicator.",
        examples=["Browser upload"],
    )
    id: Optional[str] = Field(
        None, title="The unique identifier for the risk indicator."
    )
    weight: Optional[int] = Field(
        None,
        description="Configured weight of the risk indicator at the time this event was seen.",
        examples=[5],
    )


class SourceEmail(Model):
    from_: Optional[str] = Field(
        None,
        alias="from",
        description='The display name of the sender, as it appears in the "From" field in the email. In many cases, this is the same as source.email.sender, but it can be different if the message is sent by a server or other mail agent on behalf of someone else.',
        examples=["ari@example.com"],
    )
    sender: Optional[str] = Field(
        None,
        description="The address of the entity responsible for transmitting the message. In many cases, this is the same as source.email.from, but it can be different if the message is sent by a server or other mail agent on behalf of someone else.",
        examples=["ari@example.com"],
    )


class SourceUser(Model):
    email: Optional[List[str]] = Field(
        None,
        description="For endpoint events where a file in cloud storage is synced to a device, the email address of the user logged in to the cloud storage provider.",
        examples=[["first.last@example.com", "first_last_example_com"]],
    )


class Tab(Model):
    title: Optional[str] = Field(
        None,
        description="The title of this app or browser tab.",
        examples=["Example Domain"],
    )
    title_error: Optional[str] = Field(
        None,
        alias="titleError",
        description="Reason the title of this app or browser tab is unavailable.",
        examples=["InsufficientPermissions"],
    )
    url: Optional[str] = Field(
        None,
        description="The URL of this browser tab.",
        examples=["https://example.com/"],
    )
    url_error: Optional[str] = Field(
        None,
        alias="urlError",
        description="Reason the URL of this browser tab is unavailable.",
        examples=["InsufficientPermissions"],
    )


class User(Model):
    device_uid: Optional[str] = Field(
        None,
        alias="deviceUid",
        description="Unique identifier for the device. Null if the file event occurred on a cloud provider.",
        examples=[24681],
    )
    email: Optional[str] = Field(
        None,
        description="The Code42 username used to sign in to the Code42 app on the device. Null if the file event occurred on a cloud provider.",
        examples=["cody@example.com"],
    )
    id: Optional[str] = Field(
        None,
        description="Unique identifier for the user of the Code42 app on the device. Null if the file event occurred on a cloud provider.",
        examples=[1138],
    )


class AcquiredFrom(Model):
    event_id: Optional[str] = Field(
        None,
        alias="eventId",
        examples=[
            "0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163"
        ],
        title="The unique identifier for the event.",
    )
    tabs: Optional[List[Tab]] = Field(
        None, title="Metadata about the browser tab source."
    )
    source_account_name: Optional[str] = Field(
        None,
        alias="sourceAccountName",
        title="For cloud sync apps installed on user devices, the name of the cloud account where the event was observed. This can help identify if the activity occurred in a business or personal account.",
    )
    source_account_type: Optional[str] = Field(
        None,
        alias="sourceAccountType",
        title="For cloud sync apps installed on user devices, the type of account where the event was observed. For example, 'BUSINESS' or 'PERSONAL'.",
    )
    source_category: Optional[str] = Field(
        None,
        alias="sourceCategory",
        examples=["Social Media"],
        title="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
    )
    source_name: Optional[str] = Field(
        None,
        alias="sourceName",
        examples=["Mari's MacBook"],
        title="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
    )
    source_user: Optional[AcquiredFromSourceUser] = Field(None, alias="sourceUser")
    agent_timestamp: Optional[datetime] = Field(
        None,
        alias="agentTimestamp",
        examples=["2020-10-27T15:16:05.369203Z"],
        title="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
    )
    user_email: Optional[str] = Field(
        None,
        alias="userEmail",
        examples=["cody@example.com"],
        title="The Code42 username used to sign in to the Code42 app on the device (for endpoint events) or the cloud service username of the person who caused the event (for cloud events).",
    )
    event_action: Optional[str] = Field(
        None,
        alias="eventAction",
        examples=["file-downloaded"],
        title="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
    )
    source_domains: Optional[List[str]] = Field(
        None,
        alias="sourceDomains",
        examples=["example.com"],
        title="The domain section of the URLs reported in file.acquiredFrom.tabs.url.",
    )
    file_name: Optional[str] = Field(
        None,
        alias="fileName",
        examples=["example.txt"],
        title="The name of the file, including the file extension.",
    )
    md5: Optional[str] = Field(
        None,
        examples=["6123bbce7f3937667a368bbb9f3d79ce"],
        title="The MD5 hash of the file contents.",
    )
    git: Optional[AcquiredFromGit] = None


class Destination(Model):
    account_name: Optional[str] = Field(
        None,
        alias="accountName",
        description="For cloud sync apps installed on user devices, the name of the cloud account where the event was observed. This can help identify if the activity occurred in a business or personal account.",
    )
    account_type: Optional[str] = Field(
        None,
        alias="accountType",
        description="For cloud sync apps installed on user devices, the type of account where the event was observed. For example, 'BUSINESS' or 'PERSONAL'.",
        examples=["BUSINESS"],
    )
    category: Optional[str] = Field(
        None,
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        examples=["Social Media"],
    )
    domains: Optional[List[str]] = Field(
        None,
        description="The domain section of the URLs reported in destination.tabs.url.",
    )
    email: Optional[DestinationEmail] = Field(
        None, description="Metadata about the destination email."
    )
    ip: Optional[str] = Field(
        None,
        description="The external IP address of the user's device.",
        examples=["127.0.0.1"],
    )
    name: Optional[str] = Field(
        None,
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        examples=["Mari's MacBook"],
    )
    operating_system: Optional[str] = Field(
        None,
        alias="operatingSystem",
        description="The operating system of the destination device.",
        examples=["Windows 10"],
    )
    print_job_name: Optional[str] = Field(
        None,
        alias="printJobName",
        description="For print events, the name of the print job, as reported by the user's device.",
        examples=["printer.exe"],
    )
    printer_name: Optional[str] = Field(
        None,
        alias="printerName",
        description="For print events, the name of the printer the job was sent to.",
        examples=["OfficeJet"],
    )
    printed_files_backup_path: Optional[str] = Field(
        None, alias="printedFilesBackupPath"
    )
    private_ip: Optional[List[str]] = Field(
        None,
        alias="privateIp",
        description="The IP address of the user's device on your internal network, including Network interfaces, Virtual Network Interface controllers (NICs), and Loopback/non-routable addresses.",
        examples=[["127.0.0.1", "127.0.0.2"]],
    )
    removable_media: Optional[RemovableMedia] = Field(
        None,
        alias="removableMedia",
        description="Metadata about the removable media destination.",
    )
    tabs: Optional[List[Tab]] = Field(
        None,
        description="Metadata about the browser tab destination.",
    )
    user: Optional[DestinationUser] = Field(
        None, description="Metadata about the destination user."
    )
    remote_hostname: Optional[str] = Field(
        None,
        alias="remoteHostname",
        title="For events where a file transfer tool was used, the destination hostname.",
    )


class File(Model):
    acquired_from: Optional[List[AcquiredFrom]] = Field(None, alias="acquiredFrom")
    category: Optional[str] = Field(
        None,
        description="A categorization of the file that is inferred from MIME type.",
        examples=["Audio"],
    )
    category_by_bytes: Optional[str] = Field(
        None,
        alias="categoryByBytes",
        description="A categorization of the file based on its contents.",
        examples=["Image"],
    )
    category_by_extension: Optional[str] = Field(
        None,
        alias="categoryByExtension",
        description="A categorization of the file based on its extension.",
        examples=["Document"],
    )
    change_type: Optional[str] = Field(
        None,
        alias="changeType",
        description="The action that caused the event. For example: CREATED, MODIFIED, DELETED.",
        examples=["CREATED"],
    )
    classifications: Optional[List[FileClassification]] = Field(
        None, description="Data provided by an external file classification vendor."
    )
    cloud_drive_id: Optional[str] = Field(
        None,
        alias="cloudDriveId",
        description="Unique identifier reported by the cloud provider for the drive containing the file at the time the event occurred.",
        examples=["RvBpZ48u2m"],
    )
    created: Optional[datetime] = Field(
        None,
        description="File creation timestamp as reported by the device's operating system in Coordinated Universal Time (UTC); available for Mac and Windows NTFS devices only.",
        examples=["2020-10-27T15:16:05.369203Z"],
    )
    directory: Optional[str] = Field(
        None,
        description="The file location on the user's device; a forward or backslash must be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
        examples=["/Users/alix/Documents/"],
    )
    original_directory: Optional[str] = Field(
        None,
        alias="originalDirectory",
        examples=["/Users/alix/Documents/"],
        title="The original file location on the user’s device or cloud service location; a forward or backslash must be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
    )
    directory_id: Optional[List[str]] = Field(
        None,
        alias="directoryId",
        description="Unique identifiers of the parent drives that contain the file; searching on directoryId will return events for all of the files contained in the parent drive.",
        examples=[["1234", "56d78"]],
    )
    hash: Optional[Hash] = Field(None, description="Hash values of the file.")
    id: Optional[str] = Field(
        None,
        description="Unique identifier reported by the cloud provider for the file associated with the event.",
        examples=["PUL5zWLRrdudiJZ1OCWw"],
    )
    mime_type: Optional[str] = Field(
        None,
        alias="mimeType",
        title="The MIME type of the file. For endpoint events, if the mimeTypeByBytes differs from mimeTypeByExtension, this indicates the most likely MIME type for the file. For activity observed by a web browser, this is the only MIME type reported.",
    )
    mime_type_by_bytes: Optional[str] = Field(
        None,
        alias="mimeTypeByBytes",
        description="The MIME type of the file based on its contents.",
        examples=["text/csv"],
    )
    mime_type_by_extension: Optional[str] = Field(
        None,
        alias="mimeTypeByExtension",
        description="The MIME type of the file based on its extension.",
        examples=["audio/vorbis"],
    )
    modified: Optional[datetime] = Field(
        None,
        description="File modification timestamp as reported by the device's operating system.  This only indicates changes to file contents.  Changes to file permissions, file owner, or other metadata are not reflected in this timestamp.  Date is reported in Coordinated Universal Time (UTC).",
        examples=["2020-10-27T15:16:05.369203Z"],
    )
    name: Optional[str] = Field(
        None,
        description="The name of the file, including the file extension.",
        examples=["ReadMe.md"],
    )
    original_name: Optional[str] = Field(
        None,
        alias="originalName",
        examples=["ReadMe.md"],
        title="The original name of the file, including the file extension.",
    )
    owner: Optional[str] = Field(
        None,
        description="The name of the user who owns the file as reported by the device's file system.",
        examples=["ari.example"],
    )
    size_in_bytes: Optional[int] = Field(
        None,
        alias="sizeInBytes",
        description="Size of the file in bytes.",
        examples=[256],
    )
    url: Optional[str] = Field(
        description="URL reported by the cloud provider at the time the event occurred.",
        examples=["https://example.com"],
    )
    archive_id: Optional[str] = Field(
        None,
        alias="archiveId",
        title="Unique identifier for files identified as an archive, such as .zip files.",
    )
    parent_archive_id: Optional[str] = Field(
        None,
        alias="parentArchiveId",
        title="For files contained within an archive (such as a .zip file), the unique identifier for that archive; searching on parentArchiveID returns events for all files contained within that archive",
    )
    password_protected: Optional[bool] = Field(
        None,
        alias="passwordProtected",
        title="Indicates if this file is password protected.",
    )


class Risk(Model):
    indicators: Optional[List[RiskIndicator]] = Field(
        None,
        description="List of risk indicators identified for this event. If more than one risk indicator applies to this event, the sum of all indicators determines the total risk score.",
    )
    score: Optional[int] = Field(
        None,
        description="Sum of the weights for each risk indicator. This score is used to determine the overall risk severity of the event.",
        examples=[12],
    )
    severity: Optional[str] = Field(
        None,
        description="The general risk assessment of the event, based on the numeric score.",
        examples=["CRITICAL"],
    )
    trust_reason: Optional[str] = Field(
        None,
        alias="trustReason",
        description="The reason the event is trusted. trustReason is only populated if trusted is true for this event.",
        examples=["TRUSTED_DOMAIN_BROWSER_URL"],
    )
    trusted: Optional[bool] = Field(
        None,
        description="Indicates whether or not the file activity is trusted based on your Data Preferences settings.",
        examples=[True],
    )
    untrusted_values: UntrustedValues = Field(None, alias="untrustedValues")


class Source(Model):
    account_name: Optional[str] = Field(
        None,
        alias="accountName",
        description="For cloud sync apps installed on user devices, the name of the cloud account where the event was observed. This can help identify if the activity occurred in a business or personal account.",
    )
    account_type: Optional[str] = Field(
        None,
        alias="accountType",
        description="For cloud sync apps installed on user devices, the type of account where the event was observed. For example, ‘BUSINESS’ or ‘PERSONAL’.",
    )
    category: Optional[str] = Field(
        None,
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        examples=["Social Media"],
    )
    domain: Optional[str] = Field(
        None,
        description="Fully qualified domain name (FQDN) for the user's device at the time the event is recorded.  If the device is unable to resolve the domain name of the host, it reports the IP address of the host.",
        examples=["localhost"],
    )
    domains: Optional[List[str]] = Field(
        None,
        description="The domain section of the URLs reported in source.tabs.url. (Note: Although similar in name, this field has no relation to source.domain, which reports the FQDN or IP address of the user’s device.)",
    )
    email: Optional[SourceEmail] = Field(
        None, description="Metadata about the email source."
    )
    ip: Optional[str] = Field(
        None,
        description="The external IP address of the user's device.",
        examples=["127.0.0.1"],
    )
    name: Optional[str] = Field(
        None,
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        examples=["Mari's MacBook"],
    )
    operating_system: Optional[str] = Field(
        None,
        alias="operatingSystem",
        description="The operating system of the source device.",
        examples=["Windows 10"],
    )
    private_ip: Optional[List[str]] = Field(
        None,
        alias="privateIp",
        description="The IP address of the user's device on your internal network, including Network interfaces, Virtual Network Interface controllers (NICs), and Loopback/non-routable addresses.",
        examples=[["127.0.0.1", "127.0.0.2"]],
    )
    remote_hostname: Optional[str] = Field(
        None,
        alias="remoteHostname",
        title="For events where a file transfer tool was used, the source hostname.",
    )
    removable_media: Optional[RemovableMedia] = Field(
        None,
        alias="removableMedia",
        description="Metadata about the removable media source.",
    )
    tabs: Optional[List[Tab]] = Field(
        None, description="Metadata about the browser tab source."
    )
    user: Optional[SourceUser] = Field(
        None, description="Metadata about the source user."
    )


class RelatedEvent(Model):
    agent_timestamp: Optional[datetime] = Field(
        None,
        alias="agentTimestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
        examples=["2020-10-27T15:16:05.369203Z"],
    )
    event_action: Optional[str] = Field(
        None,
        alias="eventAction",
        description="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
        examples=["file-downloaded"],
    )
    id: Optional[str] = Field(
        None,
        description="The unique identifier for the event.",
        examples=[
            "0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163"
        ],
    )
    source_category: Optional[str] = Field(
        None,
        alias="sourceCategory",
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        examples=["Social Media"],
    )
    source_name: Optional[str] = Field(
        None,
        alias="sourceName",
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        examples=["Mari's MacBook"],
    )
    tabs: Optional[List[Tab]] = Field(
        None, description="Metadata about the browser tab source."
    )
    user_email: Optional[str] = Field(
        None,
        alias="userEmail",
        description="The Code42 username used to sign in to the Code42 app on the device (for endpoint events) or the cloud service username of the person who caused the event (for cloud events).",
        examples=["cody@example.com"],
    )


class Event(Model):
    action: Optional[str] = Field(
        None,
        description="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
        examples=["file-downloaded"],
    )
    id: Optional[str] = Field(
        None,
        description="The unique identifier for the event.",
        examples=[
            "0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163"
        ],
    )
    ingested: Optional[datetime] = Field(
        None,
        description="Date and time the event was initially received by Code42; timestamp is based on the Code42 server system clock and reported in Coordinated Universal Time (UTC).",
        examples=["2020-10-27T15:15:05.369203Z"],
    )
    inserted: Optional[datetime] = Field(
        None,
        description="Date and time the event processing is completed by Code42; timestamp is based on the Code42 server system clock and reported in Coordinated Universal Time (UTC). Typically occurs very soon after the event.ingested time.",
        examples=["2020-10-27T15:16:05.369203Z"],
    )
    observer: Optional[str] = Field(
        None,
        description="The data source that captured the file event. For example: GoogleDrive, Office365, Salesforce.",
        examples=["Endpoint"],
    )
    detector_display_name: Optional[str] = Field(
        None,
        alias="detectorDisplayName",
        title="Indicates the name you provided when the cloud data connection was initially configured in the Code42 console.",
    )
    related_events: Optional[List[RelatedEvent]] = Field(
        None,
        alias="relatedEvents",
        description="List of other events associated with this file. This can help determine the origin of the file.",
    )
    share_type: Optional[List[str]] = Field(
        None,
        alias="shareType",
        description="Sharing types added by this event.",
        examples=[["SharedViaLink"]],
    )
    vector: Optional[str] = Field(
        None,
        examples=["GIT_PUSH"],
        title="The method of file movement. For example: UPLOADED, DOWNLOADED, EMAILED.",
    )
    xfc_event_id: Optional[str] = Field(
        None,
        alias="xfcEventId",
        description="The identifier for the exfiltrated file collection data associated with this event.",
    )


class Git(Model):
    event_id: Optional[str] = Field(
        None,
        alias="eventId",
        title="A global unique identifier (GUID) generated by Incydr for this Git event. All files associated with this event have the same Git event ID. A single Git event can be associated with multiple file events.",
    )
    last_commit_hash: Optional[str] = Field(
        None,
        alias="lastCommitHash",
        title="Hash value from the most recent commit in this Git event.",
    )
    repository_email: Optional[str] = Field(
        None,
        alias="repositoryEmail",
        title="The email address specified by the user who performed the Git event. This is a user-defined value and may differ from the credentials used to sign in to Git.",
    )
    repository_endpoint_path: Optional[str] = Field(
        None,
        alias="repositoryEndpointPath",
        title="File path of the local Git repository on the user's endpoint.",
    )
    repository_uri: Optional[str] = Field(
        None,
        alias="repositoryUri",
        title="Uniform Resource Identifier (URI) for the Git repository.",
    )
    repository_user: Optional[str] = Field(
        None,
        alias="repositoryUser",
        title="The username specified by the user who performed the Git event. This is a user-defined value and may differ from the credentials used to sign in to Git.",
    )


class FileEventV2(ResponseModel):
    """
    New fields are often being made available on the event response and this model definition may not contain the most recent additions.
    See the response definition for the [File Event Search API](https://developer.code42.com/api/#tag/File-Events/operation/searchEvents) for the most up to date information on what data is available.

    **Fields**:

    * **timestamp**: - The date and time that the Code42 service on the device detected the event.  This timestamp is based on the device’s system clock and reported in Coordinated Universal Time (UTC).
    * **destination**: `Destination` - A [`Destination`] object containing metadata about the destination of the file event.
    * **event**: `Event` - An [`Event`] object containing summary information about the event.
    * **file**: `File` - A [`File`] object containing metadata about the file for this event.
    * **process**: `Process` - A [`Process`] object containing metadata about the process associated with the event.
    * **report**: `Report` - A [`Report`] object containing metadata for reports from 3rd party sources, such Salesforce downloads.
    * **risk**: `Risk` - A [`Risk`] object containing metadata on risk factors associated with the event.
    * **source**: `Source` - A [`Source`] object containing metadata about the source of the file event.
    * **user**: `User` - A [`User`] object containing metadata Attributes of the Code42 username signed in to the Code42 app on the device.
    * **git**: `Git` - A [`Git`] object containing git details for the event (if applicable).
    """

    timestamp: Optional[datetime] = Field(
        None,
        alias="@timestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
        examples=["2020-10-27T15:16:05.369203Z"],
    )
    destination: Optional[Destination] = Field(
        None,
        description="Metadata about the destination of the file event.",
    )
    event: Optional[Event] = Field(
        None,
        description="Summary information about the event.",
    )
    file: Optional[File] = Field(
        None,
        description="Metadata about the file for this event.",
    )
    process: Optional[Process] = Field(
        None,
        description="Metadata about the process associated with the event.",
    )
    report: Optional[Report] = Field(
        None,
        description="Metadata for reports from 3rd party sources, such Salesforce downloads.",
    )
    response_controls: Optional[ResponseControls] = Field(
        None,
        alias="responseControls",
        description="Metadata about preventative actions applied to file activity. Only applies to events for users on a preventative watchlist.",
    )
    risk: Optional[Risk] = Field(
        None,
        description="Risk factor metadata.",
    )
    source: Optional[Source] = Field(
        None,
        description="Metadata about the source of the file event.",
    )
    user: Optional[User] = Field(
        None,
        description="Attributes of the the Code42 username signed in to the Code42 app on the device.",
    )
    git: Optional[Git] = Field(
        None,
        description="Git details for the event.",
    )
