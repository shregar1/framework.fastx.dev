"""
Presenter/ViewModel Pattern.

Separates presentation logic from domain logic,
formatting data for display in views.

Implements:
- Presenter interface
- View model formatting
- Response builders

SOLID Principles:
- Single Responsibility: Presenters handle display logic only
- Interface Segregation: View-specific interfaces
- Dependency Inversion: Controllers depend on presenter abstractions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

TData = TypeVar("TData")
TViewModel = TypeVar("TViewModel")


class IPresenter(ABC, Generic[TData, TViewModel]):
    """
    Abstract presenter interface.

    Transforms domain data into view-appropriate format.

    Usage:
        class UserPresenter(IPresenter[User, UserViewModel]):
            def present(self, user: User) -> UserViewModel:
                return UserViewModel(
                    id=user.id,
                    display_name=f"{user.first_name} {user.last_name}",
                    avatar_url=user.avatar or DEFAULT_AVATAR,
                    member_since=user.created_at.strftime("%B %Y")
                )
    """

    @abstractmethod
    def present(self, data: TData) -> TViewModel:
        """
        Present data as view model.

        Args:
            data: Domain data to present.

        Returns:
            View model for display.
        """
        pass

    def present_many(self, items: List[TData]) -> List[TViewModel]:
        """Present a collection of items."""
        return [self.present(item) for item in items]


@dataclass
class ViewModel:
    """
    Base view model class.

    View models contain display-ready data.

    Usage:
        @dataclass
        class UserViewModel(ViewModel):
            id: str
            display_name: str
            avatar_url: str
            member_since: str
    """

    pass


@dataclass
class PaginatedViewModel(Generic[TViewModel]):
    """
    View model for paginated data.

    Usage:
        paginated = PaginatedViewModel(
            items=[...],
            page=1,
            page_size=20,
            total_items=100,
            total_pages=5
        )
    """

    items: List[TViewModel]
    page: int
    page_size: int
    total_items: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


@dataclass
class ApiResponse(Generic[TData]):
    """
    Standard API response wrapper.

    Usage:
        response = ApiResponse.success(user_data)
        response = ApiResponse.error("User not found", code="NOT_FOUND")
    """

    success: bool
    data: Optional[TData] = None
    error: Optional[str] = None
    code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def ok(cls, data: TData, **metadata) -> "ApiResponse[TData]":
        """Create success response."""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def error(
        cls,
        message: str,
        code: str = "ERROR",
        **metadata,
    ) -> "ApiResponse[TData]":
        """Create error response."""
        return cls(success=False, error=message, code=code, metadata=metadata)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.data is not None:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
            result["code"] = self.code
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class ResponseBuilder(Generic[TData]):
    """
    Fluent response builder.

    Usage:
        response = (
            ResponseBuilder()
            .with_data(user)
            .with_metadata("request_id", req_id)
            .with_links({"self": "/users/123"})
            .build()
        )
    """

    def __init__(self):
        self._data: Optional[TData] = None
        self._metadata: Dict[str, Any] = {}
        self._links: Dict[str, str] = {}
        self._headers: Dict[str, str] = {}

    def with_data(self, data: TData) -> "ResponseBuilder[TData]":
        """Set response data."""
        self._data = data
        return self

    def with_metadata(self, key: str, value: Any) -> "ResponseBuilder[TData]":
        """Add metadata."""
        self._metadata[key] = value
        return self

    def with_links(self, links: Dict[str, str]) -> "ResponseBuilder[TData]":
        """Add HATEOAS links."""
        self._links.update(links)
        return self

    def with_header(self, key: str, value: str) -> "ResponseBuilder[TData]":
        """Add response header."""
        self._headers[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build the response."""
        response = {
            "success": True,
            "data": self._data,
        }
        if self._metadata:
            response["metadata"] = self._metadata
        if self._links:
            response["_links"] = self._links
        return response


class JsonPresenter(IPresenter[TData, dict]):
    """
    Generic JSON presenter.

    Usage:
        presenter = JsonPresenter(
            fields=["id", "email", "name"],
            transforms={"created_at": lambda dt: dt.isoformat()}
        )
        json_data = presenter.present(user)
    """

    def __init__(
        self,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        transforms: Optional[Dict[str, Callable]] = None,
    ):
        self._fields = fields
        self._exclude = exclude or []
        self._transforms = transforms or {}

    def present(self, data: TData) -> dict:
        """Convert to JSON-serializable dict."""
        if hasattr(data, "__dict__"):
            obj_dict = data.__dict__.copy()
        elif hasattr(data, "_asdict"):
            obj_dict = data._asdict()
        elif isinstance(data, dict):
            obj_dict = data.copy()
        else:
            return {"value": data}

        # Filter fields
        if self._fields:
            obj_dict = {k: v for k, v in obj_dict.items() if k in self._fields}

        # Exclude fields
        for key in self._exclude:
            obj_dict.pop(key, None)

        # Remove private fields
        obj_dict = {k: v for k, v in obj_dict.items() if not k.startswith("_")}

        # Apply transforms
        for key, transform in self._transforms.items():
            if key in obj_dict:
                obj_dict[key] = transform(obj_dict[key])

        return obj_dict


class HtmlPresenter(IPresenter[TData, str]):
    """
    HTML presenter for server-side rendering.

    Usage:
        presenter = HtmlPresenter(template="<h1>{title}</h1><p>{content}</p>")
        html = presenter.present(article)
    """

    def __init__(
        self,
        template: str,
        escape_html: bool = True,
    ):
        self._template = template
        self._escape = escape_html

    def present(self, data: TData) -> str:
        """Render data as HTML."""
        if hasattr(data, "__dict__"):
            values = data.__dict__
        elif isinstance(data, dict):
            values = data
        else:
            values = {"value": data}

        if self._escape:
            import html
            values = {k: html.escape(str(v)) for k, v in values.items()}

        return self._template.format(**values)


class CompositePresenter(IPresenter[TData, TViewModel]):
    """
    Combines multiple presenters.

    Usage:
        presenter = CompositePresenter([
            UserBasicPresenter(),
            UserStatsPresenter(),
            UserLinksPresenter()
        ])
    """

    def __init__(self, presenters: List[IPresenter]):
        self._presenters = presenters

    def present(self, data: TData) -> dict:
        """Combine results from all presenters."""
        result = {}
        for presenter in self._presenters:
            partial = presenter.present(data)
            if isinstance(partial, dict):
                result.update(partial)
        return result
