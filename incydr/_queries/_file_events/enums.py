from enum import Enum
from enum import EnumMeta

# Create search term enums from list of valid strings.

search_terms = [
    "@timestamp",
    "event.id",
    "event.inserted",
    "event.action",
    "event.observer",
    "event.shareType",
    "event.ingested",
    "event.relatedEvents",
    "user.email",
    "user.id",
    "user.deviceUid",
    "file.name",
    "file.directory",
    "file.category",
    "file.mimeTypeByBytes",
    "file.categoryByBytes",
    "file.mimeTypeByExtension",
    "file.categoryByExtension",
    "file.sizeInBytes",
    "file.owner",
    "file.created",
    "file.modified",
    "file.hash.md5",
    "file.hash.sha256",
    "file.hash.md5Error",
    "file.hash.sha256Error",
    "report.id",
    "report.name",
    "report.description",
    "report.headers",
    "report.count",
    "report.type",
    "source.category",
    "source.name",
    "source.domain",
    "source.ip",
    "source.privateIp",
    "source.operatingSystem",
    "source.email.sender",
    "source.email.from",
    "destination.category",
    "destination.name",
    "destination.user.email",
    "process.executable",
    "process.owner",
    "risk.score",
    "risk.severity",
    "risk.indicators",
    "risk.trusted",
    "risk.trustReason",
]


def _create_enum_dict(term_list):
    d = {}
    for i in term_list:
        a = i.replace(".", "_").upper().strip("@")
        d[a] = i
    return d


class StrEnum(str, Enum):
    pass


search_term_dict = _create_enum_dict(search_terms)

EventTerms = Enum("EventTerms", search_term_dict, type=StrEnum)


class Operator(str, Enum):
    # all valid filter operators for querying file events
    IS = "IS"
    IS_NOT = "IS_NOT"
    EXISTS = "EXISTS"
    DOES_NOT_EXIST = "DOES_NOT_EXIST"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    ON = "ON"
    ON_OR_AFTER = "ON_OR_AFTER"
    ON_OR_BEFORE = "ON_OR_BEFORE"
    WITHIN_THE_LAST = "WITHIN_THE_LAST"


# Overriding the metaclass __contains__() functions lets us test if a string is a valid enum value.
class MetaEnum(EnumMeta):
    # https://stackoverflow.com/questions/10445819/overriding-contains-method-for-a-class/10446010#10446010
    # https://stackoverflow.com/questions/55220588/how-to-create-python-enum-class-from-existing-dict-with-additional-methods
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class FileCategory(str, Enum, metaclass=MetaEnum):
    """file category enum values."""

    AUDIO = "Audio"
    DOCUMENT = "Document"
    EXECUTABLE = "Executable"
    IMAGE = "Image"
    PDF = "Pdf"
    PRESENTATION = "Presentation"
    SCRIPT = "Script"
    SOURCE_CODE = "SourceCode"
    SPREADSHEET = "Spreadsheet"
    VIDEO = "Video"
    VIRTUAL_DISK_IMAGE = "VirtualDiskImage"
    ZIP = "Archive"


class EventAction(str, Enum, metaclass=MetaEnum):
    """event action enum values."""

    # Exposure Type in v1
    REMOVABLE_MEDIA_CREATED = "removable-media-created"
    REMOVABLE_MEDIA_MODIFIED = "removable-media-modified"
    REMOVABLE_MEDIA_DELETED = "removable-media-deleted"
    SYNC_APP_CREATED = "sync-app-created"
    SYNC_APP_MODIFIED = "sync-app-modified"
    SYNC_APP_DELETED = "sync-app-deleted"
    FILE_SHARED = "file-shared"

    # Event Type in v1
    FILE_CREATED = "file-created"
    FILE_DELETED = "file-deleted"
    FILE_DOWNLOADED = "file-downloaded"
    FILE_EMAILED = "file-emailed"
    FILE_MODIFIED = "file-modified"
    FILE_PRINTED = "file-printed"
    APPLICATION_READ = "application-read"


