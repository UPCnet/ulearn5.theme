# 1- Requiere que le lleguen los datos del EVA mediante una llamada a webservice

payload = {"wstoken": 'dd767d33520a27a30d15a96415655b1b',
           "wsfunction": 'local_blanquerna_get_pending_tasks',
           "moodlewsrestformat": 'json',
           "username": userid.lower(),
           }

req = requests.post("http://eva.blanquerna.edu/webservice/rest/server.php",
                    data=payload,
                    verify=False)
