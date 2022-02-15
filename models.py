
from cgitb import text
from enum import Enum
from optparse import Option
from typing import List, Optional
from pydantic import BaseModel


class EmojiObject(BaseModel):
    index: int
    length: int
    productId: Optional[str]
    emojiId: Optional[str]

class MentioneesObject(BaseModel):
  index: int
  length: int
  userId: str

class MentionObject(BaseModel):
  mentionees: List[MentioneesObject]

class ContentProviderObject(BaseModel):
  type: str
  originalContentUrl: Optional[str]
  previewImageUrl: Optional[str]

class ImageSetObject(BaseModel):
  id: Optional[str]
  index: int
  total: int

class MessageObject(BaseModel):
    type: str
    id: Optional[str]
    contentProvider: Optional[ContentProviderObject]
    imageSet: Optional[ImageSetObject]
    text: Optional[str]
    emojis: Optional[List[EmojiObject]]
    mention: Optional[MentionObject]
    duration: Optional[int]
    fileName: Optional[str]
    fileSize: Optional[str]
    title: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class SourceObject(BaseModel):
    type: str
    userId: str
    groupId: Optional[str]
    roomId: Optional[str]


class EventObject(BaseModel):
    type: str
    message: Optional[MessageObject]
    timestamp: int
    source: SourceObject
    replyToken: Optional[str]
    mode: str


class UserProfile(BaseModel):
    displayName: str
    userId: str
    language: str
    pictureUrl: Optional[str]
    statusMessage: Optional[str]
