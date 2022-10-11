# Enums

!!! note
    Incydr SDK's enums all inherit from Python's `str` class.  The `str` value for each enum can be used wherever that enum class is expected.

## Alerts

### Alert Severity

::: incydr.enums.alerts.AlertSeverity
    :docstring:

* **LOW** = `"LOW"`
* **MEDIUM** = `"MEDIUM"`
* **HIGH** = `"HIGH"`

### Alert State

::: incydr.enums.alerts.AlertState
    :docstring:

* **OPEN** = `"OPEN"`
* **RESOLVED** = `"RESOLVED"`
* **IN_PROGRESS** = `"IN_PROGRESS"`
* **PENDING** = `"PENDING"`

### Alert Terms

::: incydr.enums.alerts.AlertTerm
    :docstring:

* **ALERT_ID** = `"AlertId"`
* **TYPE** = `"Type"`
* **NAME** = `"Name"`
* **DESCRIPTION** = `"Description"`
* **ACTOR** = `"Actor"`
* **ACTOR_ID** = `"ActorId"`
* **TARGET** = `"Target"`
* **RISK_SEVERITY** = `"RiskSeverity"`
* **CREATED_AT** = `"CreatedAt"`
* **HAS_AUTH_SIGNIFICANT_WATCHLIST** = `"HasAuthSignificantWatchlist"`
* **STATE** = `"State"`
* **STATE_LAST_MODIFIED_AT** = `"StateLastModifiedAt"`
* **STATE_LAST_MODIFIED_BY** = `"StateLastModifiedBy"`
* **LAST_MODIFIED_TIME** = `"LastModifiedTime"`
* **LAST_MODIFIED_BY** = `"LastModifiedBy"`
* **RULE_ID** = `"RuleId"`
* **SEVERITY** = `"Severity"`

### Risk Severity

::: incydr.enums.alerts.RiskSeverity
    :docstring:

* **CRITICAL** = `"CRITICAL"`
* **HIGH** = `"HIGH"`
* **MODERATE** = `"MODERATE"`
* **LOW** = `"LOW"`
* **NO_RISK_INDICATED** = `"NO_RISK_INDICATED"`

## File Events

### Event Search Terms

::: incydr.enums.file_events.EventSearchTerm
    :docstring:

