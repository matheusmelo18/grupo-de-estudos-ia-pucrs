import os
import re
import statistics

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def obter_temperatura_servidor(datacenter: str) -> dict:
    """Retorna a temperatura atual em graus Celsius de um datacenter (sp-01, rs-02 ou rj-03)."""
    tabela = {"sp-01": 24.5, "rs-02": 21.0, "rj-03": 27.8}
    return {"datacenter": datacenter, "celsius": tabela[datacenter]}


def verificar_status_banco(cluster: str) -> dict:
    """Retorna o status operacional de um cluster de banco de dados (prod, homolog ou analytics)."""
    tabela = {"prod": "saudavel", "homolog": "degradado", "analytics": "offline"}
    return {"cluster": cluster, "status": tabela[cluster]}


def calcular_desvio_padrao(valores: list[float]) -> float:
    """Calcula o desvio padrao amostral de uma lista com pelo menos 2 numeros."""
    return round(statistics.stdev(valores), 2)


def validar_formato_documento(cnpj: str) -> dict:
    """Confere apenas o FORMATO de um CNPJ (14 digitos, com ou sem pontuacao); nao consulta a Receita."""
    so_digitos = re.sub(r"\D", "", cnpj)
    return {"cnpj": cnpj, "formato_valido": len(so_digitos) == 14 and so_digitos.isdigit()}


FERRAMENTAS = {
    "obter_temperatura_servidor": obter_temperatura_servidor,
    "verificar_status_banco": verificar_status_banco,
    "calcular_desvio_padrao": calcular_desvio_padrao,
    "validar_formato_documento": validar_formato_documento,
}


def responder(pergunta: str) -> tuple[str, str | None]:
    """Retorna (texto_final, nome_da_ferramenta_chamada ou None)."""
    config = types.GenerateContentConfig(
        tools=list(FERRAMENTAS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    contents = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    # Passo 1-2: o modelo decide se quer uma ferramenta
    response = client.models.generate_content(model=MODEL, contents=contents, config=config)
    if not response.function_calls:
        return response.text, None

    primeira = response.function_calls[0].name
    contents.append(response.candidates[0].content)

    # Passo 3: executar cada chamada pedida
    partes_resposta = []
    for chamada in response.function_calls:
        funcao = FERRAMENTAS.get(chamada.name)
        args = dict(chamada.args) if chamada.args else {}
        resultado = funcao(**args) if funcao else None
        partes_resposta.append(
            types.Part.from_function_response(name=chamada.name, response={"result": resultado})
        )

    # Passo 4: devolver ao modelo para a resposta final
    contents.append(types.Content(role="user", parts=partes_resposta))
    final = client.models.generate_content(model=MODEL, contents=contents, config=config)
    return final.text, primeira


# (prompt, ferramenta_esperada ou None quando NAO deve chamar ferramenta)
BATERIA = [
    ("Qual a temperatura do datacenter rs-02?", "obter_temperatura_servidor"),
    ("O cluster analytics esta funcionando?", "verificar_status_banco"),
    ("Qual o desvio padrao de 10, 12, 9, 15 e 11?", "calcular_desvio_padrao"),
    ("O CNPJ 12.345.678/0001-95 tem formato valido?", "validar_formato_documento"),
    ("Explique em duas frases o que e um cluster de banco de dados.", None),
    ("Para que serve o desvio padrao em monitoramento de servidores?", None),
]

if __name__ == "__main__":
    acertos = 0
    for pergunta, esperada in BATERIA:
        texto, chamada = responder(pergunta)
        ok = chamada == esperada
        acertos += ok
        print(f"{'OK ' if ok else 'FAIL'} esperada={esperada} chamou={chamada} | {pergunta}\n  -> {texto[:120]}")
    print(f"Roteamento correto: {acertos}/{len(BATERIA)}")
