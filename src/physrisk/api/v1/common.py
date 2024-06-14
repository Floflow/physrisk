from typing import Dict, List, Optional, Union

import numpy as np
from pydantic import BaseModel, Field


class TypedArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def validate_type(cls, val):
        return np.array(val, dtype=cls.inner_type)  # type: ignore


class ArrayMeta(type):
    def __getitem__(cls, t):
        return type("Array", (TypedArray,), {"inner_type": t})


class Array(np.ndarray, metaclass=ArrayMeta):
    pass


class Asset(BaseModel, extra="allow"):
    """Defines an asset. An asset is identified first by its asset_class and then by its type within the class.
    An asset's value may be impacted through damage or through disruption
    disruption being reduction of an asset's ability to generate cashflows
    (or equivalent value, e.g. by reducing expenses or increasing sales).
    """

    asset_class: str = Field(
        description="name of asset class; corresponds to physrisk class names, e.g. PowerGeneratingAsset"
    )
    latitude: float = Field(description="Latitude in degrees")
    longitude: float = Field(description="Longitude in degrees")
    type: Optional[str] = Field(None, description="Type of the asset <level_1>/<level_2>/<level_3>")
    location: Optional[str] = Field(
        None, description="Location (e.g. Africa, Asia, Europe, Global, Oceania, North America, South America)"
    )
    capacity: Optional[float] = Field(None, description="Power generation capacity")
    attributes: Optional[Dict[str, str]] = Field(
        None, description="Bespoke attributes (e.g. number of storeys, structure type, occupancy type)"
    )


class Assets(BaseModel):
    """Defines a collection of assets."""

    items: List[Asset]


class BaseHazardRequest(BaseModel):
    group_ids: List[str] = Field(
        ["public"],
        description="""List of data groups which can be used to service the request,
            e.g. 'osc': available to OS-Climate members (e.g. pending license decision),
                 'public'.""",
    )


class Country(BaseModel):
    """Country information."""

    country: str
    continent: str
    country_iso_a3: str


class Countries(BaseModel):
    """List of Country."""

    items: List[Country]


class IntensityCurve(BaseModel):
    """Hazard indicator intensity curve. Acute hazards are parameterized by event intensities and
    return periods in years. Chronic hazards are parameterized by a set of index values.
    Index values are defined per indicator."""

    intensities: List[float] = Field([], description="Hazard indicator intensities.")
    return_periods: Optional[List[float]] = Field(
        [], description="[Deprecated] Return period in years in the case of an acute hazard."
    )
    index_values: Optional[Union[List[float], List[str]]] = Field(
        [],
        description="Set of index values. \
            This is return period in years in the case of an acute hazard or \
            a set of indicator value thresholds in the case of a multi-threshold chronic hazard.",
    )
    index_name: str = Field(
        "",
        description="Name of the index. In the case of an acute hazard this is 'return period'; \
            for a multi-threshold chronic hazard this is 'threshold'.",
    )


class ExceedanceCurve(BaseModel):
    """General exceedance curve (e.g. hazazrd, impact)."""

    values: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")
    exceed_probabilities: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")

    class Config:
        arbitrary_types_allowed = True


class Distribution(BaseModel):
    """General exceedance curve (e.g. hazazrd, impact)."""

    bin_edges: np.ndarray = Field(default_factory=lambda: np.zeros(11), description="")
    probabilities: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")

    class Config:
        arbitrary_types_allowed = True


class HazardEventDistrib(BaseModel):
    """Intensity curve of an acute hazard."""

    intensity_bin_edges: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")
    probabilities: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")
    path: List[str] = Field([], description="Path to the hazard indicator data source.")

    class Config:
        arbitrary_types_allowed = True


class VulnerabilityCurve(BaseModel):
    """Defines a damage or disruption curve."""

    asset_type: str = Field(...)
    location: str = Field(...)
    event_type: str = Field(description="hazard event type, e.g. RiverineInundation")
    impact_type: str = Field(description="'Damage' or 'Disruption'")
    # intensity: Array = Field(...)
    # intensity: np.ndarray = np.zeros(1) #Field(default_factory=lambda: np.zeros(1))
    intensity: List[float] = Field(...)
    intensity_units: str = Field(description="units of the intensity")
    impact_mean: List[float] = Field(description="mean impact (damage or disruption)")
    impact_std: List[float] = Field(description="standard deviation of impact (damage or disruption)")

    class Config:
        arbitrary_types_allowed = True


class VulnerabilityCurves(BaseModel):
    """List of VulnerabilityCurve."""

    items: List[VulnerabilityCurve]


class VulnerabilityDistrib(BaseModel):
    """Defines a vulnerability matrix."""

    intensity_bin_edges: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")
    impact_bin_edges: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")
    prob_matrix: np.ndarray = Field(default_factory=lambda: np.zeros(10), description="")

    class Config:
        arbitrary_types_allowed = True
