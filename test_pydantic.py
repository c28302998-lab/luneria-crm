from pydantic import BaseModel

class Test(BaseModel):
    proof_url: str = None

try:
    Test.model_validate({"proof_url": None})
    print("SUCCESS")
except Exception as e:
    print(e)
