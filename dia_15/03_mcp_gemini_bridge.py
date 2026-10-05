"""Dia 15 - Ponte MCP <-> Gemini (copiada do Dia 14 e refatorada).

Diferenca para a versao do Dia 14: a logica agora vive na funcao reutilizavel
`perguntar(sessao, pergunta)`, com um laco de chamadas de ferramenta (o modelo
pode chamar varias ferramentas em sequencia) e um trace de cada chamada.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MAX_RODADAS = 10  # protecao contra laco infinito de chamadas de ferramenta


def gerar(pergunta, contents, config=None):
    last = None
    for m in MODELS:
        try:
            if config is not None:
                return client.models.generate_content(
                    model=m, contents=contents, config=config
                ), m
            return client.models.generate_content(
                model=m, contents=contents
            ), m
        except Exception as e:  # 503/404 -> tenta proximo
            last = e
            continue
    raise last if last else RuntimeError("sem modelo")


def converter_mcp_para_gemini_tools(mcp_tools):
    gemini_tools = []
    for t in mcp_tools.tools:
        gemini_tools.append(
            types.FunctionDeclaration(
                name=t.name,
                description=t.description or "",
                parameters_json_schema=t.inputSchema,
            )
        )
    return types.Tool(function_declarations=gemini_tools)


async def perguntar(sessao: ClientSession, pergunta: str) -> str:
    """Envia a pergunta ao Gemini e executa as ferramentas MCP ate a resposta final."""
    mcp_tools = await sessao.list_tools()
    tool_config = types.GenerateContentConfig(
        tools=[converter_mcp_para_gemini_tools(mcp_tools)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    contents = [pergunta]
    for _ in range(MAX_RODADAS):
        resp, usado = gerar(pergunta, contents, tool_config)
        if not resp.function_calls:
            return resp.text

        model_content = resp.candidates[0].content  # preserva thought_signature
        contents.append(model_content)

        partes_resposta = []
        for fc in resp.function_calls:
            # TRACE: cada ferramenta chamada e seus argumentos
            print(f"  >> [trace] ferramenta={fc.name} args={dict(fc.args)}")
            result = await sessao.call_tool(fc.name, dict(fc.args))
            texto = result.content[0].text if result.content else ""
            if result.isError:
                texto = f"ERRO da ferramenta: {texto}"
            partes_resposta.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": texto},
                )
            )
        contents.append(types.Content(role="user", parts=partes_resposta))

    return "(limite de rodadas de ferramentas atingido)"


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["server_utils.py"], env=None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for pergunta in ["Quanto e 25 graus Celsius em Fahrenheit?"]:
                print("PERGUNTA:", pergunta)
                print(" resposta final:", await perguntar(session, pergunta))


if __name__ == "__main__":
    asyncio.run(main())
