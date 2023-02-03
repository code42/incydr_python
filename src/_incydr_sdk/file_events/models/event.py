from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from _incydr_sdk.core.models import Model
from _incydr_sdk.core.models import ResponseModel
from _incydr_sdk.enums.file_events import ReportType


class DestinationEmail(Model):
    recipients: Optional[List[str]] = Field(
        description="The email addresses of those who received the email. Includes the To, Cc, and Bcc recipients.",
        example=["cody@example.com", "theboss@example.com"],
    )
    subject: Optional[str] = Field(
        description="The subject of the email message.",
        example="Important business documents",
    )


class DestinationUser(Model):
    email: Optional[List[str]] = Field(
        description="For endpoint events where a file in cloud storage is synced to a device, the email address of the user logged in to the cloud storage provider. For cloud events, the email addresses of users added as sharing recipients. In some case, OneDrive events may return multiple values, but this is often the same username formatted in different ways.",
        example=["first.last@example.com", "first_last_example_com"],
    )


class FileClassification(Model):
    value: Optional[str] = Field(
        description="The classification value applied to the file.",
        example="Classified",
    )
    vendor: Optional[str] = Field(
        description="The name of the vendor that classified the file.",
        example="MICROSOFT INFORMATION PROTECTION",
    )


class Hash(Model):
    md5: Optional[str] = Field(
        description="The MD5 hash of the file contents.",
        example="a162591e78eb2c816a28907d3ac020f9",
    )
    md5_error: Optional[str] = Field(
        alias="md5Error", description="Reason the MD5 hash is unavailable."
    )
    sha256: Optional[str] = Field(
        description="The SHA-256 hash of the file contents.",
        example="ded96d69c63754472efc4aa86fed68d4e17784b38089851cfa84e699e48b4155",
    )
    sha256_error: Optional[str] = Field(
        alias="sha256Error", description="Reason the SHA-256 hash is unavailable."
    )


class Process(Model):
    executable: Optional[str] = Field(
        description="The name of the process that accessed the file, as reported by the device’s operating system. Depending on your Code42 product plan, this value may be null for some event types.",
        example="bash",
    )
    owner: Optional[str] = Field(
        description="The username of the process owner, as reported by the device’s operating system. Depending on your Code42 product plan, this value may be null for some event types.",
        example="root",
    )


class RemovableMedia(Model):
    bus_type: Optional[str] = Field(
        alias="busType",
        description="For events detected on removable media, indicates the communication system used to transfer data between the host and the removable device.",
        example="USB 3.0 Bus",
    )
    capacity: Optional[int] = Field(
        description="For events detected on removable media, the capacity of the removable device in bytes.",
        example=15631122432,
    )
    media_name: Optional[str] = Field(
        alias="mediaName",
        description="For events detected on removable media, the media name of the device, as reported by the vendor/device. This is usually very similar to the productName, but can vary based on the type of device. For example, if the device is a hard drive in a USB enclosure, this may be the combination of the drive model and the enclosure model.\nThis value is not provided by all devices, so it may be null in some cases.",
        example="Cruzer Blade",
    )
    name: Optional[str] = Field(
        description="For events detected on removable media, the name of the removable device.",
        example="JUMPDRIVE",
    )
    partition_id: Optional[List[str]] = Field(
        alias="partitionId",
        description="For events detected on removable media, a unique identifier assigned to the volume/partition when it was formatted. Windows devices refer to this as the VolumeGuid. On Mac devices, this is the Disk / Partition UUID, which appears when running the Terminal command diskUtil info.",
        example=["disk0s2", "disk0s3"],
    )
    serial_number: Optional[str] = Field(
        alias="serialNumber",
        description="For events detected on removable media, the serial number of the removable device.",
        example="4C531001550407108465",
    )
    vendor: Optional[str] = Field(
        description="For events detected on removable media, the vendor of the removable device.",
        example="SanDisk",
    )
    volume_name: Optional[List[str]] = Field(
        alias="volumeName",
        description='For events detected on removable media, the name assigned to the volume when it was formatted, as reported by the device\'s operating system. This is also frequently called the "partition" name.',
        example=["MY_FILES"],
    )