class Category(str, Enum, metaclass=MetaEnum):
    """source and destination category enum values."""

    BUSINESS_TOOLS = "Business Tools"
    CLOUD_STORAGE = "Cloud Storage"
    DEVICE = "Device"
    EMAIL = "Email"
    MESSAGING = "Messaging"
    MULTIPLE_POSSIBILITIES = "Multiple Possibilities"
    SOCIAL_MEDIA = "Social Media"
    SOURCE_CODE_REPOSITORY = "Source Code Repository"
    UNCATEGORIZED = "Uncategorized"
    UNKNOWN = "Unknown"
    BUSINESS_INTELLIGENCE_TOOLS = "Business Intelligence Tools"
    CIVIL_SERVICES = "Civil Services"
    CLOUD_COMPUTING = "Cloud Computing"
    CODING_TOOLS = "Coding Tools"
    CONTRACT_MANAGEMENT = "Contract Management"
    CRM_TOOLS = "CRM Tools"
    DESIGN_TOOLS = "Design Tools"
    E_COMMERCE = "E-commerce"
    FILE_CONVERSION_TOOLS = "File Conversion Tools"
    FINANCIAL_SERVICES = "Financial Services"
    HEALTHCARE_AND_INSURANCE = "Healthcare & Insurance"
    HR_TOOLS = "HR Tools"
    IMAGE_HOSTING = "Image Hosting"
    IT_SERVICES = "IT Services"
    JOB_LISTINGS = "Job Listings"
    LEARNING_PLATFORMS = "Learning Platforms"
    MARKETING_TOOLS = "Marketing Tools"
    PDF_MANAGER = "PDF Manager"
    PHOTO_PRINTING = "Photo Printing"
    PRODUCTIVITY_TOOLS = "Productivity Tools"
    PROFESSIONAL_SERVICES = "Professional Services"
    REAL_ESTATE = "Real Estate"
    SALES_TOOLS = "Sales Tools"
    SEARCH_ENGINE = "Search Engine"
    SHIPPING = "Shipping"
    SOFTWARE = "Software"
    TRAVEL = "Travel"
    WEB_HOSTING = "Web Hosting"


class ShareType(str, Enum, metaclass=MetaEnum):
    """share type enum values."""

    PUBLIC_LINK_SHARE = "Anyone with the link"
    DOMAIN_SHARE = "Anyone in your organization"
    DIRECT_USER_SHARE = "Shared with specific people"


class ReportType(str, Enum, metaclass=MetaEnum):
    """report type enum values."""

    AD_HOC = "REPORT_TYPE_AD_HOC"
    SAVED = "REPORT_TYPE_SAVED"


