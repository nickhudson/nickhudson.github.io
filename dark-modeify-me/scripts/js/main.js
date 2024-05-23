// Google Analytics
window.dataLayer = window.dataLayer || [];

function gtag() {
	dataLayer.push(arguments);
}

gtag('js', new Date());
gtag('config', 'G-WMPJ15XJ5M');

// Declare web worker constant for browsers that support workers
const processWorker = window.Worker ? new Worker('./scripts/js/worker.js') : null;

// Process and return the data passed from index.html (Python)
function pyToJs(o) {
	if (Array.isArray(o)) {
		return o.map(val => 
			pyToJs(val)
		);
	};

	// For Python dictionaries, convert the 'Proxy' types to a js object and traverse the tree
	if (typeof o === 'object') {
		const obj = Object.fromEntries(o);

		for (const p in obj) {
			if (typeof obj[p] === 'object')
				obj[p] = pyToJs(obj[p])
		};

		return obj;
	};

	return pyscript.interpreter.globals.get(o) || o;
};

// Simple fetch function, returns tthe response data as text
function urlToText(url, file={dyn: false}) {
	if (file.dyn == true) {
		// console.log('dynamic file!');
		return;
	}

	return fetch(url).then(res =>
		res.text()
	).catch(e => {
		console.error(e);
	});
};