* **TIMESTAMP** = `"@timestamp"`
* **DESTINATION_ACCOUNT_NAME** = `"destination.accountName"`
* **DESTINATION_ACCOUNT_TYPE** = `"destination.accountType"`
* **DESTINATION_CATEGORY** = `"destination.category"`
* **DESTINATION_DOMAINS** = `"destination.domains"`
* **DESTINATION_EMAIL_RECIPIENTS** = `"destination.email.recipients"`
* **DESTINATION_EMAIL_SUBJECT** = `"destination.email.subject"`
* **DESTINATION_IP** = `"destination.ip"`
* **DESTINATION_NAME** = `"destination.name"`
* **DESTINATION_OPERATING_SYSTEM** = `"destination.operatingSystem"`
* **DESTINATION_PRINT_JOB_NAME** = `"destination.printJobName"`
* **DESTINATION_PRINTED_FILES_BACKUP_PATH** = `"destination.printedFilesBackupPath"`
* **DESTINATION_PRINTER_NAME** = `"destination.printerName"`
* **DESTINATION_PRIVATE_IP** = `"destination.privateIp"`
* **DESTINATION_REMOVABLE_MEDIA_BUS_TYPE** = `"destination.removableMedia.busType"`
* **DESTINATION_REMOVABLE_MEDIA_CAPACITY** = `"destination.removableMedia.capacity"`
* **DESTINATION_REMOVABLE_MEDIA_MEDIA_NAME** = `"destination.removableMedia.mediaName"`
* **DESTINATION_REMOVABLE_MEDIA_NAME** = `"destination.removableMedia.name"`
* **DESTINATION_REMOVABLE_MEDIA_PARTITION_ID** = `"destination.removableMedia.partitionId"`
* **DESTINATION_REMOVABLE_MEDIA_SERIAL_NUMBER** = `"destination.removableMedia.serialNumber"`
* **DESTINATION_REMOVABLE_MEDIA_VENDOR** = `"destination.removableMedia.vendor"`
* **DESTINATION_REMOVABLE_MEDIA_VOLUME_NAME** = `"destination.removableMedia.volumeName"`
* **DESTINATION_TABS_TITLE** = `"destination.tabs.title"`
* **DESTINATION_TABS_TITLE_ERROR** = `"destination.tabs.titleError"`
* **DESTINATION_TABS_URL** = `"destination.tabs.url"`
* **DESTINATION_TABS_URL_ERROR** = `"destination.tabs.urlError"`
* **DESTINATION_USER_EMAIL** = `"destination.user.email"`
* **EVENT_ACTION** = `"event.action"`
* **EVENT_ID** = `"event.id"`
* **EVENT_INGESTED** = `"event.ingested"`
* **EVENT_INSERTED** = `"event.inserted"`
* **EVENT_OBSERVER** = `"event.observer"`
* **EVENT_RELATED_EVENTS_AGENT_TIMESTAMP** = `"event.relatedEvents.agentTimestamp"`
* **EVENT_RELATED_EVENTS_EVENT_ACTION** = `"event.relatedEvents.eventAction"`
* **EVENT_RELATED_EVENTS_ID** = `"event.relatedEvents.id"`
* **EVENT_RELATED_EVENTS_SOURCE_CATEGORY** = `"event.relatedEvents.sourceCategory"`
* **EVENT_RELATED_EVENTS_SOURCE_NAME** = `"event.relatedEvents.sourceName"`
* **EVENT_RELATED_EVENTS_TABS_TITLE** = `"event.relatedEvents.tabs.title"`
* **EVENT_RELATED_EVENTS_TABS_TITLE_ERROR** = `"event.relatedEvents.tabs.titleError"`
* **EVENT_RELATED_EVENTS_TABS_URL** = `"event.relatedEvents.tabs.url"`
* **EVENT_RELATED_EVENTS_TABS_URL_ERROR** = `"event.relatedEvents.tabs.urlError"`
* **EVENT_RELATED_EVENTS_USER_EMAIL** = `"event.relatedEvents.userEmail"`
* **EVENT_SHARE_TYPE** = `"event.shareType"`
* **FILE_CATEGORY** = `"file.category"`
* **FILE_CATEGORY_BY_BYTES** = `"file.categoryByBytes"`
* **FILE_CATEGORY_BY_EXTENSION** = `"file.categoryByExtension"`
* **FILE_CLASSIFICATIONS_VALUE** = `"file.classifications.value"`
* **FILE_CLASSIFICATIONS_VENDOR** = `"file.classifications.vendor"`
* **FILE_CLOUD_DRIVE_ID** = `"file.cloudDriveId"`
* **FILE_CREATED** = `"file.created"`
* **FILE_DIRECTORY** = `"file.directory"`
* **FILE_DIRECTORY_ID** = `"file.directoryId"`
* **FILE_HASH_MD5** = `"file.hash.md5"`
* **FILE_HASH_MD5_ERROR** = `"file.hash.md5Error"`
* **FILE_HASH_SHA256** = `"file.hash.sha256"`
* **FILE_HASH_SHA256_ERROR** = `"file.hash.sha256Error"`
* **FILE_ID** = `"file.id"`
* **FILE_MIME_TYPE_BY_BYTES** = `"file.mimeTypeByBytes"`
* **FILE_MIME_TYPE_BY_EXTENSION** = `"file.mimeTypeByExtension"`
* **FILE_MODIFIED** = `"file.modified"`
* **FILE_NAME** = `"file.name"`
* **FILE_OWNER** = `"file.owner"`
* **FILE_SIZE_IN_BYTES** = `"file.sizeInBytes"`
* **FILE_URL** = `"file.url"`
* **PROCESS_EXECUTABLE** = `"process.executable"`
* **PROCESS_OWNER** = `"process.owner"`
* **REPORT_COUNT** = `"report.count"`
* **REPORT_DESCRIPTION** = `"report.description"`
* **REPORT_HEADERS** = `"report.headers"`
* **REPORT_ID** = `"report.id"`
* **REPORT_NAME** = `"report.name"`
* **REPORT_TYPE** = `"report.type"`
* **RISK_INDICATORS_NAME** = `"risk.indicators.name"`
* **RISK_INDICATORS_WEIGHT** = `"risk.indicators.weight"`
* **RISK_SCORE** = `"risk.score"`
* **RISK_SEVERITY** = `"risk.severity"`
* **RISK_TRUST_REASON** = `"risk.trustReason"`
* **RISK_TRUSTED** = `"risk.trusted"`
* **SOURCE_CATEGORY** = `"source.category"`
* **SOURCE_DOMAIN** = `"source.domain"`
* **SOURCE_DOMAINS** = `"source.domains"`
* **SOURCE_EMAIL_FROM** = `"source.email.from"`
* **SOURCE_EMAIL_SENDER** = `"source.email.sender"`
* **SOURCE_IP** = `"source.ip"`
* **SOURCE_NAME** = `"source.name"`
* **SOURCE_OPERATING_SYSTEM** = `"source.operatingSystem"`
* **SOURCE_PRIVATE_IP** = `"source.privateIp"`
* **SOURCE_REMOVABLE_MEDIA_BUS_TYPE** = `"source.removableMedia.busType"`
* **SOURCE_REMOVABLE_MEDIA_CAPACITY** = `"source.removableMedia.capacity"`
* **SOURCE_REMOVABLE_MEDIA_MEDIA_NAME** = `"source.removableMedia.mediaName"`
* **SOURCE_REMOVABLE_MEDIA_NAME** = `"source.removableMedia.name"`
* **SOURCE_REMOVABLE_MEDIA_PARTITION_ID** = `"source.removableMedia.partitionId"`
* **SOURCE_REMOVABLE_MEDIA_SERIAL_NUMBER** = `"source.removableMedia.serialNumber"`
* **SOURCE_REMOVABLE_MEDIA_VENDOR** = `"source.removableMedia.vendor"`
* **SOURCE_REMOVABLE_MEDIA_VOLUME_NAME** = `"source.removableMedia.volumeName"`
* **SOURCE_TABS_TITLE** = `"source.tabs.title"`
* **SOURCE_TABS_TITLE_ERROR** = `"source.tabs.titleError"`
* **SOURCE_TABS_URL** = `"source.tabs.url"`
* **SOURCE_TABS_URL_ERROR** = `"source.tabs.urlError"`
* **USER_DEVICE_UID** = `"user.deviceUid"`
* **USER_EMAIL** = `"user.email"`
* **USER_ID** = `"user.id"`

