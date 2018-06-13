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
	chunk_step = 230000
	interval = 10000    
	user_id = data['user_id']
	client = Wit(wit_token)
	doc = requests.get(link)
	resp = None
	with closing(doc):
		try:
			if(len(doc.content)>300000):
				msg = "Точность при распозновании больших голосовых сообщений не гарантируется. Сообщение распознается по частям. \n\n"
				sound = doc.content
				current_point=interval
				amount = len(sound) // chunk_step
				step = len(sound) // (amount+1)
				for i in range(amount):
					current_part = sound[current_point-interval:current_point+step]
					current_point+=step
					resp = client.speech(current_part, None, {'Content-Type': 'audio/mpeg3'})
					msg = msg + str(resp['_text']) + '\n' + '...' + '\n'
				current_part = sound[current_point-1000:len(sound)]
				resp = client.speech(current_part, None, {'Content-Type': 'audio/mpeg3'})
				msg = msg + str(resp['_text'])
				resp = msg
			else: 
				resp = client.speech(doc.content, None, {'Content-Type': 'audio/mpeg3'})
				resp = "Вот, что получилось распознать:\n\n" + str(resp['_text'])
		except:
			resp = "Не удалось распознать сообщение"
		finally:
			if(len(resp)>3500):
				cnt = 0
				amount_msg = len(sound) // 3500
				for i in range(amount_msg):
					vk.method('messages.send', {'user_id': user_id, 'message': resp[cnt:cnt+3500]})
					cnt = cnt + 3500
				vk.method('messages.send', {'user_id': user_id, 'message': resp[cnt:len(resp)]})
			else:
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
