import time
import os
import json
import subprocess
import urllib.request
import vk_api
import requests
from wit import Wit
from contextlib import closing

token = str(os.environ["TOKEN"])
wit_token = str(os.environ["WIT_TOKEN"])
vk = vk_api.VkApi(token = token, api_version='5.73') # Токен Vk Api
values = {'out' : 0, 'count' : 100, 'time_offset' : 60} # Данные для обновления информации о входящих сообщениях



def recognize_voice(data, link, token, wit_token):
    user_id = data['user_id']
    client = Wit(wit_token)
    doc = requests.get(link)
    resp = None
    with closing(doc):
        try:
            resp = client.speech(doc.content, None, {'Content-Type': 'audio/mpeg3'})
            resp = str(resp['_text'])
        except:
            resp = "Не удалось распознать сообщение"
        finally:
            vk.method('messages.send', {'user_id': user_id, 'message': resp})
    return


def main():
	while True: # Бесконечный цикл
		time.sleep(1) # Задержка
		response = vk.method('messages.get', values) # Получаем список сообщений
        # Смотрим, какием сообщения новые
		if response['items']:
			values['last_message_id'] = response['items'][0]['id']
        #Отвечаем
		for item in response['items']:
			data = item
			for data in response["items"]:
				if(data.get('attachments',"")!=""):
					a = data['attachments']
					if a[0]['type'] == 'doc':
						if a[0]['doc']['type'] == 5:
							recognize_voice(item, a[0]['doc']['preview']['audio_msg']['link_mp3'], token, wit_token)
                
			cycle=0
			while(cycle!=1):
				if(data.get('fwd_messages',"")!=""):
					data = data.get('fwd_messages')
					if(len(data)>1):
						cycle = 1
						for i in range(len(data)):
							data[i] = dict(data[i])
							data_i = data[i]
							if(data_i.get('attachments',"")!=""):
								a = data_i['attachments']
								if a[0]['type'] == 'doc':
									if a[0]['doc']['type'] == 5:
										recognize_voice(item, a[0]['doc']['preview']['audio_msg']['link_mp3'], token, wit_token)
							
					elif(len(data)==1):
						data = dict(data[0])
						if(data.get('attachments',"")!=""):
							cycle = 1
							a = data['attachments']
							if a[0]['type'] == 'doc':
								if a[0]['doc']['type'] == 5:
									recognize_voice(item, a[0]['doc']['preview']['audio_msg']['link_mp3'], token, wit_token)
				else:
					cycle = 1
    			
						
if __name__ == '__main__':
    main()