class Report(Model):
    count: Optional[int] = Field(
        description="The total number of rows returned in the report.", example=20
    )
    description: Optional[str] = Field(
        description="The description of the report.",
        example="Top 20 accounts based on annual revenue",
    )
    headers: Optional[List[str]] = Field(
        description="The list of column headers that are in the report.",
        example=[
            "USERNAME",
            "ACCOUNT_NAME",
            "TYPE",
            "DUE_DATE",
            "LAST_UPDATE",
            "ADDRESS1_STATE",
        ],
    )
    id: Optional[str] = Field(
        description="The ID of the report associated with this event.",
        example="00OB00000042FHdMAM",
    )
    name: Optional[str] = Field(
        description="The display name of the report.",
        example="Top Accounts Report",
    )
    type: Optional[ReportType] = Field(
        description='Indicates if the report is "REPORT_TYPE_AD_HOC" or "REPORT_TYPE_SAVED".',
        example="REPORT_TYPE_SAVED",
    )


class RiskIndicator(Model):
    name: Optional[str] = Field(
        description="Name of the risk indicator.",
        example="Browser upload",
    )
    weight: Optional[int] = Field(
        description="Configured weight of the risk indicator at the time this event was seen.",
        example=5,
    )


class SourceEmail(Model):
    from_: Optional[str] = Field(
        alias="from",
        description='The display name of the sender, as it appears in the "From" field in the email. In many cases, this is the same as source.email.sender, but it can be different if the message is sent by a server or other mail agent on behalf of someone else.',
        example="ari@example.com",
    )
    sender: Optional[str] = Field(
        description="The address of the entity responsible for transmitting the message. In many cases, this is the same as source.email.from, but it can be different if the message is sent by a server or other mail agent on behalf of someone else.",
        example="ari@example.com",
    )


class SourceUser(Model):
    email: Optional[List[str]] = Field(
        None,
        description="For endpoint events where a file in cloud storage is synced to a device, the email address of the user logged in to the cloud storage provider.",
        example=["first.last@example.com", "first_last_example_com"],
    )


class Tab(Model):
    title: Optional[str] = Field(
        description="The title of this app or browser tab.",
        example="Example Domain",
    )
    title_error: Optional[str] = Field(
        alias="titleError",
        description="Reason the title of this app or browser tab is unavailable.",
        example="InsufficientPermissions",
    )
    url: Optional[str] = Field(
        description="The URL of this browser tab.",
        example="https://example.com/",
    )
    url_error: Optional[str] = Field(
        alias="urlError",
        description="Reason the URL of this browser tab is unavailable.",
        example="InsufficientPermissions",
    )


class User(Model):
    device_uid: Optional[str] = Field(
        alias="deviceUid",
        description="Unique identifier for the device. Null if the file event occurred on a cloud provider.",
        example=24681,
    )
    email: Optional[str] = Field(
        description="The Code42 username used to sign in to the Code42 app on the device. Null if the file event occurred on a cloud provider.",
        example="cody@example.com",
    )
    id: Optional[str] = Field(
        description="Unique identifier for the user of the Code42 app on the device. Null if the file event occurred on a cloud provider.",
        example=1138,
    )


class AcquiredFrom(Model):
    agent_timestamp: Optional[datetime] = Field(
        None,
        alias="agentTimestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
        example="2020-10-27T15:16:05.369203Z",
    )
    event_action: Optional[str] = Field(
        None,
        alias="eventAction",
        description="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
        example="file-downloaded",
    )
    event_id: Optional[str] = Field(
        None,
        alias="eventId",
        description="The unique identifier for the event.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    file_name: Optional[str] = Field(
        None,
        alias="fileName",
        description="The name of the file, including the file extension.",
        example="example.txt",
    )
    md5: Optional[str] = Field(
        None,
        description="The MD5 hash of the file contents.",
        example="6123bbce7f3937667a368bbb9f3d79ce",
    )
    source_category: Optional[str] = Field(
        None,
        alias="sourceCategory",
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        example="Social Media",
    )
    source_domains: Optional[List[str]] = Field(
        None,
        alias="sourceDomains",
        description="The domain section of the URLs reported in file.acquiredFrom.tabs.url.",
        example="example.com",
    )
    source_name: Optional[str] = Field(
        None,
        alias="sourceName",
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        example="Mari's MacBook",
    )
    tabs: Optional[List[Tab]] = Field(
        None,
        description="Metadata about the browser tab source.",
    )
    user_email: Optional[str] = Field(
        None,
        alias="userEmail",
        description="The Code42 username used to sign in to the Code42 app on the device (for endpoint events) or the cloud service username of the person who caused the event (for cloud events).",
        example="cody@example.com",
    )


