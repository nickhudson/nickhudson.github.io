const styleRegex = /(<\/*style.*>)/g;
const logoCommentRegex = /(<!.*logo.*>)/g;
const logoTD = /<td.*>\s*.*<img.*src=".*logo([^s\/])*"\s*.*>\s*<\/td>/g;
const logoTD2 = /<{1}tr>\s*<{1}td.*>\s*.*<{1}img.*src=".*logo([^s\/])*"\s*.*>\s*<\/td>\s*<\/tr>/;
const bgRegex = /bgcolor="[#\w\s]*"|background="[#\w\s]*"|background-color:[#\w\s]*;|background:[#\w\s]*;/
const btnsRegex = /<{1}(table|td|a)([\s\S](?!>))*(height="\b([3][0-9]|[4][0-8])"|style=".*border-radius.*")\s*.*>/


insertCss = () => {
	if (!html.length) html.push(str);

	const htmlSplit = html.pop().split(styleRegex);

	htmlSplit.splice(
		htmlSplit.findIndex((val) =>
			val.match(styleRegex)
		) + 1,
		0,
		`\n${css}\n`
	)

	html.push(htmlSplit.join(''))
}