class RiskIndicators(str, Enum, metaclass=MetaEnum):
    """risk indicators enum values."""

    # Destinations
    ADOBE_UPLOAD = "Adobe upload"
    ADOBE_ACROBAT_UPLOAD = "Adobe Acrobat upload"
    AIR_DROP = "AirDrop"
    AMAZON_DRIVE_UPLOAD = "Amazon Drive upload"
    AOL_UPLOAD = "AOL upload"
    BAIDU_NET_DISK_UPLOAD = "Baidu NetDisk upload"
    BITBUCKET_UPLOAD = "Bitbucket upload"
    BOX_UPLOAD = "Box upload"
    CANVA_UPLOAD = "Canva upload"
    CLOUD_CONVERT_UPLOAD = "CloudConvert upload"
    COLABORATORY_UPLOAD = "Colaboratory upload"
    COMBINE_PDF_UPLOAD = "CombinePDF upload"
    COMCAST_UPLOAD = "Comcast upload"
    COMPRESS_JPEG_UPLOAD = "Compress JPEG upload"
    CRASHPLAN_UPLOAD = "Crashplan upload"
    DISCORD_UPLOAD = "Discord upload"
    DRAKE_PORTALS_UPLOAD = "Drake Portals upload"
    DROPBOX_UPLOAD = "Dropbox upload"
    EVERNOTE_UPLOAD = "Evernote upload"
    FACEBOOK_MESSENGER_UPLOAD = "Facebook Messenger upload"
    FACEBOOK_UPLOAD = "Facebook upload"
    FASTMAIL_UPLOAD = "Fastmail upload"
    FIGMA_UPLOAD = "Figma upload"
    FILE_DOT_IO_UPLOAD = "File.io upload"
    FILESTACK_UPLOAD = "Filestack upload"
    FOUR_CHAN_UPLOAD = "4chan upload"
    FREE_CONVERT_UPLOAD = "Free Convert upload"
    FREE_PDF_CONVERT_UPLOAD = "Free PDF Convert upload"
    GIT_HUB_UPLOAD = "GitHub upload"
    GIT_HUB_PAGES_UPLOAD = "GitHub Pages upload"
    GIT_LAB_UPLOAD = "GitLab upload"
    GMAIL_UPLOAD = "Gmail upload"
    GMX_UPLOAD = "GMX upload"
    GOOGLE_APPS_SCRIPT_UPLOAD = "Google Apps Script upload"
    GOOGLE_CHAT_UPLOAD = "Google Chat upload"
    GOOGLE_CLOUD_SHELL_UPLOAD = "Google Cloud Shell upload"
    GOOGLE_DRIVE_UPLOAD = "Google Drive upload"
    GOOGLE_HANGOUTS_UPLOAD = "Google Hangouts upload"
    GOOGLE_JAMBOARD_UPLOAD = "Google Jamboard upload"
    GOOGLE_KEEP_UPLOAD = "Google Keep upload"
    GOOGLE_MESSAGES_UPLOAD = "Google Messages upload"
    GOOGLE_SITES_UPLOAD = "Google Sites upload"
    HEIC_TO_JPEG_UPLOAD = "HEICtoJPEG upload"
    ICLOUD_MAIL_UPLOAD = "iCloud Mail upload"
    ICLOUD_UPLOAD = "iCloud upload"
    I_LOVE_PDF_UPLOAD = "iLovePDF upload"
    IMAGE_COLOR_PICKER_UPLOAD = "Image Color Picker upload"
    IMGUR_UPLOAD = "Imgur upload"
    JPG2_PDF_UPLOAD = "JPG2PDF upload"
    KAPWING_UPLOAD = "Kapwing upload"
    LINKED_IN_UPLOAD = "LinkedIn upload"
    LYCOS_UPLOAD = "Lycos upload"
    MAIL_COM_UPLOAD = "Mail.com upload"
    MEGA_UPLOAD = "Mega upload"
    MICROSOFT_TEAMS_UPLOAD = "Microsoft Teams upload"
    MIRO_UPLOAD = "Miro upload"
    MONDAY_UPLOAD = "Monday upload"
    MURAL_UPLOAD = "Mural upload"
    NOTION_UPLOAD = "Notion upload"
    ODNOKLASSNIKI_UPLOAD = "Odnoklassniki upload"
    OK_UPLOAD = "OK upload"
    ONE_DRIVE_UPLOAD = "OneDrive upload"
    ONE_SIX_THREE_DOT_COM_UPLOAD = "163.com upload"
    ONE_TWO_SIX_DOT_COM_UPLOAD = "126.com upload"
    OPEN_TEXT_HIGHTAIL_UPLOAD = "OpenText Hightail upload"
    OTHER_DESTINATION = "Other destination"
    OUTLOOK_UPLOAD = "Outlook upload"
    OVERLEAF_UPLOAD = "Overleaf upload"
    PDF24_TOOLS_UPLOAD = "PDF24 Tools upload"
    PDF_ESCAPE_UPLOAD = "PDFescape upload"
    PDF_FILLER_UPLOAD = "pdfFiller upload"
    PDF_SIMPLI_UPLOAD = "PDFSimpli upload"
    PHOTOPEA_UPLOAD = "Photopea upload"
    PIXLR_UPLOAD = "Pixlr upload"
    PROTON_MAIL_UPLOAD = "ProtonMail upload"
    PUBLIC_LINK_FROM_CORPORATE_BOX = "Public link from corporate Box"
    PUBLIC_LINK_FROM_CORPORATE_GOOGLE_DRIVE = "Public link from corporate Google Drive"
    PUBLIC_LINK_FROM_CORPORATE_ONE_DRIVE = "Public link from corporate OneDrive"
    QQMAIL_UPLOAD = "QQMail upload"
    QZONE_UPLOAD = "Qzone upload"
    REDDIT_UPLOAD = "Reddit upload"
    REMOVABLE_MEDIA = "Removable media"
    REMOVE_DOT_BG_UPLOAD = "remove.bg upload"
    SALESFORCE_DOWNLOAD = "Download to unmonitored device from corporate Salesforce"
    SECURE_FIRM_PORTAL_UPLOAD = "Secure Firm Portal upload"
    SEJDA_UPLOAD = "Sejda upload"
    SENT_FROM_CORPORATE_GMAIL = "Sent from corporate Gmail"
    SENT_FROM_CORPORATE_OFFICE365 = "Sent from corporate Microsoft Office 365"
    SHARED_FROM_CORPORATE_BOX = "Shared from corporate Box"
    SHARED_FROM_CORPORATE_GOOGLE_DRIVE = "Shared from corporate Google Drive"
    SHARED_FROM_CORPORATE_ONE_DRIVE = "Shared from corporate OneDrive"
    SHAREFILE_UPLOAD = "Sharefile upload"
    SINA_MAIL_UPLOAD = "Sina Mail upload"
    SLACK_UPLOAD = "Slack upload"
    SMALL_PDF_UPLOAD = "SmallPDF upload"
    SMART_VAULT_UPLOAD = "SmartVault upload"
    SODA_PDF_UPLOAD = "Soda PDF upload"
    SOHU_MAIL_UPLOAD = "Sohu Mail upload"
    SOURCE_FORGE_UPLOAD = "SourceForge upload"
    STACK_OVERFLOW_UPLOAD = "Stack Overflow upload"
    STASH_UPLOAD = "Stash upload"
    SUGAR_SYNC_UPLOAD = "SugarSync upload"
    TELEGRAM_UPLOAD = "Telegram upload"
    TINY_PNG_UPLOAD = "TinyPNG upload"
    TRELLO_UPLOAD = "Trello upload"
    TUMBLR_UPLOAD = "Tumblr upload"
    TUTANOTA_UPLOAD = "Tutanota upload"
    TWITCH_UPLOAD = "Twitch upload"
    TWITTER_UPLOAD = "Twitter upload"
    UNKNOWN_DESTINATION = "Unknown destination"
    UNMONITORED_DEVICE_DOWNLOAD_BOX = (
        "Download to unmonitored device from corporate Box"
    )
    UNMONITORED_DEVICE_DOWNLOAD_GOOGLE_DRIVE = (
        "Download to unmonitored device from corporate Google Drive"
    )
    UNMONITORED_DEVICE_DOWNLOAD_ONE_DRIVE = (
        "Download to unmonitored device from corporate OneDrive"
    )
    VEED_UPLOAD = "VEED upload"
    VIMEO_UPLOAD = "Vimeo upload"
    VK_UPLOAD = "Vk upload"
    WEBEX_UPLOAD = "Webex upload"
    WE_CHAT_UPLOAD = "WeChat upload"
    WEIBO_UPLOAD = "Weibo upload"
    WE_TRANSFER_UPLOAD = "WeTransfer upload"
    WHATS_APP_UPLOAD = "WhatsApp upload"
    WIX_UPLOAD = "Wix upload"
    WORD_PRESS_UPLOAD = "WordPress upload"
    YAHOO_UPLOAD = "Yahoo upload"
    YOU_TUBE_UPLOAD = "YouTube upload"
    ZIX_UPLOAD = "Zix upload"
    ZOHO_MAIL_UPLOAD = "Zoho Mail upload"
    ZOHO_WORK_DRIVE_UPLOAD = "Zoho WorkDrive upload"
    ZOOM_UPLOAD = "Zoom upload"

    # User behavior
    FILE_MISMATCH = "File mismatch"
    OFF_HOURS = "Off hours"
    REMOTE = "Remote"
    FIRST_DESTINATION_USE = "First use of destination"
    RARE_DESTINATION_USE = "Rare use of destination"
    CONTRACT = "Contract"
    DEPARTING = "Departing"
    ELEVATED_ACCESS = "Elevated access"
    FLIGHT_RISK = "Flight risk"
    HIGH_IMPACT = "High impact"
    HIGH_RISK = "High risk"
    PERFORMANCE_CONCERNS = "Performance concerns"
    POOR_SECURITY_PRACTICES = "Poor security practices"
    SUSPICIOUS_SYSTEM_ACTIVITY = "Suspicious system activity"

    # File categories
    AUDIO = "Audio"
    DOCUMENT = "Document"
    EXECUTABLE = "Executable"
    IMAGE = "Image"
    PDF = "PDF"
    PRESENTATION = "Presentation"
    SCRIPT = "Script"
    SOURCE_CODE = "Source code"
    SPREADSHEET = "Spreadsheet"
    VIDEO = "Video"
    VIRTUAL_DISK_IMAGE = "Virtual Disk Image"
    ZIP = "Zip"