### File Categories

::: incydr.enums.file_events.FileCategory
    :docstring:

* **AUDIO** = `"Audio"`
* **DOCUMENT** = `"Document"`
* **EXECUTABLE** = `"Executable"`
* **IMAGE** = `"Image"`
* **PDF** = `"Pdf"`
* **PRESENTATION** = `"Presentation"`
* **SCRIPT** = `"Script"`
* **SOURCE_CODE** = `"SourceCode"`
* **SPREADSHEET** = `"Spreadsheet"`
* **VIDEO** = `"Video"`
* **VIRTUAL_DISK_IMAGE** = `"VirtualDiskImage"`
* **ZIP** = `"Archive"`

### Event Actions

::: incydr.enums.file_events.EventAction
    :docstring:

* **REMOVABLE_MEDIA_CREATED** = `"removable-media-created"`
* **REMOVABLE_MEDIA_MODIFIED** = `"removable-media-modified"`
* **REMOVABLE_MEDIA_DELETED** = `"removable-media-deleted"`
* **SYNC_APP_CREATED** = `"sync-app-created"`
* **SYNC_APP_MODIFIED** = `"sync-app-modified"`
* **SYNC_APP_DELETED** = `"sync-app-deleted"`
* **FILE_SHARED** = `"file-shared"`
* **FILE_CREATED** = `"file-created"`
* **FILE_DELETED** = `"file-deleted"`
* **FILE_DOWNLOADED** = `"file-downloaded"`
* **FILE_EMAILED** = `"file-emailed"`
* **FILE_MODIFIED** = `"file-modified"`
* **FILE_PRINTED** = `"file-printed"`
* **APPLICATION_READ** = `"application-read"`

### Source & Destination Categories

::: incydr.enums.file_events.Category
    :docstring:

