# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: data_transfer.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'data_transfer.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x64\x61ta_transfer.proto\"\x1a\n\nDataPacket\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"\x1e\n\x0cSendResponse\x12\x0e\n\x06status\x18\x01 \x01(\t28\n\x0c\x44\x61taTransfer\x12(\n\x08SendData\x12\x0b.DataPacket\x1a\r.SendResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_transfer_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DATAPACKET']._serialized_start=23
  _globals['_DATAPACKET']._serialized_end=49
  _globals['_SENDRESPONSE']._serialized_start=51
  _globals['_SENDRESPONSE']._serialized_end=81
  _globals['_DATATRANSFER']._serialized_start=83
  _globals['_DATATRANSFER']._serialized_end=139
# @@protoc_insertion_point(module_scope)