class Destination(Model):
    account_name: Optional[str] = Field(
        alias="accountName",
        description="For cloud sync apps installed on user devices, the name of the cloud account where the event was observed. This can help identify if the activity occurred in a business or personal account.",
    )
    account_type: Optional[str] = Field(
        alias="accountType",
        description="For cloud sync apps installed on user devices, the type of account where the event was observed. For example, 'BUSINESS' or 'PERSONAL'.",
        example="BUSINESS",
    )
    category: Optional[str] = Field(
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        example="Social Media",
    )
    domains: Optional[List[str]] = Field(
        description="The domain section of the URLs reported in destination.tabs.url.",
    )
    email: Optional[DestinationEmail] = Field(
        description="Metadata about the destination email."
    )
    ip: Optional[str] = Field(
        description="The external IP address of the user's device.",
        example="127.0.0.1",
    )
    name: Optional[str] = Field(
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        example="Mari's MacBook",
    )
    operating_system: Optional[str] = Field(
        alias="operatingSystem",
        description="The operating system of the destination device.",
        example="Windows 10",
    )
    print_job_name: Optional[str] = Field(
        alias="printJobName",
        description="For print events, the name of the print job, as reported by the user's device.",
        example="printer.exe",
    )
    printer_name: Optional[str] = Field(
        alias="printerName",
        description="For print events, the name of the printer the job was sent to.",
        example="OfficeJet",
    )
    printed_files_backup_path: Optional[str] = Field(alias="printedFilesBackupPath")
    private_ip: Optional[List[str]] = Field(
        alias="privateIp",
        description="The IP address of the user's device on your internal network, including Network interfaces, Virtual Network Interface controllers (NICs), and Loopback/non-routable addresses.",
        example=["127.0.0.1", "127.0.0.2"],
    )
    removable_media: Optional[RemovableMedia] = Field(
        alias="removableMedia",
        description="Metadata about the removable media destination.",
    )
    tabs: Optional[List[Tab]] = Field(
        description="Metadata about the browser tab destination.",
    )
    user: Optional[DestinationUser] = Field(
        description="Metadata about the destination user."
    )


