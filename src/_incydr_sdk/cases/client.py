from datetime import datetime
from itertools import count
from pathlib import Path
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union

from requests import Response

from _incydr_sdk.cases.models import Case
from _incydr_sdk.cases.models import CaseDetail
from _incydr_sdk.cases.models import CaseFileEvents
from _incydr_sdk.cases.models import CasesPage
from _incydr_sdk.cases.models import CreateCaseRequest
from _incydr_sdk.cases.models import QueryCasesRequest
from _incydr_sdk.cases.models import UpdateCaseRequest
from _incydr_sdk.core.utils import get_filename_from_content_disposition
from _incydr_sdk.enums import SortDirection
from _incydr_sdk.enums.cases import CaseStatus
from _incydr_sdk.enums.cases import SortKeys
from _incydr_sdk.file_events.models.event import FileEventV2
from _incydr_sdk.queries.utils import MICROSECOND_FORMAT


class CasesV1:
    """
    Client for `/v1/cases` endpoints.

    Usage example:

        >>> import incydr
        >>> client = incydr.Client(**kwargs)
        >>> client.cases.v1.get_case(23)
    """

    def __init__(self, parent):
        self._parent = parent

    def create(
        self,
        name: str,
        subject: str = None,
        assignee: str = None,
        description: str = None,
        findings: str = None,
    ) -> CaseDetail:
        """
        Create a case.

        **Parameters:**

        * **name**: `str` (required) The unique name given to the case.
        * **subject**: `str` The user UID of the subject being investigated in this case.
        * **assignee**: `str` The user UID of the administrator assigned to investigate the case.
        * **findings**: `str` Markdown formatted text summarizing the findings for a case.
        * **description**: `str` Brief description providing context for a case.

        **Returns**: A [`Case`][case-model] object representing the newly created case.
        """
        data = CreateCaseRequest(
            name=name,
            subject=subject,
            assignee=assignee,
            findings=findings,
            description=description,
        )
        response = self._parent.session.post(url="/v1/cases", json=data.dict())
        return CaseDetail.parse_response(response)

    def delete(self, case_number: Union[int, Case]) -> Response:
        """
        Delete a case.

        **Parameters**:

        * **case_number** `int | Case` Unique numeric identifier for the case or a [`Case`](../models/#case) object.

        Usage example:

            >>> client.cases.v1.delete(23)
            <Response [204]>

            # Alternatively:
            >>> case = client.cases.v1.get_case(23)
            >>> client.cases.v1.delete(case)

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(case_number, Case):
            case_number = case_number.number
        return self._parent.session.delete(f"/v1/cases/{case_number}")

    def get_case(self, case_number: int) -> CaseDetail:
        """
        Get a single case.

        **Parameters**:

        * **case_number**: `int` Unique numeric identifier for the case.

        **Returns**: A [`Case`][case-model] object representing the case.
        """
        response = self._parent.session.get(f"/v1/cases/{case_number}")
        return CaseDetail.parse_response(response)

    def get_page(
        self,
        assignee: str = None,
        created_at: Tuple[datetime, datetime] = None,
        is_assigned: bool = None,
        last_modified_by: str = None,
        name: str = None,
        status: CaseStatus = None,
        page_num: int = 1,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NUMBER,
    ) -> CasesPage:
        """
        Get a page of cases.

        Filter results by passing appropriate parameters:

        **Parameters**:

        * **assignee**: `str` - User UID of an assignee of a case on which to filter.
        * **created_at**: `Tuple[datetime, datetime]` - Filter cases created between the supplied start and end times.
        * **is_assigned**: `bool` - Filter cases with an assignee (`True`) or without (`False`).
        * **last_modified_by**: `str` - User UID of the user who most recently modified the case.
        * **name**: str - Name of a case on which to filter; will include partial matches.
        * **status**: [`CaseStatus`][case-statuses] - One or more case statuses on which to filter. Available values: `OPEN`, `CLOSED`
        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page. Defaults to client's `page_size` setting.
        * **sort_dir**: `SortDirection` - The direction on which to sort the response, based on the corresponding key.
        * **sort_key**: [`SortKeys`][cases-sort-keys] - One or more values on which the response will be sorted.

        **Returns**: A [`CasesPage`][casespage-model] object.
        """

        if created_at is not None:
            if not isinstance(created_at, (Tuple, list)):
                raise TypeError(
                    f"created_at kwarg should be a Tuple[datetime, datetime] object"
                    f", passed 'created_at={created_at}' of type: {type(created_at)}"
                )
            else:
                created_at = f"{created_at[0].strftime(MICROSECOND_FORMAT)}/{created_at[1].strftime(MICROSECOND_FORMAT)}"

        data = QueryCasesRequest(
            assignee=assignee,
            createdAt=created_at,
            isAssigned=is_assigned,
            lastModifiedBy=last_modified_by,
            name=name,
            status=status,
            pgNum=page_num,
            pgSize=page_size or self._parent.settings.page_size,
            srtDir=sort_dir,
            srtKey=sort_key,
        )
        response = self._parent.session.get("/v1/cases", params=data.dict())
        return CasesPage.parse_response(response)

    def iter_all(
        self,
        assignee: str = None,
        created_at: Tuple[datetime, datetime] = None,
        is_assigned: bool = None,
        last_modified_by: str = None,
        name: str = None,
        status: CaseStatus = None,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NUMBER,
    ) -> Iterator[Case]:
        """
        Iterate over all cases.

        Accepts the same parameters as `.get_page()` excepting `page_num`.

        **Returns**: A generator yielding individual [`Case`][case-model] objects.
        """
        page_size = page_size or self._parent.settings.page_size
        for page_num in count(1):
            page = self.get_page(
                assignee=assignee,
                created_at=created_at,
                is_assigned=is_assigned,
                last_modified_by=last_modified_by,
                name=name,
                status=status,
                page_num=page_num,
                page_size=page_size,
                sort_dir=sort_dir,
                sort_key=sort_key,
            )
            yield from page.cases
            if len(page.cases) < page_size:
                break

    def update(self, case: Union[Case, CaseDetail]):
        """
        Updates a case.
        Valid updatable fields: name, assignee, description, findings, subject, status

        **Parameters**

        * **case**: [`Case`][case-model] The modified case object.

        Usage example:

            >>> case = client.cases.v1.get_case(23)
            >>> case.name = "Updated name"
            >>> client.cases.v1.update(case)

        **Returns**: A [`Case`][case-model] object with updated values from server.
        """
        data = UpdateCaseRequest(**case.dict())
        response = self._parent.session.put(
            f"/v1/cases/{case.number}", json=data.dict()
        )
        return CaseDetail.parse_response(response)

    def download_summary_pdf(
        self, case_number: int, target_folder: Union[str, Path]
    ) -> Path:
        """
        Downloads a summary of a case in PDF format to specified target folder.

        **Parameters**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **target_folder**: `Path | str` A string or `pathlib.Path` object that represents the folder which the PDF
            will be saved to.

        **Returns**: A `pathlib.Path` object representing location of the downloaded PDF.
        """
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        if not folder.is_dir():
            raise ValueError(
                f"`target_folder` argument must resolve to a folder: {target_folder}"
            )
        response = self._parent.session.get(f"/v1/cases/{case_number}/export")
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}.pdf"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def download_file_event_csv(self, case_number: int, target_folder: Path) -> Path:
        """
        Downloads all file event data for a case in CSV format to specified target folder.

        **Parameters**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **target_folder**: `Path | str` A string or `pathlib.Path` object that represents the folder which the CSV
            will be saved to.

        **Returns**: A `pathlib.Path` object representing location of the downloaded CSV.
        """
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        if not folder.is_dir():
            raise ValueError(
                f"`target_folder` argument must resolve to a folder: {target_folder}"
            )
        response = self._parent.session.get(f"/v1/cases/{case_number}/fileevent/export")
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}-file-events.csv"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def download_full_case_zip(
        self,
        case_number,
        target_folder: Path,
        include_files=True,
        include_summary=True,
        include_file_events=True,
    ) -> Path:
        """
        Downloads full export of case in ZIP format to specified target folder.

        **Parameters**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **target_folder**: `Path | str` A string or `pathlib.Path` object that represents the folder which the ZIP
            will be saved to.
        * **include_files**: `bool` Include source files (if they are available) in the .zip. default=True
        * **include_summary**: `bool` Include summary PDF in the .zip. default=True
        * **include_file_events**: `bool` Include file events .csv in the .zip. default=True

        **Returns**: A `pathlib.Path` object representing location of the downloaded ZIP.
        """
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        response = self._parent.session.get(
            f"/v1/cases/{case_number}/export/full",
            params={
                "files": include_files,
                "summary": include_summary,
                "fileEvents": include_file_events,
            },
        )
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}.zip"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def download_file_for_event(
        self, case_number: int, event_id: str, target_folder: Path
    ) -> Path:
        """
        Download the source file (if captured) from a file event attached to a case.

        **Parameters**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **event_id**: `str` Unique identifier for event to download.
        * **target_folder**: `Path | str` A string or `pathlib.Path` object that represents the folder which the file
            will be saved to.

        **Returns**: A `pathlib.Path` object representing location of the downloaded file.
        """
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        response = self._parent.session.get(
            f"/v1/cases/{case_number}/fileevent/{event_id}/file"
        )
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}-{event_id}-unknown-filename"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def get_file_events(
        self, case_number: int, page_num: int = 1, page_size: int = None
    ) -> CaseFileEvents:
        """
        Get abbreviated details for file events attached to a case.

        **Parameters**

        * **case_number**: `int` - Unique numeric identifier for the case.
        * **page_num**: `int` - Page number for results, starting at 1.
        * **page_size**: `int` - Max number of results to return for a page. Defaults to client's `page_size` setting.

        **Returns**: A [`CaseFileEvents`][casefileevents-model] object containing the associated file events.
        """
        params = {
            "pgNum": page_num,
            "pgSize": page_size or self._parent.settings.page_size,
        }
        r = self._parent.session.get(
            f"/v1/cases/{case_number}/fileevent", params=params
        )
        return CaseFileEvents.parse_response(r)

    def add_file_events_to_case(
        self, case_number: int, event_ids: Union[str, List[str]]
    ) -> Response:
        """
        Attach file events to a case.

        **Parameters:**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **event_ids**: `str | List[str]` A string or list of strings representing the eventId(s) to attach to the
            case.

        **Returns**: A `requests.Response` indicating success.
        """
        if isinstance(event_ids, str):
            event_ids = [event_ids]
        return self._parent.session.post(
            f"/v1/cases/{case_number}/fileevent", json={"events": event_ids}
        )

    def delete_file_event_from_case(self, case_number: int, event_id: str) -> Response:
        """
        Remove file events from a case.

        **Parameters:**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **event_id**: `str` Unique identifier of event to remove from the case.

        **Returns**: A `requests.Response` indicating success.
        """
        return self._parent.session.delete(
            f"/v1/cases/{case_number}/fileevent/{event_id}"
        )

    def get_file_event_detail(self, case_number: int, event_id: str):
        """
        Get the full detail for a given file event attached to a case.

        **Parameters**

        * **case_number**: `int` Unique numeric identifier for the case.
        * **event_id**: `str` Unique identifier for event associated with case.

        **Returns**:  A [`FileEventV2`][fileevent-model] object representing the file event.
        """
        response = self._parent.session.get(
            f"/v1/cases/{case_number}/fileevent/{event_id}"
        )
        return FileEventV2.parse_response(response)


class CasesClient:
    def __init__(self, parent):
        self._parent = parent
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = CasesV1(self._parent)
        return self._v1
