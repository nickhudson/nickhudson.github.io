# Imports
import asyncio
# import quopri
import os
import subprocess
import sys
#image handler
from pyodide.http import open_url
from pyodide.ffi import create_proxy, to_js
from js import document, console, alert, Object, FileReader, encodeURIComponent, processHTML 
import base64
from pathlib import Path
#custom scripts
from config import set_config, get_config
from custom_fetch import get_fetch

# Global Constants & Variables
TEMP_FILE = []
CONFIG = get_config()

fileTypes = [
	'text/html', 
	'message/rfc822'
]
uploadInput = document.getElementById('upload')
processButton = document.getElementById('process')
downloadButton = document.getElementById('download')

contentEl = document.getElementById('content')
outputEl = document.getElementById('output')
outputCodeEl = document.getElementById('output-code')
viewModeEl = contentEl.querySelector('#view-mode')

#Testing set config
#set_config("test", "test")

# Functions
def hideShowEl(hideEl, showEl, cl):
	hideEl.classList.add(cl)
	showEl.classList.remove(cl)

	if len(showEl.classList) == 0:
		showEl.removeAttribute('class')

def read_complete(e):
	loadedFile = uploadInput.files.item(0)
	codeStr = e.target.result.encode().decode()

	outputEl.srcdoc = outputCodeEl.innerText = codeStr

	TEMP_FILE.append({
		'name': loadedFile.name.rsplit('.', 1)[0],
		'type': loadedFile.type,
		'data': codeStr
	})

	processButton.disabled = False
	downloadButton.disabled = True
	contentEl.classList.remove('hidden')

	if len(contentEl.classList) == 0:
		contentEl.removeAttribute('class')
	
	if viewModeEl.style.visibility == 'hidden':
		viewModeEl.style.visibility = 'visible'

async def read_file(e):
	fileList = uploadInput.files

	for f in fileList:
		if fileTypes.count(f.type) > 0:
			reader = FileReader.new()
			onLoadEvent = create_proxy(read_complete)

			reader.onload = onLoadEvent
			reader.readAsText(f)
	
	return

async def process_file(e):
	if len(TEMP_FILE) > 0:
		latestFile = TEMP_FILE[len(TEMP_FILE) - 1]
		elData = viewModeEl.dataset

		if latestFile['type'] == 'text/html':
			updatedHTML = await processHTML(
				latestFile['data'], 
				to_js(get_config())
			)

			latestFile['data'] = outputEl.srcdoc = outputCodeEl.innerText = updatedHTML.data
			uploadInput.value = ''

			processButton.disabled = True

			if updatedHTML.status == 'error':
				if elData.viewMode == 'code':
					elData.viewMode = 'design'
					viewModeEl.innerHTML = 'View Code'
					hideShowEl(outputCodeEl, outputEl, 'hidden')
				
				viewModeEl.style.visibility = 'hidden'
			else:
				downloadButton.disabled = False
			return
	
	return alert(f'Please upload one of the following file types: {", ".join(fileTypes)}')

def download_file(e):
	if len(TEMP_FILE) > 0:
		outputFile = TEMP_FILE[len(TEMP_FILE) - 1]
		uri = f'data:{outputFile["type"]};charset=utf-8,{encodeURIComponent(outputFile["data"])}'
		tag = document.createElement('a')

		tag.href = uri
		tag.download = f'{outputFile["name"]} copy'

		tag.style.display = 'none'
		document.body.appendChild(tag)
		tag.click()
		document.body.removeChild(tag)

def clear_file(e):
	e.preventDefault()

	if len(TEMP_FILE) > 0:
		TEMP_FILE.clear()
		uploadInput.value = outputEl.srcdoc = ''
		processButton.disabled = downloadButton.disabled = True
		contentEl.classList.add('hidden')

		if viewModeEl.style.visibility == 'hidden':
			viewModeEl.style.visibility = 'visible'

def change_view(e):
	e.preventDefault()

	elData = e.target.dataset
	fileData = TEMP_FILE[len(TEMP_FILE) - 1]['data']

	if elData.viewMode == 'design':
		elData.viewMode = 'code'
		e.target.innerHTML = 'View Design'

		hideShowEl(outputEl, outputCodeEl, 'hidden')
	else: 
		elData.viewMode = 'design'
		e.target.innerHTML = 'View Code'

		hideShowEl(outputCodeEl, outputEl, 'hidden')
		
#calls get_fetch(url, type)
async def fetch_req(url):
	response = await get_fetch(url)
	return response

async def main():
	#task = await fetch_req("https://dummyjson.com/products/1")

	fileEvent = create_proxy(read_file)
	processEvent = create_proxy(process_file)
	downloadEvent = create_proxy(download_file)
	clearEvent = create_proxy(clear_file)
	viewEvent = create_proxy(change_view)

	uploadInput.accept = ','.join(fileTypes)

	# Event Listeners
	uploadInput.addEventListener('change', fileEvent)
	processButton.addEventListener('click', processEvent)
	downloadButton.addEventListener('click', downloadEvent)
	contentEl.querySelector('.close').addEventListener('click', clearEvent)
	contentEl.querySelector('#view-mode').addEventListener('click', viewEvent)

# Output & Misc + Guard rails to run when file is invoked directly
if __name__ == '__main__':
	# Can't use run as an async queue already exists so we create another task
	main_task = asyncio.create_task(main())
