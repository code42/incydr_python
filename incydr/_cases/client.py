from datetime import datetime
from itertools import count
from pathlib import Path
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union

from requests import Response

from .models import Case
from .models import CaseFileEventsResponse
from .models import CasesPage
from .models import CreateCaseRequest
from .models import QueryCasesRequest
from .models import SortKeys
from .models import Status
from .models import UpdateCaseRequest
from incydr._core.util import get_filename_from_content_disposition
from incydr._core.util import SortDirection
from incydr._file_events.models import FileEventV2


class CasesV1:
    """Cases V1 Client"""

    default_page_size = 100

    def __init__(self, session):
        self._session = session

    def create(
        self,
        name: str,
        subject: str = None,
        assignee: str = None,
        description: str = None,
        findings: str = None,
    ) -> Case:
        """Create a case."""
        data = CreateCaseRequest(
            name=name,
            subject=subject,
            assignee=assignee,
            findings=findings,
            description=description,
        )
        response = self._session.post(url="/v1/cases", json=data.dict())
        return Case.parse_response(response)

    def delete(self, case_number: Union[int, Case]) -> Response:
        """Delete a case."""
        if isinstance(case_number, Case):
            case_number = case_number.number
        return self._session.delete(f"/v1/cases/{case_number}")

    def get_case(self, case_number: int) -> Case:
        """Get a single case."""
        response = self._session.get(f"/v1/cases/{case_number}")
        return Case(**response.json())

    def get_page(
        self,
        assignee: str = None,
        created_at: Tuple[datetime, datetime] = None,
        is_assigned: bool = None,
        last_modified_by: str = None,
        name: str = None,
        status: Status = None,
        page_num: int = 1,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NUMBER,
    ) -> CasesPage:
        """Get a page of cases."""
        data = QueryCasesRequest(
            assignee=assignee,
            createdAt=created_at,
            isAssigned=is_assigned,
            lastModifiedBy=last_modified_by,
            name=name,
            status=status,
            pgNum=page_num,
            pgSize=page_size,
            srtDir=sort_dir,
            srtKey=sort_key,
        )
        response = self._session.get("/v1/cases", params=data.dict())
        return CasesPage.parse_response(response)

    def iter_all(
        self,
        assignee: str = None,
        created_at: Tuple[datetime, datetime] = None,
        is_assigned: bool = None,
        last_modified_by: str = None,
        name: str = None,
        status: Status = None,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NUMBER,
    ) -> Iterator[Case]:
        """Iterate over all cases."""
        page_size = page_size or self.default_page_size
        for page_num in count(1):
            page = self.get_page(
                assignee=assignee,
                created_at=created_at,
                is_assigned=is_assigned,
                last_modified_by=last_modified_by,
                name=name,
                status=status,
                page_num=page_num,
                sort_dir=sort_dir,
                sort_key=sort_key,
            )
            yield from page.cases
            if len(page.cases) < page_size:
                break

    def update(self, case: Case):
        """Updates a case. Accepts a :class:`Case` object."""
        data = UpdateCaseRequest(**case.dict())
        response = self._session.put(
            f"/v1/cases/{case.number}", json=data.dict(by_alias=True)
        )
        return Case.parse_response(response)

    def download_summary_pdf(self, case_number: int, target_folder: Path) -> Path:
        """Downloads summary of case in pdf format to specified target folder."""
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        if not folder.is_dir():
            raise ValueError(
                f"`target_folder` argument must resolve to a folder: {target_folder}"
            )
        response = self._session.get(f"/v1/cases/{case_number}/export")
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}.csv"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def download_fileevent_csv(self, case_number: int, target_folder: Path) -> Path:
        """Downloads all file event data for a case in CSV format to specified target folder."""
        folder = Path(target_folder)  # ensure a Path object if we get passed a string
        if not folder.is_dir():
            raise ValueError(
                f"`target_folder` argument must resolve to a folder: {target_folder}"
            )
        response = self._session.get(f"/v1/cases/{case_number}/fileevent/export")
        filename = get_filename_from_content_disposition(
            response, fallback=f"Case-{case_number}.csv"
        )
        target = folder / filename
        target.write_bytes(response.content)
        return target

    def download_full_case_zip(self, case_number) -> None:
        """Downloads full export of case in zip format to specified target folder."""
        return self._session.post(f"/v1/cases/{case_number}/export/full/downloadToken")

    def get_file_events(self, case_number: int) -> CaseFileEventsResponse:
        """Gets file event details attached to a case."""
        r = self._session.get(f"/v1/cases/{case_number}/fileevent")
        return CaseFileEventsResponse.parse_response(r)

    def add_file_events_to_case(
        self, case_number: int, event_ids: Union[str, List[str]]
    ) -> Response:
        """Attach file events to a case."""
        if isinstance(event_ids, str):
            event_ids = [event_ids]
        return self._session.post(
            f"/v1/cases/{case_number}/fileevent", json={"events": event_ids}
        )

    def delete_file_event_from_case(self, case_number: int, event_id: str):
        """Remove file events from a case."""
        return self._session.delete(f"/v1/cases/{case_number}/fileevent/{event_id}")

    def get_file_event_detail(self, case_number: int, event_id: str):
        """Get the full detail for a given file event."""
        response = self._session.get(f"/v1/cases/{case_number}/fileevent/{event_id}")
        return FileEventV2(**response.json())

    def download_file_for_event(self, case_number: int, event_id: str):
        """Download the source file (if captured) from a file event attached to a case."""
        return self._session.get(f"/v1/cases/{case_number}/fileevent/{event_id}/file")


class CasesClient:
    def __init__(self, session):
        self._session = session
        self._v1 = None

    @property
    def v1(self):
        if self._v1 is None:
            self._v1 = CasesV1(self._session)
        return self._v1
