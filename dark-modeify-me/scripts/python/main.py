# Imports
import asyncio
# import quopri
import os
import subprocess
import sys
#image handler
from pyodide.http import open_url
from pyodide.ffi import create_proxy, to_js
from js import window, document, console, alert, Object, parseInt, setTimeout, clearTimeout, FileReader, encodeURIComponent, ResizeObserver, typeOf, trackInput, processHTML 
import math
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

currWinWidth = 0

# DOM Elements
infoButton = document.getElementById('info')
uploadInput = document.getElementById('upload')
processButton = document.getElementById('process')
downloadButton = document.getElementById('download')

popoverEls = document.getElementsByClassName('popover')
infoEl = document.getElementById('how-to')
contentEl = document.getElementById('content')
outputEl = document.getElementById('output')
outputCodeEl = document.getElementById('output-code')
viewModeEl = contentEl.querySelector('#view-mode')

#Testing set config
#set_config("test", "test")

# Functions
def toggle_elem(hideEl, showEl, cl):
	hideEl.classList.add(cl)
	showEl.classList.remove(cl)

	if len(showEl.classList) == 0:
		showEl.removeAttribute('class')

async def popover_pos(e, self = ''):
	if hasattr(e, 'offsetTop'):
		popBtn = e
	else:
		popBtn = infoButton
		
	global currWinWidth

	popElem = popBtn.popoverTargetElement
	popWrapper = popElem.getElementsByClassName('pop-wrapper')[0]
	popArrow = popElem.getElementsByClassName('pop-arrow')[0]

	popWrapLeft = popWrapper.offsetLeft
	popWrapRight = popWrapper.getBoundingClientRect().right
	popBtnLeft = popBtn.offsetLeft
	popArrowLeft = popArrow.getBoundingClientRect().left

	popWrapWidth = popWrapper.getBoundingClientRect().width
	popBtnWidth = popBtn.offsetWidth
	popArrowWidth = popArrow.getBoundingClientRect().width

	popWrapMidPnt = popWrapLeft + (popWrapWidth / 2)
	popBtnMidPnt = popBtnLeft + (popBtnWidth / 2)
	popArrowMidPnt = popArrowLeft + (popArrowWidth / 2)

	topMargin = 15
	popElPad = parseInt(window.getComputedStyle(popElem).getPropertyValue('padding'))

	async def popelem_pos():
		global currWinWidth
		
		popWrapper.style.top = (
			popBtn.offsetTop + 
			popBtn.offsetHeight -
			popElPad + 
			topMargin
		)
		
		if window.innerWidth > 800:
			if popWrapLeft <= popElPad and popWrapMidPnt >= popBtnMidPnt:
				popWrapper.style.margin = 'initial'
				popWrapper.style.left = 'auto'
				popWrapper.style.float = 'left'
			elif popBtnMidPnt > window.innerWidth / 2 and popWrapRight >= window.innerWidth - popElPad and popWrapLeft <= (popBtnLeft - popBtnWidth):
				popWrapper.style.margin = 'initial'
				popWrapper.style.left = 'auto'
				popWrapper.style.float = 'right'
			else:
				popWrapper.style.margin = 'initial'
				popWrapper.style.float = 'none'
				popWrapper.style.left = (
					popBtnMidPnt -
					(popWrapWidth / 2) -
					popElPad
				)

			currWinWidth = window.innerWidth
		else: 
			popWrapper.style.float = 'none'
			popWrapper.style.left = 'auto'
			popWrapper.style.margin = '0 auto'

	def poparrow_pos():
		clearTimeout(create_proxy(poparrow_pos))

		def pa_pos_left():
			clearTimeout(pa_pos_left)

			adjustForPopBtn = 0
			
			if math.floor(popBtnWidth) >= math.floor(popArrowWidth):
				adjustForPopBtn = popBtnWidth / 2

			popArrow.style.left = popBtnLeft - popWrapLeft - (popElPad / 2) + abs(popArrowWidth-popBtnWidth) + adjustForPopBtn
			
		if abs(popBtnMidPnt-popArrowMidPnt) > 4:
			popArrow.style.margin = '0em 0em -2px'
			popArrow.style.position = 'relative'
			setTimeout(pa_pos_left(), 0)
		else:
			popArrow.removeAttribute('style')

	await popelem_pos()
	setTimeout(create_proxy(poparrow_pos), 500)

async def toggle_popover(e):
	e.preventDefault()
	
	if hasattr(e.target, 'popoverTargetElement'):
		popBtn = e.target
	else:
		popBtn = infoButton

	popElem = popBtn.popoverTargetElement
	popoverProxy = create_proxy(popover_pos)
	popoverResize = ResizeObserver.new(popoverProxy)

	trackInput(e)

	if e.type == 'mouseover':
		popElem.showPopover()
		await popover_pos(popBtn)
		popoverResize.observe(document.body)

	if e.type == 'click' and hasattr(popElem, 'matches') and popElem.matches(':popover-open'):
		popElem.hidePopover()
	elif e.type == 'click' and hasattr(e.target, 'popoverTargetElement') and e.target.popoverTargetElement is not None:
		popElem.showPopover()

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

	trackInput(e)
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
			trackInput(e)

			if updatedHTML.status == 'error':
				if elData.viewMode == 'code':
					elData.viewMode = 'design'
					viewModeEl.innerHTML = 'View Code'
					toggle_elem(outputCodeEl, outputEl, 'hidden')
				
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

		trackInput(e)

def clear_file(e):
	e.preventDefault()

	if len(TEMP_FILE) > 0:
		TEMP_FILE.clear()
		uploadInput.value = outputEl.srcdoc = ''
		processButton.disabled = downloadButton.disabled = True
		contentEl.classList.add('hidden')

		if viewModeEl.style.visibility == 'hidden':
			viewModeEl.style.visibility = 'visible'

		trackInput(e)

def change_view(e):
	e.preventDefault()

	elData = e.target.dataset
	trackInput(e)

	if elData.viewMode == 'design':
		elData.viewMode = 'code'
		e.target.innerHTML = 'View Design'

		toggle_elem(outputEl, outputCodeEl, 'hidden')
	else: 
		elData.viewMode = 'design'
		e.target.innerHTML = 'View Code'

		toggle_elem(outputCodeEl, outputEl, 'hidden')
		
# Calls get_fetch(url, type)
async def fetch_req(url):
	response = await get_fetch(url)
	return response

async def main():
	popoverEvent = create_proxy(toggle_popover)
	fileEvent = create_proxy(read_file)
	processEvent = create_proxy(process_file)
	downloadEvent = create_proxy(download_file)
	clearEvent = create_proxy(clear_file)
	viewEvent = create_proxy(change_view)

	uploadInput.accept = ','.join(fileTypes)

	# Event Listeners
	infoEl.addEventListener('click', popoverEvent)
	infoButton.addEventListener('mouseover', popoverEvent)
	uploadInput.addEventListener('click', trackInput)
	uploadInput.addEventListener('change', fileEvent)
	processButton.addEventListener('click', processEvent)
	downloadButton.addEventListener('click', downloadEvent)
	contentEl.querySelector('.close').addEventListener('click', clearEvent)
	contentEl.querySelector('#view-mode').addEventListener('click', viewEvent)

# Output & Misc + Guard rails to run when file is invoked directly
if __name__ == '__main__':
	# Can't use run as an async queue already exists so we create another task
	main_task = asyncio.create_task(main())
