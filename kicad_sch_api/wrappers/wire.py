"""Wire wrapper class for enhanced wire manipulation."""

from typing import TYPE_CHECKING, List, Optional

from ..core.types import Point, Wire, WireType
from .base import ElementWrapper

if TYPE_CHECKING:
    from ..collections.wires import WireCollection


class WireWrapper(ElementWrapper[Wire]):
    """Enhanced wrapper for Wire with validation and parent tracking.

    Provides:
    - Validation on property setters (e.g., minimum 2 points for wires)
    - Automatic parent collection notification on changes
    - Convenient access to wire properties
    - Type-safe operations
    """

    def __init__(self, wire: Wire, parent_collection: Optional["WireCollection"] = None):
        """Initialize wire wrapper.

        Args:
            wire: The underlying Wire dataclass
            parent_collection: Parent collection for modification tracking (optional)
        """
        super().__init__(wire, parent_collection)

    @property
    def uuid(self) -> str:
        """Get wire UUID.

        Returns:
            Wire UUID string
        """
        return self._data.uuid

    @property
    def points(self) -> List[Point]:
        """Get wire points.

        Returns:
            List of Point objects defining the wire path
        """
        return self._data.points

    @points.setter
    def points(self, value: List[Point]) -> None:
        """Set wire points with validation.

        Args:
            value: List of points (must have at least 2 points)

        Raises:
            ValueError: If less than 2 points provided
        """
        if len(value) < 2:
            raise ValueError("Wire must have at least 2 points")

        # Create new Wire with updated points
        self._data = Wire(
            uuid=self._data.uuid,
            points=value,
            wire_type=self._data.wire_type,
            stroke_width=self._data.stroke_width,
            stroke_type=self._data.stroke_type,
        )
        self._mark_modified()

    @property
    def start(self) -> Point:
        """Get start point (first point of wire).

        Returns:
            First point in the wire path
        """
        return self._data.points[0]

    @property
    def end(self) -> Point:
        """Get end point (last point of wire).

        Returns:
            Last point in the wire path
        """
        return self._data.points[-1]

    @property
    def wire_type(self) -> WireType:
        """Get wire type (WIRE or BUS).

        Returns:
            WireType enum value
        """
        return self._data.wire_type

    @wire_type.setter
    def wire_type(self, value: WireType) -> None:
        """Set wire type.

        Args:
            value: WireType enum value (WIRE or BUS)
        """
        self._data = Wire(
            uuid=self._data.uuid,
            points=self._data.points,
            wire_type=value,
            stroke_width=self._data.stroke_width,
            stroke_type=self._data.stroke_type,
        )
        self._mark_modified()

    @property
    def stroke_width(self) -> float:
        """Get stroke width.

        Returns:
            Stroke width in mm
        """
        return self._data.stroke_width

    @stroke_width.setter
    def stroke_width(self, value: float) -> None:
        """Set stroke width.

        Args:
            value: Stroke width in mm
        """
        self._data = Wire(
            uuid=self._data.uuid,
            points=self._data.points,
            wire_type=self._data.wire_type,
            stroke_width=value,
            stroke_type=self._data.stroke_type,
        )
        self._mark_modified()

    @property
    def stroke_type(self) -> str:
        """Get stroke type.

        Returns:
            Stroke type string
        """
        return self._data.stroke_type

    @stroke_type.setter
    def stroke_type(self, value: str) -> None:
        """Set stroke type.

        Args:
            value: Stroke type string
        """
        self._data = Wire(
            uuid=self._data.uuid,
            points=self._data.points,
            wire_type=self._data.wire_type,
            stroke_width=self._data.stroke_width,
            stroke_type=value,
        )
        self._mark_modified()

    # Delegate methods to underlying Wire dataclass

    @property
    def length(self) -> float:
        """Get total wire length.

        Returns:
            Total length of all wire segments in mm
        """
        return self._data.length

    def is_simple(self) -> bool:
        """Check if wire is a simple 2-point wire.

        Returns:
            True if wire has exactly 2 points, False otherwise
        """
        return self._data.is_simple()

    def is_horizontal(self) -> bool:
        """Check if wire is horizontal (delegates to Wire).

        Returns:
            True if wire is horizontal
        """
        return self._data.is_horizontal()

    def is_vertical(self) -> bool:
        """Check if wire is vertical (delegates to Wire).

        Returns:
            True if wire is vertical
        """
        return self._data.is_vertical()
