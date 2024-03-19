onmessage = async(e) => {
	output = e.data[3];
	dmCss = e.data[4];
	dmLogo = e.data[5];
	errorHTML = e.data[6];
	colors = e.data[7];
	
	mainFunc = Function(`return ${e.data[2]}`)();

	postMessage(await mainFunc(e.data[0], e.data[1]));
}