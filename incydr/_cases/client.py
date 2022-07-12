from functools import singledispatchmethod
from itertools import count
from typing import Union

from .models import *
from .models import CreateCaseRequest, UpdateCaseRequest


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
        response = self._session.post(url="/v1/cases", data=data)
        return Case.parse_response(response)

    def get_by_id(self, case_number: int) -> Case:
        """Get a single case."""
        response = self._session.get(f"/v1/cases/{case_number}")
        return Case(**response.json())

    def get_page(
        self,
        assignee: str = None,
        created_at: tuple[datetime, datetime] = None,
        is_assigned: bool = None,
        last_modified_by: str = None,
        name: str = None,
        status: Status = None,
        page_num: int = 1,
        page_size: int = None,
        sort_dir: SortDirection = SortDirection.ASC,
        sort_key: SortKeys = SortKeys.NUMBER,
    ) -> CasesPage:
        data = QueryCasesRequest(
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
        response = self._session.get("/v1/cases", params=data.dict(by_alias=True))
        return CasesPage.parse_response(response)

    def iter_all(self, **kwargs):
        page_size = kwargs.get("page_size") or self.default_page_size
        for i in count(1):
            page = self.get_page(**kwargs, page_num=i)
            for case in page.cases:
                yield case
            if len(page.cases) < page_size:
                break

    def update(self, case: Union[Case, int], **kwargs):
        """Updates a case. Accepts a :class:`Case` object or an :class:`int` (representing the case number) as the first argument:

        .. highlight:: python
        .. code-block:: python

            >>> case = client.cases.get(23)
            >>> case.name = "updated_name!"
            >>> client.cases.update(case)
            Case(name='updated_name!', number=23, status=<Status.OPEN: 'OPEN'>, assignee=None, assignee_username=None, createdByUserUid=None, createdByUsername=None, description=None, findings=None, lastModifiedByU
            serUid='942564422882759874', lastModifiedByUsername='admin@example.com', subject=None, subjectUsername=None, updatedAt=datetime.datetime(2022, 5, 6, 16, 31, 53, 675133, tzinfo=datetime.tim
            ezone.utc), createdAt=datetime.datetime(2022, 4, 21, 2, 7, 57, 276392, tzinfo=datetime.timezone.utc))

        :param case: The case to update.
        :type case: :class:Case
        """
        data = UpdateCaseRequest(**case.dict())
        response = self._session.put(
            f"/v1/cases/{case.number}", json=data.dict(by_alias=True)
        )
        return Case.parse_response(response)


class CasesClient(CasesV1):
    def __init__(self, session):
        super().__init__(session)
        self.v1 = self