* **BUSINESS_TOOLS** = `"Business Tools"`
* **CLOUD_STORAGE** = `"Cloud Storage"`
* **DEVICE** = `"Device"`
* **EMAIL** = `"Email"`
* **MESSAGING** = `"Messaging"`
* **MULTIPLE_POSSIBILITIES** = `"Multiple Possibilities"`
* **SOCIAL_MEDIA** = `"Social Media"`
* **SOURCE_CODE_REPOSITORY** = `"Source Code Repository"`
* **UNCATEGORIZED** = `"Uncategorized"`
* **UNKNOWN** = `"Unknown"`
* **BUSINESS_INTELLIGENCE_TOOLS** = `"Business Intelligence Tools"`
* **CIVIL_SERVICES** = `"Civil Services"`
* **CLOUD_COMPUTING** = `"Cloud Computing"`
* **CODING_TOOLS** = `"Coding Tools"`
* **CONTRACT_MANAGEMENT** = `"Contract Management"`
* **CRM_TOOLS** = `"CRM Tools"`
* **DESIGN_TOOLS** = `"Design Tools"`
* **E_COMMERCE** = `"E-commerce"`
* **FILE_CONVERSION_TOOLS** = `"File Conversion Tools"`
* **FINANCIAL_SERVICES** = `"Financial Services"`
* **HEALTHCARE_AND_INSURANCE** = `"Healthcare & Insurance"`
* **HR_TOOLS** = `"HR Tools"`
* **IMAGE_HOSTING** = `"Image Hosting"`
* **IT_SERVICES** = `"IT Services"`
* **JOB_LISTINGS** = `"Job Listings"`
* **LEARNING_PLATFORMS** = `"Learning Platforms"`
* **MARKETING_TOOLS** = `"Marketing Tools"`
* **PDF_MANAGER** = `"PDF Manager"`
* **PHOTO_PRINTING** = `"Photo Printing"`
* **PRODUCTIVITY_TOOLS** = `"Productivity Tools"`
* **PROFESSIONAL_SERVICES** = `"Professional Services"`
* **REAL_ESTATE** = `"Real Estate"`
* **SALES_TOOLS** = `"Sales Tools"`
* **SEARCH_ENGINE** = `"Search Engine"`
* **SHIPPING** = `"Shipping"`
* **SOFTWARE** = `"Software"`
* **TRAVEL** = `"Travel"`
* **WEB_HOSTING** = `"Web Hosting"`

### Share Types

::: incydr.enums.file_events.ShareType
    :docstring:

* **PUBLIC_LINK_SHARE** = `"Anyone with the link"`
* **DOMAIN_SHARE** = `"Anyone in your organization"`
* **DIRECT_USER_SHARE** = `"Shared with specific people"`

### Report Types

::: incydr.enums.file_events.ReportType
    :docstring:

* **AD_HOC** = `"REPORT_TYPE_AD_HOC"`
* **SAVED** = `"REPORT_TYPE_SAVED"`

### Risk Indicators

::: incydr.enums.file_events.RiskIndicators
    :docstring:

#### Risk Indicators - Destinations

