# Diagbot
Diagnosis Chatbot made with Dialogflow and Python

## Installing
1. ensure you have python3.6 installed
2. Unzip file DiagBot.zip or clone this repository
3. Open your terminal or command prompt
4. In terminal, 'cd' (change directory) into DiagBot folder
5  run 'pip install -r requirements.txt'

## Run Package
### PyCharm
1. Change directory into DiagBot folder
2. Open PyCharm
3. Click File > Open, navigate to DiagBot folder
4. Click Run > Edit Configurations > Add new configuration (+) > Python > Script path: TLGM.py > (optional: rename to server) > apply
5. Click Run > Edit Configurations > Add new configuration (+) > Python > Script path: main.py > (optional: rename to main) > apply

### Tunelling
1. In command prompt, 'cd' (change directory) into DiagBot folder
2. run './ngrok http 5050'
3. Copy Forwarding URL
4. (in dialogflow) Click Fulfillment > insert URL in 3. into URL* field
