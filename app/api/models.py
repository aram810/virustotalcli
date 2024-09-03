import datetime
from typing import Literal

import pydantic


class _BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="allow",
    )


class LastAnalysisStats(_BaseModel):
    harmless: int
    malicious: int
    suspicious: int
    timeout: int
    undetected: int


class LookupAttributes(_BaseModel):
    last_analysis_date: datetime.datetime
    last_analysis_stats: LastAnalysisStats

    @pydantic.field_validator("last_analysis_date", mode="before")
    def convert_unix_timestamp(cls, value: int | float):
        if isinstance(value, (int, float)):
            return datetime.datetime.fromtimestamp(value)

        return value


class LookupData(_BaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    type: Literal["url", "ip_address"]
    attributes: LookupAttributes


class LookupResponse(_BaseModel):
    data: LookupData