// Main function for processing uploaded HTML files
async function processHTML(str, obj) {
	const html = [str],
				config = pyToJs(obj),

				// Output object for storing data that will be returned
				output = {},

				dmCss = await urlToText(config.darkMode.assets.dmCss),
				dmLogo = await urlToText(config.darkMode.assets.dmLogoSwap),
				errorHTML = await urlToText(config.darkMode.assets.error),
				
				colors = await urlToText(
					`scripts/python/${config.filePath.local.stouts}` + 
					config.fileName.colors,
				),

				processDM = async(arr, obj2) => {
					// Declare all constants and variables
					const dmHTML = arr,
								dmConfig = obj2.darkMode,
								
								// Error object for error handling
								error = {},

								// Regular expressions
								codeRegex = new RegExp(dmConfig.regex.code, 'g'),
								dmCol1Regex = new RegExp(dmConfig.regex.dmCssColor1, 'g'),
								dmCol2Regex = new RegExp(dmConfig.regex.dmCssColor2, 'g'),
								msoRegex = new RegExp(dmConfig.regex.msoCond, 'g'),
								styleRegex = new RegExp(dmConfig.regex.styleClose, 'i'),
								tagRegex = new RegExp(dmConfig.regex.tagOpen, 'i'),
								classRegex = new RegExp(dmConfig.regex.classAttr, 'i'),
								bgColorRegex = new RegExp(dmConfig.regex.bgColor, 'i'),
								hexRegex = new RegExp(dmConfig.regex.hexValue, 'i'),
								headRegex = new RegExp(dmConfig.regex.headTag, 'i'),
								metaRegex = new RegExp(dmConfig.regex.metaTag, 'i'),
								bodyRegex = new RegExp(dmConfig.regex.bodyTag, 'i'),
								tFullRegex = new RegExp(dmConfig.regex.tableFull, 'i'),
								tMainRegex = new RegExp(dmConfig.regex.tableMain, 'i'),
								bgElRegex = new RegExp(dmConfig.regex.tableTdBg, 'gi'),
								logoRegex = new RegExp(dmConfig.regex.logo, 'i'),
								btnRegex = new RegExp(dmConfig.regex.buttons, 'gi'),

								// Declare all functions
								strToRegex = (str2) => {
									return str2.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
								},

								hexToHSL = (str2) => {
									const rgb = {},
												hsl = {};

									str2 = str2.replace('#', '');

									if (str2.length === 3) {
										rgb.r = +`0x${str2[0]}${str2[0]}` / 255;
										rgb.g = +`0x${str2[1]}${str2[1]}` / 255;
										rgb.b = +`0x${str2[2]}${str2[2]}` / 255;
									} else if (str2.length === 6) {
										rgb.r = +`0x${str2[0]}${str2[1]}` / 255;
										rgb.g = +`0x${str2[2]}${str2[3]}` / 255;
										rgb.b = +`0x${str2[4]}${str2[5]}` / 255;
									} else {
										return;
									}
									
									rgb.cmin = Math.min(rgb.r, rgb.g, rgb.b);
									rgb.cmax = Math.max(rgb.r, rgb.g, rgb.b);
									rgb.dlt = rgb.cmax - rgb.cmin;
									
									if (rgb.dlt === 0)
										hsl.h = 0;
									else if (rgb.cmax === rgb.r)
										hsl.h = ((rgb.g - rgb.b) / rgb.dlt) % 6;
									else if (rgb.cmax === rgb.g)
										hsl.h = (rgb.b - rgb.r) / rgb.dlt + 2;
									else
										hsl.h = (rgb.r - rgb.g) / rgb.dlt + 4;
										
									hsl.h = Math.round(hsl.h * 60);
									hsl.l = (rgb.cmax + rgb.cmin) / 2
									hsl.s = rgb.dlt === 0 ? 0 : rgb.dlt / (1 - Math.abs(2 * hsl.l - 1));

									hsl.s = +(hsl.s * 100).toFixed(1);
									hsl.l = +(hsl.l * 100).toFixed(1);

									return hsl;
								},

								addClass = (e, cl) => {
									return new Promise(rslv => {
										const elList = dmHTML.slice(-1)[0]
														.match(
															typeof e === 'string' ? 
															strToRegex(e) :
															e
														);

										if (elList) {
											return elList.map((el) => {
												const tagOpen = el.match(tagRegex)?.join(),
															classAttr = el.match(classRegex)?.join(),
																
															dmEl = el.replace(
																classAttr ? classAttr : tagOpen, 
																() => {
																	if (classAttr) {
																		// Replace any previous occurences of dark-mode classes before adding new ones
																		const cleanAttr = classAttr.replace(/dm-[\w-]*/g, '');

																		return cleanAttr.replace(
																				'class="', 
																				`class="${cl} `
																			);
																	}

																	return `${tagOpen} class="${cl}"`;
																}
															);

												if (classAttr?.includes(cl))
													return rslv();

												return rslv(
													dmHTML.push(
														dmHTML.pop().replace(
															el,
															dmEl
														)
													)
												);
											})
										}

										rslv(
											error.element = `Sorry, no ${e.toString()} tag found; could not add class(es)!`
										);
									});
								},

								dynamicCss = (str2) => {
									const colorData = () => {
													try {
														JSON.parse(colors);
													} catch (e) {
														return colors;
													}
														return JSON.parse(colors).modeType;
												},

												color_1 = colorData().dark.backgroundColor,
												color_2 = colorData().light.backgroundColor,

												updatedCss = str2.replace(dmCol1Regex, color_1)
													.replace(dmCol2Regex, color_2);
													
									return updatedCss;
								},

								insertMeta = () => {
									const headOpen = dmHTML.slice(-1)[0]
													.match(headRegex),

												meta = dmConfig.assets.metaTag;

									if (!dmHTML.slice(-1)[0].match(metaRegex)) {
										return dmHTML.push(
											dmHTML.pop().replace(
												headOpen,
												`
													${headOpen}\n
													${meta}\n
												`
											)
										);
									}
								},
								
								insertCss = () => {
									if (
										dmHTML.length && 
										dmHTML.slice(-1)[0].match(styleRegex)
									) {
										return dmHTML.push(
											dmHTML.pop().replace(
												styleRegex,
												`\n${dynamicCss(dmCss)}\n`
											)
										);
									}

									error.css = 'Sorry, no stylesheet found!';
								},
								
								insertLogoSwap = () => {
									const logo = dmHTML.slice(-1)[0]
													.match(logoRegex)
													?.slice(0)[0],

												dmLogoWrap = dmLogo.split(codeRegex);
												
									if (logo) {	
										const logoLink = logo.replace(/<\/*t[rd].*>/g, '')
														.trim(),
														
													logoTD = logo.match(/<td.*>/g).pop(),
													
													dmLogoTD = dmLogoWrap[0].split(msoRegex)
														.slice(-1)[0]
														.match(/<td.*>/g)
														.pop();

										dmHTML.push(
											dmHTML.pop().replace(
												logoRegex,
												`
													${dmLogoWrap[0].replace(
														dmLogoTD, 
														logoTD
													)}
													${logoLink}
													${dmLogoWrap[1]}
												`
											)
										);

										return addClass(
											logoLink,
											'dm-hide'
										);
									}

									error.logo = 'Sorry, no logo found!';
								},
								
								overrideBG = (e, pct, cl) => {
									const elList = dmHTML.slice(-1)[0]
													.match(
														typeof e === 'string' ? 
														strToRegex(e) :
														e
													);
									
									if (elList) {
										elList.forEach((el) => {
											const hex = el.match(bgColorRegex)
															?.slice(-1)[0]
															.match(hexRegex)
															?.pop();

											if (hex) {
												const lum = hexToHSL(hex).l;

												if (
													pct >= 50 && lum >= pct ||
													pct < 50 && lum <= pct
												)
													return addClass(
														el, 
														cl
													);
											}
										});
									}
								};

					// Call all functions					
					insertMeta();
					insertCss();
					await addClass(bodyRegex, 'nyt');
					await addClass(tFullRegex, 'dm-bg-dark');
					await addClass(tMainRegex, 'dm-bg-dark dm-txt-light');

					if (dmConfig.logoSwap)
						await insertLogoSwap();

					await overrideBG(bgElRegex, 75, 'dm-bg-dark dm-txt-light');
					await overrideBG(btnRegex, 75, 'dm-bg-light dm-txt-dark');
					await overrideBG(btnRegex, 10, 'dm-bg-light dm-txt-dark');

					// Add erros (if any exists) to the output, otherwise add the processed data
					if (Object.keys(error).length) {
						output.status = 'error';
						output.data = errorHTML.replace(
							codeRegex,
							Object.values(error)
							.map((e) => {
								console.error(e);
								return `<p>${e}</p>`;
							})
							.join('')
						);
					} else {
						output.status = 'ok';
						output.data = dmHTML.pop();
					}

					// Return the output
					return output;
				};

	if (config.darkMode.autoDarkMode) { 
		// Send the function to the worker file and return the response
		if (window.Worker) {
			const msgPromise = new Promise(rslv => {
							processWorker.onmessage = (e) => {
								rslv(Object.assign(
									output,
									e.data
								));
							};
						});

			processWorker.postMessage([
				html,
				config,
				processDM.toString(),
				output,
				dmCss,
				dmLogo,
				errorHTML,
				colors
			]);

			await msgPromise;
			return output;
		}

		// Run the function on the main thread if workers aren't supported
		return await processDM(html, config);
	};

	// Return the string parameter by default
	// Opportunity here to make the function more robust or to expand error handling
	return str;
}