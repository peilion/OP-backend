from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator


class AssetPostSchema(BaseModel):
    class asset(BaseModel):
        @validator("st_time", pre=True)
        def datetime_validate(cls, v):
            return str(datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ"))

        name: str
        sn: str
        st_time: datetime
        asset_level: int
        asset_type: int
        repairs: int
        station_id: int
        parent_id: Optional[int]
        memo: Optional[str]
        statu: int = 0

    base: asset
    info: dict


class FlattenAssetSchema(BaseModel):
    id: int
    name: str
    sn: Optional[str]
    lr_time: Optional[datetime] = None
    cr_time: Optional[datetime] = None
    md_time: Optional[datetime] = None
    st_time: Optional[datetime] = None
    asset_level: Optional[int]
    memo: Optional[str] = None
    health_indicator: Optional[float]
    statu: Optional[int]
    station_name: Optional[str] = None
    parent_id: Optional[int] = None
    repairs: Optional[int]
    mp_configuration: Optional[int]


class FlattenAssetListSchema(BaseModel):
    asset: Optional[List[Optional["FlattenAssetSchema"]]]


class AssetCardSchema(FlattenAssetSchema):
    is_domestic: bool
    oil_type: int
    design_output: float
    # health_indicator_history: Optional[List]


class NestAssetSchema(BaseModel):
    id: int
    name: str
    sn: str
    lr_time: Optional[datetime] = None
    cr_time: Optional[datetime] = None
    md_time: Optional[datetime] = None
    asset_level: int
    memo: Optional[str] = None
    health_indicator: float
    statu: int
    repairs: Optional[int]

    children: Optional[List[Optional["NestAssetSchema"]]]
    station_id: int

    class Config:
        orm_mode = True


NestAssetSchema.update_forward_refs()  # for self referencing orm model


class NestAssetListSchema(BaseModel):
    asset: Optional[List[Optional["NestAssetSchema"]]]


class StatuStatisticSchema(BaseModel):
    Excellent: Optional[int] = 0
    Good: Optional[int] = 0
    Moderate: Optional[int] = 0
    Poor: Optional[int] = 0
    Offline: Optional[int] = 0


class StationStatisticSchema(BaseModel):
    class item(BaseModel):
        station: Optional[int]
        cnt: Optional[int]

    res: Optional[List[Optional["item"]]]


class TypeStatisticSchema(BaseModel):
    class item(BaseModel):
        asset_type: Optional[int]
        cnt: Optional[int]

    res: Optional[List[Optional["item"]]]


class TypeStationSchema(BaseModel):
    class item(BaseModel):
        name: str
        PumpUnit: Optional[int] = 0
        Pump: Optional[int] = 0
        Motor: Optional[int] = 0
        Rotor: Optional[int] = 0
        Stator: Optional[int] = 0
        Bearing: Optional[int] = 0

    res: Optional[List[Optional["item"]]]
    update_time: Optional[datetime] = None


class MSETSimilaritySchema(BaseModel):
    id: list
    time: list
    similarity: list
    threshold: list
