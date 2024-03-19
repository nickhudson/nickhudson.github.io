import os

#TODO WE COULD PROBABLY MAKE THIS INTO A CLASS
# Config & User settings
config = {
        'darkMode': {
            'autoDarkMode': True,
            'forceLightMode': False,
            'logoSwap': False,
            'assets': {
                'metaTag': '<meta name="color-scheme" content="light dark">',
                'dmCss': './file-assets/css/dark-mode.css',
                'dmLogoSwap': './file-assets/html/dm-logo-swap.html',
                'error': './error.html'
            },
            'regex': {
                'code': r'\$\[code]',
                'dmCssColor1': r'\$\[color_1]',
                'dmCssColor2': r'\$\[color_2]',
                'msoCond': r'(<{1}!-*)+\[(end|if)+.*>',
                'styleClose': r'\s(?=(<\/style\s*>(?!\s*<{1}!\[endif\])))',
                'tagOpen': r'<{1}\w+\b',
                'classAttr': r'class="[\w\s-]*"',
                'bgColor': r'(bgcolor|background(-color)?)([=:]"{0,1}\s*#[\w\s]*[";])',
                'hexValue': r'#[a-z0-9]{0,6}',
                'headTag': r'<{1}head.*>',
                'metaTag': r'<{1}meta.*name=".*color-scheme.*".*>',
                'bodyTag': r'<{1}body([\s\S](?!>))*"*>',
                'tableFull': r'<{1}table.*width="100%".*>',
                'tableMain': r'<{1}table.*(width="|style=".*width:\s*)(6[0-9][0-9]|700)("|px).*>',
                'tableTdBg': r'<{1}(table|td).*(bgcolor|background|style=".*background(-color)?.*").*>',
                'logo': r'<{1}tr>\s*<{1}td.*>\s*.*<{1}img.*src=".*logo([^s\/])*"\s*.*>([\s\S](?!<{1}tr>))*<\/td>\s*<\/tr>',
                'buttons': r'<{1}(table|td|a)([\s\S](?!>))*(height="\b([3][0-9]|[4][0-8])"|style=".*border-radius.*")\s*.*>(?=([\s\S](?!<\/td|table>))*<\/a>)'
            }
        },
        'filePath': {
            'files': './file-assets/files/',
            'local': {
                'tests': f'file://{os.getcwd()}/../../file-assets/tests/',
                'test_dir': f'{os.getcwd()}/../../file-assets/tests/',
                'stouts': f'./stouts/',
                'files': f'../../file-assets/files/',
                'images': f'../../file-assets/images/',
                'backgrounds': f'../../file-assets/images/backgrounds/'
            },
         },
        'fileName': {
            'coords': '_coords.json',
            'colors': 'colors.json',
        },
        'folderName': {
            'backgrounds': 'backgrounds'
        }
    }

def get_config():
    return config

#TODO Need to be more robust
def set_config(key, val):
    config[key] = val