class File(Model):
    acquired_from: Optional[List[AcquiredFrom]] = Field(None, alias="acquiredFrom")
    category: Optional[str] = Field(
        description="A categorization of the file that is inferred from MIME type.",
        example="Audio",
    )
    category_by_bytes: Optional[str] = Field(
        alias="categoryByBytes",
        description="A categorization of the file based on its contents.",
        example="Image",
    )
    category_by_extension: Optional[str] = Field(
        alias="categoryByExtension",
        description="A categorization of the file based on its extension.",
        example="Document",
    )
    change_type: Optional[str] = Field(
        None,
        alias="changeType",
        description="The action that caused the event. For example: CREATED, MODIFIED, DELETED.",
        example="CREATED",
    )
    classifications: Optional[List[FileClassification]] = Field(
        description="Data provided by an external file classification vendor."
    )
    cloud_drive_id: Optional[str] = Field(
        alias="cloudDriveId",
        description="Unique identifier reported by the cloud provider for the drive containing the file at the time the event occurred.",
        example="RvBpZ48u2m",
    )
    created: Optional[datetime] = Field(
        description="File creation timestamp as reported by the device's operating system in Coordinated Universal Time (UTC); available for Mac and Windows NTFS devices only.",
        example="2020-10-27T15:16:05.369203Z",
    )
    directory: Optional[str] = Field(
        description="The file location on the user's device; a forward or backslash must be included at the end of the filepath. Possibly null if the file event occurred on a cloud provider.",
        example="/Users/alix/Documents/",
    )
    directory_id: Optional[List[str]] = Field(
        alias="directoryId",
        description="Unique identifiers of the parent drives that contain the file; searching on directoryId will return events for all of the files contained in the parent drive.",
        example=["1234", "56d78"],
    )
    hash: Optional[Hash] = Field(description="Hash values of the file.")
    id: Optional[str] = Field(
        description="Unique identifier reported by the cloud provider for the file associated with the event.",
        example="PUL5zWLRrdudiJZ1OCWw",
    )
    mime_type_by_bytes: Optional[str] = Field(
        alias="mimeTypeByBytes",
        description="The MIME type of the file based on its contents.",
        example="text/csv",
    )
    mime_type_by_extension: Optional[str] = Field(
        alias="mimeTypeByExtension",
        description="The MIME type of the file based on its extension.",
        example="audio/vorbis",
    )
    modified: Optional[datetime] = Field(
        description="File modification timestamp as reported by the device's operating system.  This only indicates changes to file contents.  Changes to file permissions, file owner, or other metadata are not reflected in this timestamp.  Date is reported in Coordinated Universal Time (UTC).",
        example="2020-10-27T15:16:05.369203Z",
    )
    name: Optional[str] = Field(
        description="The name of the file, including the file extension.",
        example="ReadMe.md",
    )
    owner: Optional[str] = Field(
        description="The name of the user who owns the file as reported by the device's file system.",
        example="ari.example",
    )
    size_in_bytes: Optional[int] = Field(
        alias="sizeInBytes", description="Size of the file in bytes.", example=256
    )
    url: Optional[str] = Field(
        description="URL reported by the cloud provider at the time the event occurred.",
        example="https://example.com",
    )


class Risk(Model):
    indicators: Optional[List[RiskIndicator]] = Field(
        description="List of risk indicators identified for this event. If more than one risk indicator applies to this event, the sum of all indicators determines the total risk score.",
    )
    score: Optional[int] = Field(
        description="Sum of the weights for each risk indicator. This score is used to determine the overall risk severity of the event.",
        example=12,
    )
    severity: Optional[str] = Field(
        description="The general risk assessment of the event, based on the numeric score.",
        example="CRITICAL",
    )
    trust_reason: Optional[str] = Field(
        alias="trustReason",
        description="The reason the event is trusted. trustReason is only populated if trusted is true for this event.",
        example="TRUSTED_DOMAIN_BROWSER_URL",
    )
    trusted: Optional[bool] = Field(
        description="Indicates whether or not the file activity is trusted based on your Data Preferences settings.",
        example=True,
    )


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
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        example="Social Media",
    )
    domain: Optional[str] = Field(
        description="Fully qualified domain name (FQDN) for the user's device at the time the event is recorded.  If the device is unable to resolve the domain name of the host, it reports the IP address of the host.",
        example="localhost",
    )
    domains: Optional[List[str]] = Field(
        description="The domain section of the URLs reported in source.tabs.url. (Note: Although similar in name, this field has no relation to source.domain, which reports the FQDN or IP address of the user’s device.)",
    )
    email: Optional[SourceEmail] = Field(description="Metadata about the email source.")
    ip: Optional[str] = Field(
        description="The external IP address of the user's device.",
        example="127.0.0.1",
    )
    name: Optional[str] = Field(
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        example="Mari's MacBook",
    )
    operating_system: Optional[str] = Field(
        alias="operatingSystem",
        description="The operating system of the source device.",
        example="Windows 10",
    )
    private_ip: Optional[List[str]] = Field(
        alias="privateIp",
        description="The IP address of the user's device on your internal network, including Network interfaces, Virtual Network Interface controllers (NICs), and Loopback/non-routable addresses.",
        example=["127.0.0.1", "127.0.0.2"],
    )
    removable_media: Optional[RemovableMedia] = Field(
        alias="removableMedia",
        description="Metadata about the removable media source.",
    )
    tabs: Optional[List[Tab]] = Field(
        description="Metadata about the browser tab source."
    )
    user: Optional[SourceUser] = Field(
        None, description="Metadata about the source user."
    )


