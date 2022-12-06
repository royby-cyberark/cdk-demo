import json
from typing import Dict


def get_response(code: int, message: str) -> Dict:
    return {
        'statusCode': code,
        'body': json.dumps(message)
    }