* **ADOBE_UPLOAD** = `"Adobe upload"`
* **ADOBE_ACROBAT_UPLOAD** = `"Adobe Acrobat upload"`
* **AIR_DROP** = `"AirDrop"`
* **AMAZON_DRIVE_UPLOAD** = `"Amazon Drive upload"`
* **AOL_UPLOAD** = `"AOL upload"`
* **BAIDU_NET_DISK_UPLOAD** = `"Baidu NetDisk upload"`
* **BITBUCKET_UPLOAD** = `"Bitbucket upload"`
* **BOX_UPLOAD** = `"Box upload"`
* **CANVA_UPLOAD** = `"Canva upload"`
* **CLOUD_CONVERT_UPLOAD** = `"CloudConvert upload"`
* **COLABORATORY_UPLOAD** = `"Colaboratory upload"`
* **COMBINE_PDF_UPLOAD** = `"CombinePDF upload"`
* **COMCAST_UPLOAD** = `"Comcast upload"`
* **COMPRESS_JPEG_UPLOAD** = `"Compress JPEG upload"`
* **CRASHPLAN_UPLOAD** = `"Crashplan upload"`
* **DISCORD_UPLOAD** = `"Discord upload"`
* **DRAKE_PORTALS_UPLOAD** = `"Drake Portals upload"`
* **DROPBOX_UPLOAD** = `"Dropbox upload"`
* **EVERNOTE_UPLOAD** = `"Evernote upload"`
* **FACEBOOK_MESSENGER_UPLOAD** = `"Facebook Messenger upload"`
* **FACEBOOK_UPLOAD** = `"Facebook upload"`
* **FASTMAIL_UPLOAD** = `"Fastmail upload"`
* **FIGMA_UPLOAD** = `"Figma upload"`
* **FILE_DOT_IO_UPLOAD** = `"File.io upload"`
* **FILESTACK_UPLOAD** = `"Filestack upload"`
* **FOUR_CHAN_UPLOAD** = `"4chan upload"`
* **FREE_CONVERT_UPLOAD** = `"Free Convert upload"`
* **FREE_PDF_CONVERT_UPLOAD** = `"Free PDF Convert upload"`
* **GIT_HUB_UPLOAD** = `"GitHub upload"`
* **GIT_HUB_PAGES_UPLOAD** = `"GitHub Pages upload"`
* **GIT_LAB_UPLOAD** = `"GitLab upload"`
* **GMAIL_UPLOAD** = `"Gmail upload"`
* **GMX_UPLOAD** = `"GMX upload"`
* **GOOGLE_APPS_SCRIPT_UPLOAD** = `"Google Apps Script upload"`
* **GOOGLE_CHAT_UPLOAD** = `"Google Chat upload"`
* **GOOGLE_CLOUD_SHELL_UPLOAD** = `"Google Cloud Shell upload"`
* **GOOGLE_DRIVE_UPLOAD** = `"Google Drive upload"`
* **GOOGLE_HANGOUTS_UPLOAD** = `"Google Hangouts upload"`
* **GOOGLE_JAMBOARD_UPLOAD** = `"Google Jamboard upload"`
* **GOOGLE_KEEP_UPLOAD** = `"Google Keep upload"`
* **GOOGLE_MESSAGES_UPLOAD** = `"Google Messages upload"`
* **GOOGLE_SITES_UPLOAD** = `"Google Sites upload"`
* **HEIC_TO_JPEG_UPLOAD** = `"HEICtoJPEG upload"`
* **ICLOUD_MAIL_UPLOAD** = `"iCloud Mail upload"`
* **ICLOUD_UPLOAD** = `"iCloud upload"`
* **I_LOVE_PDF_UPLOAD** = `"iLovePDF upload"`
* **IMAGE_COLOR_PICKER_UPLOAD** = `"Image Color Picker upload"`
* **IMGUR_UPLOAD** = `"Imgur upload"`
* **JPG2_PDF_UPLOAD** = `"JPG2PDF upload"`
* **KAPWING_UPLOAD** = `"Kapwing upload"`
* **LINKED_IN_UPLOAD** = `"LinkedIn upload"`
* **LYCOS_UPLOAD** = `"Lycos upload"`
* **MAIL_COM_UPLOAD** = `"Mail.com upload"`
* **MEGA_UPLOAD** = `"Mega upload"`
* **MICROSOFT_TEAMS_UPLOAD** = `"Microsoft Teams upload"`
* **MIRO_UPLOAD** = `"Miro upload"`
* **MONDAY_UPLOAD** = `"Monday upload"`
* **MURAL_UPLOAD** = `"Mural upload"`
* **NOTION_UPLOAD** = `"Notion upload"`
* **ODNOKLASSNIKI_UPLOAD** = `"Odnoklassniki upload"`
* **OK_UPLOAD** = `"OK upload"`
* **ONE_DRIVE_UPLOAD** = `"OneDrive upload"`
* **ONE_SIX_THREE_DOT_COM_UPLOAD** = `"163.com upload"`
* **ONE_TWO_SIX_DOT_COM_UPLOAD** = `"126.com upload"`
* **OPEN_TEXT_HIGHTAIL_UPLOAD** = `"OpenText Hightail upload"`
* **OTHER_DESTINATION** = `"Other destination"`
* **OUTLOOK_UPLOAD** = `"Outlook upload"`
* **OVERLEAF_UPLOAD** = `"Overleaf upload"`
* **PDF24_TOOLS_UPLOAD** = `"PDF24 Tools upload"`
* **PDF_ESCAPE_UPLOAD** = `"PDFescape upload"`
* **PDF_FILLER_UPLOAD** = `"pdfFiller upload"`
* **PDF_SIMPLI_UPLOAD** = `"PDFSimpli upload"`
* **PHOTOPEA_UPLOAD** = `"Photopea upload"`
* **PIXLR_UPLOAD** = `"Pixlr upload"`
* **PROTON_MAIL_UPLOAD** = `"ProtonMail upload"`
* **PUBLIC_LINK_FROM_CORPORATE_BOX** = `"Public link from corporate Box"`
* **PUBLIC_LINK_FROM_CORPORATE_GOOGLE_DRIVE** = `"Public link from corporate Google Drive"`
* **PUBLIC_LINK_FROM_CORPORATE_ONE_DRIVE** = `"Public link from corporate OneDrive"`
* **QQMAIL_UPLOAD** = `"QQMail upload"`
* **QZONE_UPLOAD** = `"Qzone upload"`
* **REDDIT_UPLOAD** = `"Reddit upload"`
* **REMOVABLE_MEDIA** = `"Removable media"`
* **REMOVE_DOT_BG_UPLOAD** = `"remove.bg upload"`
* **SALESFORCE_DOWNLOAD** = `"Download to unmonitored device from corporate Salesforce"`
* **SECURE_FIRM_PORTAL_UPLOAD** = `"Secure Firm Portal upload"`
* **SEJDA_UPLOAD** = `"Sejda upload"`
* **SENT_FROM_CORPORATE_GMAIL** = `"Sent from corporate Gmail"`
* **SENT_FROM_CORPORATE_OFFICE365** = `"Sent from corporate Microsoft Office 365"`
* **SHARED_FROM_CORPORATE_BOX** = `"Shared from corporate Box"`
* **SHARED_FROM_CORPORATE_GOOGLE_DRIVE** = `"Shared from corporate Google Drive"`
* **SHARED_FROM_CORPORATE_ONE_DRIVE** = `"Shared from corporate OneDrive"`
* **SHAREFILE_UPLOAD** = `"Sharefile upload"`
* **SINA_MAIL_UPLOAD** = `"Sina Mail upload"`
* **SLACK_UPLOAD** = `"Slack upload"`
* **SMALL_PDF_UPLOAD** = `"SmallPDF upload"`
* **SMART_VAULT_UPLOAD** = `"SmartVault upload"`
* **SODA_PDF_UPLOAD** = `"Soda PDF upload"`
* **SOHU_MAIL_UPLOAD** = `"Sohu Mail upload"`
* **SOURCE_FORGE_UPLOAD** = `"SourceForge upload"`
* **STACK_OVERFLOW_UPLOAD** = `"Stack Overflow upload"`
* **STASH_UPLOAD** = `"Stash upload"`
* **SUGAR_SYNC_UPLOAD** = `"SugarSync upload"`
* **TELEGRAM_UPLOAD** = `"Telegram upload"`
* **TINY_PNG_UPLOAD** = `"TinyPNG upload"`
* **TRELLO_UPLOAD** = `"Trello upload"`
* **TUMBLR_UPLOAD** = `"Tumblr upload"`
* **TUTANOTA_UPLOAD** = `"Tutanota upload"`
* **TWITCH_UPLOAD** = `"Twitch upload"`
* **TWITTER_UPLOAD** = `"Twitter upload"`
* **UNKNOWN_DESTINATION** = `"Unknown destination"`
* **UNMONITORED_DEVICE_DOWNLOAD_BOX** = `"Download to unmonitored device from corporate Box"`
* **UNMONITORED_DEVICE_DOWNLOAD_GOOGLE_DRIVE** = `"Download to unmonitored device from corporate Google Drive"`
* **UNMONITORED_DEVICE_DOWNLOAD_ONE_DRIVE** = `"Download to unmonitored device from corporate OneDrive"`
* **VEED_UPLOAD** = `"VEED upload"`
* **VIMEO_UPLOAD** = `"Vimeo upload"`
* **VK_UPLOAD** = `"Vk upload"`
* **WEBEX_UPLOAD** = `"Webex upload"`
* **WE_CHAT_UPLOAD** = `"WeChat upload"`
* **WEIBO_UPLOAD** = `"Weibo upload"`
* **WE_TRANSFER_UPLOAD** = `"WeTransfer upload"`
* **WHATS_APP_UPLOAD** = `"WhatsApp upload"`
* **WIX_UPLOAD** = `"Wix upload"`
* **WORD_PRESS_UPLOAD** = `"WordPress upload"`
* **YAHOO_UPLOAD** = `"Yahoo upload"`
* **YOU_TUBE_UPLOAD** = `"YouTube upload"`
* **ZIX_UPLOAD** = `"Zix upload"`
* **ZOHO_MAIL_UPLOAD** = `"Zoho Mail upload"`
* **ZOHO_WORK_DRIVE_UPLOAD** = `"Zoho WorkDrive upload"`
* **ZOOM_UPLOAD** = `"Zoom upload"`