class RelatedEvent(Model):
    agent_timestamp: Optional[datetime] = Field(
        alias="agentTimestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
        example="2020-10-27T15:16:05.369203Z",
    )
    event_action: Optional[str] = Field(
        alias="eventAction",
        description="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
        example="file-downloaded",
    )
    id: Optional[str] = Field(
        description="The unique identifier for the event.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    source_category: Optional[str] = Field(
        alias="sourceCategory",
        description="General category of where the file originated. For example: Cloud Storage, Email, Social Media.",
        example="Social Media",
    )
    source_name: Optional[str] = Field(
        alias="sourceName",
        description="The name reported by the device's operating system.  This may be different than the device name in the Code42 console.",
        example="Mari's MacBook",
    )
    tabs: Optional[List[Tab]] = Field(
        description="Metadata about the browser tab source."
    )
    user_email: Optional[str] = Field(
        alias="userEmail",
        description="The Code42 username used to sign in to the Code42 app on the device (for endpoint events) or the cloud service username of the person who caused the event (for cloud events).",
        example="cody@example.com",
    )


class Event(Model):
    action: Optional[str] = Field(
        description="The type of file event observed. For example: file-modified, application-read, removable-media-created.",
        example="file-downloaded",
    )
    id: Optional[str] = Field(
        description="The unique identifier for the event.",
        example="0_147e9445-2f30-4a91-8b2a-9455332e880a_973435567569502913_986467523038446097_163",
    )
    ingested: Optional[datetime] = Field(
        description="Date and time the event was initially received by Code42; timestamp is based on the Code42 server system clock and reported in Coordinated Universal Time (UTC).",
        example="2020-10-27T15:15:05.369203Z",
    )
    inserted: Optional[datetime] = Field(
        description="Date and time the event processing is completed by Code42; timestamp is based on the Code42 server system clock and reported in Coordinated Universal Time (UTC). Typically occurs very soon after the event.ingested time.",
        example="2020-10-27T15:16:05.369203Z",
    )
    observer: Optional[str] = Field(
        description="The data source that captured the file event. For example: GoogleDrive, Office365, Salesforce.",
        example="Endpoint",
    )
    related_events: Optional[List[RelatedEvent]] = Field(
        alias="relatedEvents",
        description="List of other events associated with this file. This can help determine the origin of the file.",
    )
    share_type: Optional[List[str]] = Field(
        alias="shareType",
        description="Sharing types added by this event.",
        example=["SharedViaLink"],
    )
    vector: Optional[str]


class Git(Model):
    event_id: Optional[str] = Field(None, alias="eventId")
    last_commit_hash: Optional[str] = Field(None, alias="lastCommitHash")
    repository_email: Optional[str] = Field(None, alias="repositoryEmail")
    repository_endpoint_path: Optional[str] = Field(
        None, alias="repositoryEndpointPath"
    )
    repository_uri: Optional[str] = Field(None, alias="repositoryUri")
    repository_user: Optional[str] = Field(None, alias="repositoryUser")


class FileEventV2(ResponseModel):
    """
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
        alias="@timestamp",
        description="Date and time that the Code42 service on the device detected an event; based on the device’s system clock and reported in Coordinated Universal Time (UTC).",
        example="2020-10-27T15:16:05.369203Z",
    )
    destination: Optional[Destination] = Field(
        description="Metadata about the destination of the file event.",
    )
    event: Optional[Event] = Field(
        description="Summary information about the event.",
    )
    file: Optional[File] = Field(
        description="Metadata about the file for this event.",
    )
    process: Optional[Process] = Field(
        description="Metadata about the process associated with the event.",
    )
    report: Optional[Report] = Field(
        description="Metadata for reports from 3rd party sources, such Salesforce downloads.",
    )
    risk: Optional[Risk] = Field(
        description="Risk factor metadata.",
    )
    source: Optional[Source] = Field(
        description="Metadata about the source of the file event.",
    )
    user: Optional[User] = Field(
        description="Attributes of the the Code42 username signed in to the Code42 app on the device.",
    )
    git: Optional[Git] = Field(
        description="Git details for the event.",
    )
