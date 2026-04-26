"""Pydantic request and response schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class CustomerFeatures(BaseModel):
    """Input features for a single churn prediction."""

    credit_score:     int   = Field(..., ge=300, le=850)
    geography:        str   = Field(..., examples=["France", "Spain", "Germany"])
    gender:           str   = Field(..., examples=["Male", "Female"])
    age:              int   = Field(..., ge=18, le=100)
    tenure:           int   = Field(..., ge=0, le=10)
    balance:          float = Field(..., ge=0.0)
    num_of_products:  int   = Field(..., ge=1, le=4)
    has_cr_card:      int   = Field(..., ge=0, le=1)
    is_active_member: int   = Field(..., ge=0, le=1)
    estimated_salary: float = Field(..., ge=0.0)

    @field_validator("geography")
    @classmethod
    def validate_geography(cls, v: str) -> str:
        allowed = {"France", "Spain", "Germany"}
        if v not in allowed:
            raise ValueError(f"geography must be one of {allowed}")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        allowed = {"Male", "Female"}
        if v not in allowed:
            raise ValueError(f"gender must be one of {allowed}")
        return v


class PredictRequest(BaseModel):
    features: CustomerFeatures


class PredictResponse(BaseModel):
    prediction:  int
    label:       Literal["No Churn", "Churn"]
    probability: float = Field(..., description="Probability of the predicted class")


class TrainRequest(BaseModel):
    csv_path:      str = Field(..., description="Absolute path to the training CSV file")
    target_column: str = Field(default="Exited", description="Name of the target column")


class TrainResponse(BaseModel):
    message:       str
    model_path:    str
    training_rows: int
    accuracy:      float