#### Risk Indicators - User Behavior

* **FILE_MISMATCH** = `"File mismatch"`
* **OFF_HOURS** = `"Off hours"`
* **REMOTE** = `"Remote"`
* **FIRST_DESTINATION_USE** = `"First use of destination"`
* **RARE_DESTINATION_USE** = `"Rare use of destination"`
* **CONTRACT** = `"Contract"`
* **DEPARTING** = `"Departing"`
* **ELEVATED_ACCESS** = `"Elevated access"`
* **FLIGHT_RISK** = `"Flight risk"`
* **HIGH_IMPACT** = `"High impact"`
* **HIGH_RISK** = `"High risk"`
* **PERFORMANCE_CONCERNS** = `"Performance concerns"`
* **POOR_SECURITY_PRACTICES** = `"Poor security practices"`
* **SUSPICIOUS_SYSTEM_ACTIVITY** = `"Suspicious system activity"`

#### Risk Indicators - File Categories

* **AUDIO** = `"Audio"`
* **DOCUMENT** = `"Document"`
* **EXECUTABLE** = `"Executable"`
* **IMAGE** = `"Image"`
* **PDF** = `"PDF"`
* **PRESENTATION** = `"Presentation"`
* **SCRIPT** = `"Script"`
* **SOURCE_CODE** = `"Source code"`
* **SPREADSHEET** = `"Spreadsheet"`
* **VIDEO** = `"Video"`
* **VIRTUAL_DISK_IMAGE** = `"Virtual Disk Image"`
* **ZIP** = `"Zip"`

