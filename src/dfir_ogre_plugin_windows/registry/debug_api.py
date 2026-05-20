# from dataclasses import dataclass
# from datetime import datetime
# from typing import Any, Generator, List, Optional

# import regquery
# from dfir_ogre_common import (
#     Record,
#     SecurityDescriptor,
#     security_descriptor_from_bytes,
# )
# from dfir_ogre_common import (
#     Value as OgreValue,
# )
# from regquery import Hive

# """
# This file is a python debug API that uses a not release tool named regquery to debug the rust dfir-nt-hive crate
# """


# @dataclass
# class RegValue:
#     _name: str
#     _type: str
#     _data: Any

#     def name(self) -> str:
#         return self._name

#     def type(self) -> str:
#         return self._type

#     def data(self) -> Any:
#         return self._data

#     def to_tuple(self, max_len: int = 0) -> Record:
#         record = Record()
#         record.add("name", OgreValue.String(self._name))
#         record.add("type", OgreValue.String(self._type))
#         if isinstance(self._data, int):
#             record.add("data", OgreValue.Int(self._data))
#         elif isinstance(self._data, bytes):
#             data = ""
#             if max_len > 0 and len(self._data) > max_len:
#                 data = self._data[0:max_len].hex() + "[..]"
#             else:
#                 data = self._data.hex()

#             record.add("data", OgreValue.String(f"0x{data}"))
#         elif isinstance(self._data, bytearray):
#             data = ""
#             if max_len > 0 and len(self._data) > max_len:
#                 data = self._data[0:max_len].hex() + "[..]"
#             else:
#                 data = self._data.hex()

#             record.add("data", OgreValue.String(f"0x{data}"))
#         else:
#             data = str(self._data)
#             if max_len > 0 and len(data) > max_len:
#                 data = data[0:max_len] + "[..]"

#             record.add("data", OgreValue.String(data))
#         return record


# @dataclass
# class RegKey:
#     key: regquery.Key
#     mtime: datetime
#     security_descriptor: SecurityDescriptor
#     path: str
#     name: str
#     _value: dict[str, RegValue]

#     def sub_keys(self) -> Generator["RegKey", Any, Any]:
#         if isinstance(self.key, regquery.Key):
#             for regkey in self.key.subkeys():
#                 key = convert_key(regkey)
#                 yield key

#     def sub_key(self, name: str) -> Optional["RegKey"]:
#         if isinstance(self.key, regquery.Key):
#             for regkey in self.key.subkeys():
#                 key = convert_key(regkey)
#                 if key.name == name:
#                     return key
#         return None

#     def sub_path(self, path: str) -> Optional["RegKey"]:
#         if isinstance(self.key, regquery.Key):
#             reg_key = self.key.get(path, value_priority=False, missing_ok=True)
#             if isinstance(reg_key, regquery.Key):
#                 return convert_key(reg_key)

#         return None

#     def sub_glob(self, path: str) -> Generator["RegKey", Any, Any]:
#         if isinstance(self.key, regquery.Key):
#             for reg_key in self.key.glob(path):
#                 if isinstance(reg_key, regquery.Key):
#                     yield convert_key(reg_key)

#     def value(self, name: str) -> Optional[RegValue]:
#         return self._value.get(name, None)

#     def values(self) -> List[RegValue]:
#         return list(self._value.values())

#     def value_data(self, name: str, default=None) -> Any:
#         value = self._value.get(name, default)
#         if value:
#             return value._data
#         return default

#     def to_tuple(self, max_len: int = 0) -> Record:
#         tuple = Record()
#         tuple.add("name", OgreValue.String(self.name))
#         tuple.add("mtime", OgreValue.Date(self.mtime))
#         tuple.add("path", OgreValue.String(self.path))
#         values_list = []
#         for _, value in self._value.items():
#             values_list.append(OgreValue.Object(value.to_tuple(max_len)))

#         tuple.add("values", OgreValue.Array(values_list))
#         tuple.add("security", OgreValue.Object(self.security_descriptor.to_record()))

#         return tuple


# def convert_key(regkey: regquery.Key) -> RegKey:
#     mtime = regkey.mtime
#     key_security = regkey.key_security
#     security_descriptor = security_descriptor_from_bytes(key_security)
#     path = regkey.path
#     name = path.split("\\").pop()
#     key = RegKey(regkey, mtime, security_descriptor, path, name, {})
#     for val in regkey.values():
#         if isinstance(val, regquery.Value):
#             data = val.data
#             type = val.type.name
#             name = val.name
#             key._value[name] = RegValue(name, type, data)
#     return key


# class Registry:
#     def __init__(self, hive_ref: Hive):
#         self.hive = hive_ref

#     # def get_key(self, query: str) -> Optional[RegKey]:
#     #     reg_key = self.hive.get(query, value_priority=False, missing_ok=True)
#     #     if isinstance(reg_key, regquery.Key):
#     #         return convert_key(reg_key)
#     #     return None

#     def glob_keys(self, query: str) -> Generator[RegKey, Any, Any]:  # List[Key]:
#         for regkey in self.hive.glob(query, filter="keys"):
#             if isinstance(regkey, regquery.Key):
#                 yield convert_key(regkey)

#     @classmethod
#     def load(cls, input_file: str, mount_point: Optional[str] = None) -> "Registry":
#         with open(input_file, "rb") as f:
#             hive = regquery.Hive(f, mount_point)
#         return Registry(hive)