class TrustReason(str, Enum, metaclass=MetaEnum):
    """trust reason enum values."""

    TRUSTED_DOMAIN_BROWSER_URL = "Trusted browser URL"
    TRUSTED_BROWSER_URL_PATH = "Trusted specific URL path"
    TRUSTED_DOMAIN_BROWSER_TAB_TITLE = "Trusted browser tab title"
    TRUSTED_BROWSER_TAB_INFOS = "Trusted browser URL and/or tab title"
    TRUSTED_DOMAIN_EMAIL_RECIPIENT = "Trusted email recipient"
    TRUSTED_DOMAIN_CLOUD_SYNC_USERNAME = "Trusted sync username"
    TRUSTED_SLACK_WORKSPACE = "Trusted Slack workspace"
    EVENT_PAIRING_SERVICE_MATCH = "Event matched with cloud activity"
    EVENT_PAIRING_SERVICE_ENDPOINT_MATCH = "Event matched with endpoint activity"
    DOWNLOAD_TO_A_MANAGED_DEVICE = "Download to a managed device"
    SHARED_WITH_TRUSTED_USERS = "Shared with trusted users"


class RiskSeverity(str, Enum, metaclass=MetaEnum):
    """risk severity enum values."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    NO_RISK_INDICATED = "NO_RISK_INDICATED"
