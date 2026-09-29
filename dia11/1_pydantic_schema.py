import os
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


class PerfilUsuario(BaseModel):
    nome: str = Field(..., description="Nome completo do usuario")
    idade: int = Field(..., description="Idade do usuario em anos", ge=0, le=120)
    habilidades: list[str] = Field(..., description="Lista de habilidades do usuario")
    status: Literal["ativo", "inativo", "pendente"] = Field(..., description="Status do usuario")


TEXTO = (
    "Oi, sou a Marina Souza, tenho 35 anos e trabalho com Python, SQL e Power BI. "
    "Minha conta ainda esta aguardando aprovacao do time."
)


def extrair_perfil(texto: str) -> PerfilUsuario:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Extraia o perfil do usuario do texto abaixo.\n\n{texto}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema= PerfilUsuario
        ),
    )
    # response.parsed ja vem como instancia de PerfilUsuario
    return response.parsed


if __name__ == "__main__":
    perfil = extrair_perfil(TEXTO)
    print(type(perfil).__name__)
    print(perfil.model_dump_json(indent=2))
    print(PerfilUsuario.model_json_schema())
