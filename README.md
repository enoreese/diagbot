# Diagbot
Diagnosis Chatbot made with Dialogflow and Python

## Installing
1. ensure you have python3.6 installed
2. Unzip file DiagBot.zip or clone this repository
3. Open your terminal or command prompt
4. In terminal, 'cd' (change directory) into DiagBot folder
5  run 'pip install -r requirements.txt'

## Dialogflow Setup
1. Create an account on Dialogflow
2. Create a new Dialogflow agent
3. Restore the dialogflow-agent.zip ZIP file in the root of this repo
4. Go to your agent's settings and then the Export and Import tab
5  Click the Restore from ZIP button
6. Select the dialogflow-agent.zip ZIP file in the root of this repo
7  Type RESTORE and and click the Restore button

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
