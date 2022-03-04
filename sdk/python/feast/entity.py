# Copyright 2019 The Feast Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime
from typing import Dict, Optional

import yaml
from google.protobuf import json_format
from google.protobuf.json_format import MessageToDict, MessageToJson

from feast.loaders import yaml as feast_yaml
from feast.protos.feast.core.Entity_pb2 import Entity as EntityV2Proto
from feast.protos.feast.core.Entity_pb2 import EntityMeta as EntityMetaProto
from feast.protos.feast.core.Entity_pb2 import EntitySpecV2 as EntitySpecProto
from feast.usage import log_exceptions
from feast.value_type import ValueType


class Entity:
    """
    Represents a collection of entities and associated metadata.

    Args:
        name: Name of the entity.
        value_type (optional): The type of the entity, such as string or float.
        description (optional): Additional information to describe the entity.
        join_key (optional): A property that uniquely identifies different entities
            within the collection. Used as a key for joining entities with their
            associated features. If not specified, defaults to the name of the entity.
        labels (optional): User-defined metadata in dictionary form.
    """

    name: str
    value_type: ValueType
    join_key: str
    description: str
    labels: Dict[str, str]
    owner: str
    created_timestamp: Optional[datetime]
    last_updated_timestamp: Optional[datetime]

    @log_exceptions
    def __init__(
        self,
        name: str,
        value_type: ValueType = ValueType.UNKNOWN,
        description: str = "",
        join_key: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        """Creates an Entity object."""
        self.name = name
        self.value_type = value_type
        self.join_key = join_key if join_key else name
        self.description = description

        if labels is None:
            self.labels = dict()
        else:
            self.labels = labels

        self.created_timestamp = None
        self.last_updated_timestamp = None

    def __hash__(self) -> int:
        return hash((id(self), self.name))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            raise TypeError("Comparisons should only involve Entity class objects.")

        if (
            self.labels != other.labels
            or self.name != other.name
            or self.description != other.description
            or self.value_type != other.value_type
            or self.join_key != other.join_key
        ):
            return False

        return True

    def __str__(self):
        return str(MessageToJson(self.to_proto()))

    def is_valid(self):
        """
        Validates the state of this entity locally.

        Raises:
            ValueError: The entity does not have a name or does not have a type.
        """
        if not self.name:
            raise ValueError("No name found in entity.")

        if not self.value_type:
            raise ValueError("No type found in entity {self.value_type}")

    @classmethod
    def from_yaml(cls, yml: str):
        """
        Creates an entity from a YAML string body or a file path.

        Args:
            yml: Either a file path containing a yaml file or a YAML string.

        Returns:
            An EntityV2 object based on the YAML file.
        """
        return cls.from_dict(feast_yaml.yaml_loader(yml, load_single=True))

    @classmethod
    def from_dict(cls, entity_dict):
        """
        Creates an entity from a dict.

        Args:
            entity_dict: A dict representation of an entity.

        Returns:
            An EntityV2 object based on the entity dict.
        """
        entity_proto = json_format.ParseDict(
            entity_dict, EntityV2Proto(), ignore_unknown_fields=True
        )
        return cls.from_proto(entity_proto)

    @classmethod
    def from_proto(cls, entity_proto: EntityV2Proto):
        """
        Creates an entity from a protobuf representation of an entity.

        Args:
            entity_proto: A protobuf representation of an entity.

        Returns:
            An EntityV2 object based on the entity protobuf.
        """
        entity = cls(
            name=entity_proto.spec.name,
            description=entity_proto.spec.description,
            value_type=ValueType(entity_proto.spec.value_type),
            labels=entity_proto.spec.labels,
            join_key=entity_proto.spec.join_key,
        )

        if entity_proto.meta.HasField("created_timestamp"):
            entity.created_timestamp = entity_proto.meta.created_timestamp.ToDatetime()
        if entity_proto.meta.HasField("last_updated_timestamp"):
            entity.last_updated_timestamp = (
                entity_proto.meta.last_updated_timestamp.ToDatetime()
            )

        return entity

    def to_proto(self) -> EntityV2Proto:
        """
        Converts an entity object to its protobuf representation.

        Returns:
            An EntityV2Proto protobuf.
        """
        meta = EntityMetaProto()
        if self.created_timestamp:
            meta.created_timestamp.FromDatetime(self.created_timestamp)
        if self.last_updated_timestamp:
            meta.last_updated_timestamp.FromDatetime(self.last_updated_timestamp)

        spec = EntitySpecProto(
            name=self.name,
            description=self.description,
            value_type=self.value_type.value,
            labels=self.labels,
            join_key=self.join_key,
        )

        return EntityV2Proto(spec=spec, meta=meta)

    def to_dict(self) -> Dict:
        """
        Converts entity to dict.

        Returns:
            Dictionary object representation of entity.
        """
        entity_dict = MessageToDict(self.to_proto())

        # Remove meta when empty for more readable exports
        if entity_dict["meta"] == {}:
            del entity_dict["meta"]

        return entity_dict

    def to_yaml(self):
        """
        Converts a entity to a YAML string.

        Returns:
            An entity string returned in YAML format.
        """
        entity_dict = self.to_dict()
        return yaml.dump(entity_dict, allow_unicode=True, sort_keys=False)

    def to_spec_proto(self) -> EntitySpecProto:
        """
        Converts an EntityV2 object to its protobuf representation.
        Used when passing EntitySpecV2 object to Feast request.

        Returns:
            An EntitySpecV2 protobuf.
        """
        spec = EntitySpecProto(
            name=self.name,
            description=self.description,
            value_type=self.value_type.value,
            labels=self.labels,
            join_key=self.join_key,
        )

        return spec

    def _update_from_entity(self, entity):
        """
        Deep replaces one entity with another.

        Args:
            entity: Entity to use as a source of configuration.
        """
        self.name = entity.name
        self.description = entity.description
        self.value_type = entity.value_type
        self.labels = entity.labels
        self.join_key = entity.join_key
        self.created_timestamp = entity.created_timestamp
        self.last_updated_timestamp = entity.last_updated_timestamp
