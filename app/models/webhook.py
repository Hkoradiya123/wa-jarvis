from pydantic import BaseModel
from typing import Optional, List, Any

class Message(BaseModel):
    id: str
    body: str
    type: str
    t: int
    notifyName: str
    from_: str = "" # maps from 'from' in JSON
    to: str
    self: str
    ack: int
    isNewMsg: bool
    star: bool
    kic: bool
    isRevoked: bool
    isGroupMsg: bool
    isMedia: bool
    isNotification: bool
    isPSA: bool
    isForwarded: bool
    broadcast: bool
    mentionedJidList: List[str]
    isVcardOverMms: bool

class WebhookPayload(BaseModel):
    event: str
    session: str
    payload: Any # This can be complicated, focusing on message events
