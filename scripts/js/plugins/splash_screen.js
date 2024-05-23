// import { hooks } from 'https://pyscript.net/releases/2024.2.1/core.js';

const splash = document.getElementById('splash'),
			duration = 450,
			splashCL = splash.classList,
			closeClass = 'closed';

addEventListener(
	'py:ready', 
	function ssDisplay() {
		splashCL.add(closeClass);

		setTimeout(() => {
			if (splashCL.contains(closeClass)) {
				splash.close();
				splash.remove();
			}

			removeEventListener(
				'py:ready',
				ssDisplay
			)
		}, duration)
	}
);

splash.style.animationDuration = `${duration}ms`;
splash.style.setProperty('--trans-dur', `${duration}ms`);
splash.showModal();