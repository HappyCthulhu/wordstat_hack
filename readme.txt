About this script:
I created it for one purpose - boost query statistics on https://wordstat.yandex.ru/. Now he can:
- connect with your privat proxy
- log in to your yandex-email account
- send random number of requests to yandex with random short pause
- send log-info to report.txt and final_report.txt

You must:
- install chromedriver and add it to variable PATH
- create folder 'text_files'. In that folder you must create files: 'emails.yml', 'final_report.txt', 'proxies.yml', 'report.txt', 'requests.yml', 'my_info.yml'
- in 'emails.yml' u can add info about ya.ru accounts: login:pass. Dont forget to add '-' in start of line (because of YAML format)
- in 'proxies.yml' u can add info about privat proxies: login:pass:IP:PORT. Dont forget to add '-' in start of line (because of YAML format
- install requirements from 'requirements.txt'
- in 'my_info.yml' u can add your anti-captcha token in YAML-dictionary format: { token: 94870129356fasjdfh74 }