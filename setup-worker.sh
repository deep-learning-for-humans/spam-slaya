pip install -r requirements.txt
wget http://ollama:11434/api/pull --post-data '{  "name": "qwen2.5:3b-instruct-q4_0"}'
python worker.py