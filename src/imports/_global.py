import os
import enum
import pytz
import logging
import urllib3
import requests
import sys
import json
import io
import speech_recognition as sr
import asyncio

from openai import AsyncOpenAI
from lxml.html import fromstring
from pydub import AudioSegment
from fuzzywuzzy import process, fuzz
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional, Annotated, List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from math import cos, radians, sin, sqrt, atan2

from parselab.parsing import BasicParser
from parselab.network import NetworkManager
from parselab.cache import FileCache

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    CallbackQuery,
    FSInputFile,
)

from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    MappedColumn,
    DeclarativeBase,
    mapped_column,
    relationship,
    selectinload,
)
from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
    Enum,
    Boolean,
    DateTime,
    Text,
    Float,
    Date,
    MetaData,
    Table,
    JSON,
    Interval,
    Column,
    Integer,
    text,
    select,
    update,
    delete,
    desc,
    func,
    extract,
    case,
    func,
    and_,
)


__all__ = [
    "asyncio",
    "os",
    "enum",
    "pytz",
    "logging",
    "datetime",
    "timedelta",
    "Optional",
    "Annotated",
    "List",
    "BaseSettings",
    "SettingsConfigDict",
    "load_dotenv",
    "JSONB",
    "ARRAY",
    "AsyncAttrs",
    "async_sessionmaker",
    "create_async_engine",
    "Column",
    "Integer",
    "ForeignKey",
    "String",
    "BigInteger",
    "Enum",
    "Boolean",
    "DateTime",
    "Text",
    "Float",
    "Date",
    "func",
    "MetaData",
    "text",
    "Table",
    "JSON",
    "Interval",
    "Mapped",
    "mapped_column",
    "DeclarativeBase",
    "relationship",
    "MappedColumn",
    "select",
    "update",
    "delete",
    "desc",
    "extract",
    "case",
    "AsyncSession",
    "selectinload",
    "and_",
    "AsyncOpenAI",
    "cos",
    "radians",
    "sin",
    "sqrt",
    "atan2",
    "urllib3",
    "requests",
    "sys",
    "json",
    "BasicParser",
    "NetworkManager",
    "FileCache",
    "fromstring",
    "ContentType",
    "FSMContext",
    "Message",
    "StatesGroup",
    "State",
    "io",
    "sr",
    "AudioSegment",
    "Union",
    "FSInputFile",
    "KeyboardButtonPollType",
    "ReplyKeyboardMarkup",
    "KeyboardButton",
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "process",
    "fuzz",
    "Router",
    "F",
    "LabeledPrice",
    "PreCheckoutQuery",
    "CallbackQuery",
]
