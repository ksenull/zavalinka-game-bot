import json
import requests


class ruGPT3APIWrapper:
    URL = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
    beginning_text = 'Веленика - это невысокая земляная насыпь вдоль наружных стен избы,\
    сооружаемая для предохранения постройки от промерзания зимой.\n\
    Завалинка - это вымышленная ягода.\n'

    def generate_definition(self, text):
        send_text = self.beginning_text + text + ' - это '
        payload = {'text': send_text}
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        r = requests.post(self.URL, data=json.dumps(payload), headers=headers)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        response = r.json()['predictions']

        print(response)


if __name__ == '__main__':
    gpt = ruGPT3APIWrapper()
    gpt.generate_definition('Суккуб')
