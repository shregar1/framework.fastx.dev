"""
Mapper/Transformer Pattern.

Handles conversion between different object representations
(e.g., Entity to DTO, Domain to Persistence).

Implements:
- Bidirectional mapping
- Collection mapping
- Composite mappers
- Auto-mapping utilities

SOLID Principles:
- Single Responsibility: Each mapper handles one conversion
- Open/Closed: Add new mappers without modification
- Interface Segregation: Separate mapping interfaces
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

TSource = TypeVar("TSource")
TDestination = TypeVar("TDestination")


class IMapper(ABC, Generic[TSource, TDestination]):
    """
    Abstract mapper interface.

    Maps between source and destination types.

    Usage:
        class UserToUserDTOMapper(IMapper[User, UserDTO]):
            def map(self, source: User) -> UserDTO:
                return UserDTO(
                    id=source.id,
                    email=source.email,
                    full_name=f"{source.first_name} {source.last_name}"
                )
    """

    @abstractmethod
    def map(self, source: TSource) -> TDestination:
        """
        Map source to destination.

        Args:
            source: Source object.

        Returns:
            Mapped destination object.
        """
        pass

    def map_many(self, sources: List[TSource]) -> List[TDestination]:
        """
        Map collection of sources.

        Args:
            sources: List of source objects.

        Returns:
            List of mapped destination objects.
        """
        return [self.map(source) for source in sources]


class IBidirectionalMapper(IMapper[TSource, TDestination]):
    """
    Bidirectional mapper interface.

    Maps in both directions between types.

    Usage:
        class UserMapper(IBidirectionalMapper[User, UserDTO]):
            def map(self, source: User) -> UserDTO:
                return UserDTO(...)

            def reverse_map(self, destination: UserDTO) -> User:
                return User(...)
    """

    @abstractmethod
    def reverse_map(self, destination: TDestination) -> TSource:
        """Map destination back to source."""
        pass

    def reverse_map_many(self, destinations: List[TDestination]) -> List[TSource]:
        """Map collection of destinations to sources."""
        return [self.reverse_map(dest) for dest in destinations]


class LambdaMapper(IMapper[TSource, TDestination]):
    """
    Mapper from a lambda function.

    Usage:
        mapper = LambdaMapper(lambda user: UserDTO(
            id=user.id,
            email=user.email
        ))
    """

    def __init__(self, map_func: Callable[[TSource], TDestination]):
        self._map_func = map_func

    def map(self, source: TSource) -> TDestination:
        return self._map_func(source)


class CompositeMapper(IMapper[TSource, TDestination]):
    """
    Chains multiple mappers together.

    Usage:
        # User -> UserDTO -> UserResponse
        composite = CompositeMapper([
            UserToUserDTOMapper(),
            UserDTOToResponseMapper()
        ])
    """

    def __init__(self, mappers: List[IMapper]):
        self._mappers = mappers

    def map(self, source: TSource) -> TDestination:
        result = source
        for mapper in self._mappers:
            result = mapper.map(result)
        return result


class MappingProfile:
    """
    Configuration for mapping between types.

    Usage:
        profile = MappingProfile()
        profile.create_map(User, UserDTO)
            .for_member("full_name", lambda u: f"{u.first_name} {u.last_name}")
            .ignore("password")
    """

    def __init__(self):
        self._mappings: Dict[tuple, "TypeMapping"] = {}

    def create_map(
        self,
        source_type: Type[TSource],
        dest_type: Type[TDestination],
    ) -> "TypeMapping[TSource, TDestination]":
        """Create a mapping configuration."""
        key = (source_type, dest_type)
        mapping = TypeMapping(source_type, dest_type)
        self._mappings[key] = mapping
        return mapping

    def get_mapping(
        self,
        source_type: Type[TSource],
        dest_type: Type[TDestination],
    ) -> Optional["TypeMapping[TSource, TDestination]"]:
        """Get mapping configuration."""
        return self._mappings.get((source_type, dest_type))


class TypeMapping(Generic[TSource, TDestination]):
    """
    Configuration for a single type mapping.

    Supports:
    - Custom member mappings
    - Ignored members
    - Conditional mappings
    """

    def __init__(
        self,
        source_type: Type[TSource],
        dest_type: Type[TDestination],
    ):
        self._source_type = source_type
        self._dest_type = dest_type
        self._member_mappings: Dict[str, Callable] = {}
        self._ignored_members: set = set()
        self._conditions: List[Callable[[TSource], bool]] = []

    def for_member(
        self,
        member: str,
        value_resolver: Callable[[TSource], Any],
    ) -> "TypeMapping[TSource, TDestination]":
        """
        Configure custom mapping for a member.

        Args:
            member: Destination member name.
            value_resolver: Function to get value from source.
        """
        self._member_mappings[member] = value_resolver
        return self

    def ignore(self, *members: str) -> "TypeMapping[TSource, TDestination]":
        """Ignore specified members during mapping."""
        self._ignored_members.update(members)
        return self

    def condition(
        self,
        predicate: Callable[[TSource], bool],
    ) -> "TypeMapping[TSource, TDestination]":
        """Add condition for mapping."""
        self._conditions.append(predicate)
        return self

    def map(self, source: TSource) -> TDestination:
        """Execute the mapping."""
        # Check conditions
        for condition in self._conditions:
            if not condition(source):
                raise ValueError("Mapping conditions not met")

        # Get source attributes
        if hasattr(source, "__dict__"):
            source_attrs = source.__dict__.copy()
        elif hasattr(source, "_asdict"):
            source_attrs = source._asdict()
        else:
            source_attrs = {}

        # Apply custom mappings
        dest_attrs = {}
        for key, value in source_attrs.items():
            if key not in self._ignored_members and not key.startswith("_"):
                dest_attrs[key] = value

        for member, resolver in self._member_mappings.items():
            dest_attrs[member] = resolver(source)

        # Remove ignored members
        for ignored in self._ignored_members:
            dest_attrs.pop(ignored, None)

        return self._dest_type(**dest_attrs)


class AutoMapper:
    """
    Automatic mapper using registered profiles.

    Usage:
        mapper = AutoMapper()
        mapper.add_profile(MyMappingProfile())

        user_dto = mapper.map(user, UserDTO)
    """

    def __init__(self):
        self._profiles: List[MappingProfile] = []
        self._cache: Dict[tuple, TypeMapping] = {}

    def add_profile(self, profile: MappingProfile) -> None:
        """Add a mapping profile."""
        self._profiles.append(profile)

    def map(
        self,
        source: TSource,
        dest_type: Type[TDestination],
    ) -> TDestination:
        """
        Map source to destination type.

        Args:
            source: Source object.
            dest_type: Destination type.

        Returns:
            Mapped object.
        """
        source_type = type(source)
        cache_key = (source_type, dest_type)

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key].map(source)

        # Find mapping in profiles
        for profile in self._profiles:
            mapping = profile.get_mapping(source_type, dest_type)
            if mapping:
                self._cache[cache_key] = mapping
                return mapping.map(source)

        # Try auto-mapping
        return self._auto_map(source, dest_type)

    def _auto_map(
        self,
        source: TSource,
        dest_type: Type[TDestination],
    ) -> TDestination:
        """Attempt automatic mapping by matching attribute names."""
        if hasattr(source, "__dict__"):
            attrs = {
                k: v for k, v in source.__dict__.items()
                if not k.startswith("_")
            }
        elif hasattr(source, "_asdict"):
            attrs = source._asdict()
        else:
            raise ValueError(f"Cannot auto-map {type(source)}")

        return dest_type(**attrs)

    def map_many(
        self,
        sources: List[TSource],
        dest_type: Type[TDestination],
    ) -> List[TDestination]:
        """Map collection."""
        return [self.map(source, dest_type) for source in sources]
