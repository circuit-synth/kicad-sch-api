"""
Element Factory for creating schematic elements from dictionaries.

Centralizes object creation logic that was previously duplicated in Schematic.__init__.
"""

import uuid
from typing import Any, Dict, List

from ..types import (
    BusEntry,
    HierarchicalLabelShape,
    Junction,
    Label,
    LabelType,
    Net,
    NoConnect,
    Point,
    Text,
    Wire,
    WireType,
)


def point_from_dict_or_tuple(position: Any) -> Point:
    """Convert position data (dict or tuple) to Point object."""
    if isinstance(position, dict):
        return Point(position.get("x", 0), position.get("y", 0))
    elif isinstance(position, (list, tuple)):
        return Point(position[0], position[1])
    elif isinstance(position, Point):
        return position
    else:
        return Point(0, 0)


class ElementFactory:
    """Factory for creating schematic elements from dictionary data."""

    @staticmethod
    def create_wire(wire_dict: Dict[str, Any]) -> Wire:
        """
        Create Wire object from dictionary.

        Args:
            wire_dict: Dictionary containing wire data

        Returns:
            Wire object
        """
        points = []
        for point_data in wire_dict.get("points", []):
            if isinstance(point_data, dict):
                points.append(Point(point_data["x"], point_data["y"]))
            elif isinstance(point_data, (list, tuple)):
                points.append(Point(point_data[0], point_data[1]))
            else:
                points.append(point_data)

        return Wire(
            uuid=wire_dict.get("uuid", str(uuid.uuid4())),
            points=points,
            wire_type=WireType(wire_dict.get("wire_type", "wire")),
            stroke_width=wire_dict.get("stroke_width", 0.0),
            stroke_type=wire_dict.get("stroke_type", "default"),
        )

    @staticmethod
    def create_junction(junction_dict: Dict[str, Any]) -> Junction:
        """
        Create Junction object from dictionary.

        Args:
            junction_dict: Dictionary containing junction data

        Returns:
            Junction object
        """
        position = junction_dict.get("position", {"x": 0, "y": 0})
        pos = point_from_dict_or_tuple(position)

        return Junction(
            uuid=junction_dict.get("uuid", str(uuid.uuid4())),
            position=pos,
            diameter=junction_dict.get("diameter", 0),
            color=junction_dict.get("color", (0, 0, 0, 0)),
        )

    @staticmethod
    def create_text(text_dict: Dict[str, Any]) -> Text:
        """
        Create Text object from dictionary.

        Args:
            text_dict: Dictionary containing text data

        Returns:
            Text object
        """
        position = text_dict.get("position", {"x": 0, "y": 0})
        pos = point_from_dict_or_tuple(position)

        return Text(
            uuid=text_dict.get("uuid", str(uuid.uuid4())),
            position=pos,
            text=text_dict.get("text", ""),
            rotation=text_dict.get("rotation", 0.0),
            size=text_dict.get("size", 1.27),
            exclude_from_sim=text_dict.get("exclude_from_sim", False),
            # Font effects
            bold=text_dict.get("bold", False),
            italic=text_dict.get("italic", False),
            thickness=text_dict.get("thickness"),
            color=text_dict.get("color"),
            face=text_dict.get("face"),
        )

    @staticmethod
    def create_label(label_dict: Dict[str, Any]) -> Label:
        """
        Create Label object from dictionary.

        Args:
            label_dict: Dictionary containing label data

        Returns:
            Label object
        """
        position = label_dict.get("position", {"x": 0, "y": 0})
        pos = point_from_dict_or_tuple(position)

        return Label(
            uuid=label_dict.get("uuid", str(uuid.uuid4())),
            position=pos,
            text=label_dict.get("text", ""),
            label_type=LabelType(label_dict.get("label_type", "label")),
            rotation=label_dict.get("rotation", 0.0),
            size=label_dict.get("size", 1.27),
            shape=(
                HierarchicalLabelShape(label_dict.get("shape")) if label_dict.get("shape") else None
            ),
            justify_h=label_dict.get("justify_h", "left"),
            justify_v=label_dict.get("justify_v", "bottom"),
        )

    @staticmethod
    def create_bus_entry(bus_entry_dict: Dict[str, Any]) -> BusEntry:
        """
        Create BusEntry object from dictionary.

        Args:
            bus_entry_dict: Dictionary containing bus entry data

        Returns:
            BusEntry object
        """
        position = bus_entry_dict.get("position", {"x": 0, "y": 0})
        pos = point_from_dict_or_tuple(position)

        # Get size (default to 2.54mm if not provided)
        size_data = bus_entry_dict.get("size", {"x": 2.54, "y": 2.54})
        size = point_from_dict_or_tuple(size_data)

        return BusEntry(
            uuid=bus_entry_dict.get("uuid", str(uuid.uuid4())),
            position=pos,
            size=size,
            rotation=bus_entry_dict.get("rotation", 0),
            stroke_width=bus_entry_dict.get("stroke_width", 0.0),
            stroke_type=bus_entry_dict.get("stroke_type", "default"),
        )

    @staticmethod
    def create_no_connect(no_connect_dict: Dict[str, Any]) -> NoConnect:
        """
        Create NoConnect object from dictionary.

        Args:
            no_connect_dict: Dictionary containing no-connect data

        Returns:
            NoConnect object
        """
        position = no_connect_dict.get("position", {"x": 0, "y": 0})
        pos = point_from_dict_or_tuple(position)

        return NoConnect(
            uuid=no_connect_dict.get("uuid", str(uuid.uuid4())),
            position=pos,
        )

    @staticmethod
    def create_net(net_dict: Dict[str, Any]) -> Net:
        """
        Create Net object from dictionary.

        Args:
            net_dict: Dictionary containing net data

        Returns:
            Net object
        """
        return Net(
            name=net_dict.get("name", ""),
            components=net_dict.get("components", []),
            wires=net_dict.get("wires", []),
            labels=net_dict.get("labels", []),
        )

    @staticmethod
    def create_wires_from_list(wire_data: List[Any]) -> List[Wire]:
        """
        Create list of Wire objects from list of dictionaries.

        Args:
            wire_data: List of wire dictionaries

        Returns:
            List of Wire objects
        """
        wires = []
        for wire_dict in wire_data:
            if isinstance(wire_dict, dict):
                wires.append(ElementFactory.create_wire(wire_dict))
        return wires

    @staticmethod
    def create_junctions_from_list(junction_data: List[Any]) -> List[Junction]:
        """
        Create list of Junction objects from list of dictionaries.

        Args:
            junction_data: List of junction dictionaries

        Returns:
            List of Junction objects
        """
        junctions = []
        for junction_dict in junction_data:
            if isinstance(junction_dict, dict):
                junctions.append(ElementFactory.create_junction(junction_dict))
        return junctions

    @staticmethod
    def create_texts_from_list(text_data: List[Any]) -> List[Text]:
        """
        Create list of Text objects from list of dictionaries.

        Args:
            text_data: List of text dictionaries

        Returns:
            List of Text objects
        """
        texts = []
        for text_dict in text_data:
            if isinstance(text_dict, dict):
                texts.append(ElementFactory.create_text(text_dict))
        return texts

    @staticmethod
    def create_labels_from_list(label_data: List[Any]) -> List[Label]:
        """
        Create list of Label objects from list of dictionaries.

        Args:
            label_data: List of label dictionaries

        Returns:
            List of Label objects
        """
        labels = []
        for label_dict in label_data:
            if isinstance(label_dict, dict):
                labels.append(ElementFactory.create_label(label_dict))
        return labels

    @staticmethod
    def create_no_connects_from_list(no_connect_data: List[Any]) -> List[NoConnect]:
        """
        Create list of NoConnect objects from list of dictionaries.

        Args:
            no_connect_data: List of no-connect dictionaries

        Returns:
            List of NoConnect objects
        """
        no_connects = []
        for no_connect_dict in no_connect_data:
            if isinstance(no_connect_dict, dict):
                no_connects.append(ElementFactory.create_no_connect(no_connect_dict))
        return no_connects

    @staticmethod
    def create_bus_entries_from_list(bus_entry_data: List[Any]) -> List[BusEntry]:
        """
        Create list of BusEntry objects from list of dictionaries.

        Args:
            bus_entry_data: List of bus entry dictionaries

        Returns:
            List of BusEntry objects
        """
        bus_entries = []
        for bus_entry_dict in bus_entry_data:
            if isinstance(bus_entry_dict, dict):
                bus_entries.append(ElementFactory.create_bus_entry(bus_entry_dict))
            elif isinstance(bus_entry_dict, BusEntry):
                bus_entries.append(bus_entry_dict)
        return bus_entries

    @staticmethod
    def create_nets_from_list(net_data: List[Any]) -> List[Net]:
        """
        Create list of Net objects from list of dictionaries.

        Args:
            net_data: List of net dictionaries

        Returns:
            List of Net objects
        """
        nets = []
        for net_dict in net_data:
            if isinstance(net_dict, dict):
                nets.append(ElementFactory.create_net(net_dict))
        return nets
