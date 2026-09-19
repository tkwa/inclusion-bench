"""Infrastructure smoke fixture, not an AI model or a scored evaluation."""
import json
import sys
json.load(sys.stdin)
print(json.dumps({'status':'unsolved','claims':[],'artifacts':[]}))
