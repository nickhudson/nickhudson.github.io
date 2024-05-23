from pyodide.http import pyfetch
from pyodide.ffi import JsException
from pathlib import Path
import base64

async def download(urlInput):
    filename = Path(urlInput).name
    response = await pyfetch(
            url=urlInput,
            method='GET',
    )
    if response.status == 200:
        status = response.status
        with open(filename, mode="wb") as file:
            file.write(await response.bytes())
        return filename, status
    else:
        status = response.status
        filename = None
        return filename, status

async def load(urlInput, type):
    match type: 
        case "fetch":
            try:
                response = await pyfetch(
                    url=urlInput,
                    method='GET',
                )
                if response.ok:
                    data = await response.json()

            except JsException:
                return None
            
            except:
                print("ERROR wtih fetch")
                return None
            
        case "image":
            response_content = await download(urlInput)
            if response_content[1] == 200:
                data = base64.b64encode(open(response_content[0], "rb").read()).decode("utf-8")
                src = f"data:image/png;base64,{data}"
                return src  
            else:
                src = None
                return src

    return data

async def get_fetch(url, type = "fetch"):
    res = await load(url, type)
    if res is None:
        return None
    else:
        return res 