### Trust Reasons

::: incydr.enums.file_events.TrustReason
    :docstring:

* **TRUSTED_DOMAIN_BROWSER_URL** = `"Trusted browser URL"`
* **TRUSTED_BROWSER_URL_PATH** = `"Trusted specific URL path"`
* **TRUSTED_DOMAIN_BROWSER_TAB_TITLE** = `"Trusted browser tab title"`
* **TRUSTED_BROWSER_TAB_INFOS** = `"Trusted browser URL and/or tab title"`
* **TRUSTED_DOMAIN_EMAIL_RECIPIENT** = `"Trusted email recipient"`
* **TRUSTED_DOMAIN_CLOUD_SYNC_USERNAME** = `"Trusted sync username"`
* **TRUSTED_SLACK_WORKSPACE** = `"Trusted Slack workspace"`
* **EVENT_PAIRING_SERVICE_MATCH** = `"Event matched with cloud activity"`
* **EVENT_PAIRING_SERVICE_ENDPOINT_MATCH** = `"Event matched with endpoint activity"`
* **DOWNLOAD_TO_A_MANAGED_DEVICE** = `"Download to a managed device"`
* **SHARED_WITH_TRUSTED_USERS** = `"Shared with trusted users"`

### Risk Severity

::: incydr.enums.file_events.RiskSeverity
    :docstring:

* **CRITICAL** = `"CRITICAL"`
* **HIGH** = `"HIGH"`
* **MODERATE** = `"MODERATE"`
* **LOW** = `"LOW"`
* **NO_RISK_INDICATED** = `"NO_RISK_INDICATED"`

## Watchlists

### Watchlist Types

::: incydr.enums.watchlists.WatchlistType
    :docstring:

* **WATCHLIST_TYPE_UNSPECIFIED** = `"WATCHLIST_TYPE_UNSPECIFIED"`
* **CONTRACT_EMPLOYEE** = `"CONTRACT_EMPLOYEE"`
* **DEPARTING_EMPLOYEE** = `"DEPARTING_EMPLOYEE"`
* **ELEVATED_ACCESS_PRIVILEGES** = `"ELEVATED_ACCESS_PRIVILEGES"`
* **FLIGHT_RISK** = `"FLIGHT_RISK"`
* **HIGH_IMPACT_EMPLOYEE** = `"HIGH_IMPACT_EMPLOYEE"`
* **NEW_EMPLOYEE** = `"NEW_EMPLOYEE"`
* **PERFORMANCE_CONCERNS** = `"PERFORMANCE_CONCERNS"`
* **POOR_SECURITY_PRACTICES** = `"POOR_SECURITY_PRACTICES"`
* **SUSPICIOUS_SYSTEM_ACTIVITY** = `"SUSPICIOUS_SYSTEM_ACTIVITY"`
* **CUSTOM** = `"CUSTOM"`
