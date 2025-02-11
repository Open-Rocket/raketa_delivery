import os
import re
import io
import sys
import enum
import pytz
import json
import httpx
import asyncio
import logging
import urllib3
import requests
import speech_recognition as sr

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydub import AudioSegment
from lxml.html import fromstring
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta
from math import cos, radians, sin, sqrt, atan2
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Annotated, List, Union, Callable, Dict, Any, Awaitable

from parselab.cache import FileCache
from parselab.parsing import BasicParser
from parselab.network import NetworkManager

from aiogram import Bot, Dispatcher
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, BaseMiddleware, filters, F
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
    TelegramObject,
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
    "Dispatcher",
    "Bot",
    "filters",
    "CommandStart",
    "TelegramObject",
    "BaseMiddleware",
    "asyncio",
    "httpx",
    "re",
    "httpx" "asyncio",
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
    "Callable",
    "Dict",
    "Any",
    "Awaitable",
]
