import os
import requests
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field


class ElevenLabsModel(BaseModel):
    model_id: str
    name: str
    description: Optional[str] = None
    token_cost_factor: float


def get_elevenlabs_models() -> List[ElevenLabsModel]:
    """
    Fetch available models from the ElevenLabs API.

    Returns:
        List[ElevenLabsModel]: A list of ElevenLabsModel objects containing model information.

    Raises:
        HTTPException: If the API request fails or if the API key is not set.
    """
    url = "https://api.elevenlabs.io/v1/models"
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500, detail="ELEVENLABS_API_KEY environment variable is not set"
        )

    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        models = [
            ElevenLabsModel(
                model_id=model["model_id"],
                name=model["name"],
                description=model.get("description"),
                token_cost_factor=model["token_cost_factor"],
            )
            for model in data
        ]
        return models
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


if __name__ == "__main__":
    try:
        models = get_elevenlabs_models()
        for model in models:
            print(f"Model ID: {model.model_id}, Name: {model.name}")
    except HTTPException as e:
        print(f"Error: {e.detail}")
