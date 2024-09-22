from duckduckgo_search import DDGS
from markdownify import markdownify as md 
import requests
from pydantic import BaseModel
import instructor
#from langchain.llms import OpenAI
from openai import OpenAI
from typing import List
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI as PandasOpenAI
from langchain_openai import ChatOpenAI


class Oferta(BaseModel):
    titulo: str
    descripcion: str
    url: str
    precio: float

class Ofertas(BaseModel):
    ofertas: List[Oferta]


consulta = "Gorras en oferta bogotá"

resultados = DDGS().text(consulta, max_results=5)



client = instructor.from_openai(OpenAI())

print(resultados)


# Paso 3: Procesar los resultados de la búsqueda
textos = []
for resultado in resultados:

    peticion = requests.get(resultado["href"])
    contenido = md(peticion.content, strip=['sgv', 'javascript', 'head'])


    oferta = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        response_model=Ofertas,
        messages=[{"role": "user", "content": contenido}],
        )

    # #textos.append(oferta)
    # textos.append({
    #             'titulo': item.titulo,
    #             'descripcion': item.descripcion,
    #             'url': item.url,
    #             'precio': item.precio
    #         })
    print("Cantiadad: ", len(oferta.ofertas))
    for item in oferta.ofertas:
            textos.append({
                'proveedor': resultado["title"],
                'titulo': item.titulo,
                'descripcion': item.descripcion,
                'url': item.url,
                'precio': item.precio
            })


df = pd.DataFrame(textos)

print(df.head())

# Configurar el LLM de OpenAI para pandas-ai
llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", openai_api_key=openai_api_key, 
                     temperature=0)

sdf = SmartDataframe(df, config={"llm":llm})

pregunta = "Genera una grafica que muestre el precio más alto y el precio más bajo de cada 'proveedor'"


response = sdf.chat(pregunta)

print(response)

