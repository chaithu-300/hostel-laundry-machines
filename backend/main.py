from fastapi import FastAPI, HTTPException
import functions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)



@app.get("/get_active_runs_by_rollnumber/{roll_number}")
def get_active_runs(roll_number):

    result = functions.get_active_runs_by_rollnumber(roll_number)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No active runs found for this roll number"
        )

    return result   

@app.get("/machines/attention")
def get_attention_machines():
    return functions.get_machines_needing_attention() 

@app.get("/machines/todays_usage_stats/{block}")
def get_todays_usage_stats(block: str):
    if block not in ["a", "b", "c", "d"]:
        raise HTTPException(
            status_code=422, 
            detail="Block must be one of the following: a, b, c, d"
        )
    return functions.get_todays_usage(block)
