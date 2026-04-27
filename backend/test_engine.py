import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.email_engine import email_engine

text = """
Verify your bank account immediately or face permanent suspension: http://google.com
"""

try:
    res = email_engine.process_email(text)
    print("SUCCESS!")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()
