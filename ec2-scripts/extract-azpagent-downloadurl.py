import json
import sys

json_data = json.load(sys.stdin)
print json_data['value'][0]['downloadUrl']