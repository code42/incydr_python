from abc import ABC
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
        return Case.parse_response(response)

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
        sort_key: SortKeys = SortKeys.NUMBER
    ) -> CasesPage:
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
        self.data = data
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


    @singledispatchmethod
    def update(self, case: Union[Case, int], **kwargs):
        """Updates a case. Accepts either a :class:`Case` object or an :class:`int` (representing the case number) as the first argument:

        .. highlight:: python
        .. code-block:: python

            >>> case = client.cases.get(23)
            >>> case.name = "updated_name!"
            >>> client.cases.update(case)
            Case(name='updated_name!', number=23, status=<Status.OPEN: 'OPEN'>, assignee=None, assignee_username=None, createdByUserUid=None, createdByUsername=None, description=None, findings=None, lastModifiedByU
            serUid='942564422882759874', lastModifiedByUsername='admin@example.com', subject=None, subjectUsername=None, updatedAt=datetime.datetime(2022, 5, 6, 16, 31, 53, 675133, tzinfo=datetime.tim
            ezone.utc), createdAt=datetime.datetime(2022, 4, 21, 2, 7, 57, 276392, tzinfo=datetime.timezone.utc))

        If a case number is the first argument, pass the data to update as keyword arguments:

        .. highlight:: python
        .. code-block:: python

            >>> client.cases.update(23, name="updated_name!")
            Case(name='updated_name!', number=23, status=<Status.OPEN: 'OPEN'>, assignee=None, assignee_username=None, createdByUserUid=None, createdByUsername=None, description=None, findings=None, lastModifiedByU
            serUid='942564422882759874', lastModifiedByUsername='admin@example.com', subject=None, subjectUsername=None, updatedAt=datetime.datetime(2022, 5, 6, 16, 31, 53, 675133, tzinfo=datetime.tim
            ezone.utc), createdAt=datetime.datetime(2022, 4, 21, 2, 7, 57, 276392, tzinfo=datetime.timezone.utc))

        :param case: The case to update.
        :type case: :class:Case or int
        :param name: The name of the case.
        :type name: str (max_length=50) or None
        :param assignee: The user_id of the person assigned to the case.
        :type assignee: str or None
        :param description: The case description.
        :type name: str (max_length=250) or None
        :param findings: Text field for tracking information found while investigating the case.
        :type name: str (max_length=30,000) or None
        :param subject: The user_id of the person being investigated in the case.
        :type subject: str or None
        :param status: The status of the case. default=Status.OPEN
        :type status: :class:Status

        """
        raise NotImplementedError()

    @update.register
    def _model(self, case: Case) -> Case:
        data = UpdateCaseRequest(**case.dict())
        response = self._session.put(f"/v1/cases/{case.number}", data=data)
        return Case(**response.json())

    @update.register
    def _params(
            self,
            case: int,
            name: str = None,
            subject: str = None,
            assignee: str = None,
            description: str = None,
            findings: str = None,
            status: Status = Status.OPEN,
    ) -> Case:
        data = UpdateCaseRequest(
            number=case,
            name=name,
            subject=subject,
            assignee=assignee,
            description=description,
            findings=findings,
            status=status,
        )
        response = self._session.put(f"/v1/cases/{case}", json=data.json())
        return Case.parse_raw(response.text)


class CasesClient(CasesV1, ABC):
    def __init__(self, session):
        super().__init__(session)
        self.v1 = CasesV1(session)
