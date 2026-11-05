from datetime import datetime,timedelta 
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine,func
from sqlalchemy.orm import Session, declarative_base
from fastapi import FastAPI, HTTPException

DB_PATH = "hostel-laundry.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

class machines(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    block = Column(String) #a,b,c,d
    kind = Column(String) #Washer, Dryer
    cycles_minutes = Column(Integer)
    in_service = Column(Integer)

class runs(Base):
    __tablename__ = "runs"
    run_id = Column(Integer, primary_key = True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    roll_no = Column(String)
    started_at = Column(DateTime, default = datetime.now) #YYYY-MM-DD HH:MM
    ends_at = Column(DateTime)
    collected_at = Column(DateTime) #Empty until collected
    status = Column(String) #Running, Completed, Collected

Base.metadata.create_all(engine)
#E8
def get_active_runs_by_rollnumber(roll_number):

    session = Session(engine)
    active_runs = session.query(runs).filter(
        runs.roll_no == roll_number.strip(),
        runs.collected_at == None
    ).all()

    response = []
    for run in active_runs:
        response.append({
            "id": run.run_id,
            "machine_id": run.machine_id,
            "roll_no": run.roll_no,
            "status": run.status,
            "ends_at": run.ends_at
        })
    session.close()
    return response
#E9
def get_machines_needing_attention():
    session = Session(engine)
    Machines = session.query(machines).all()
    response = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    for Machine in Machines:
        Runs = session.query(runs).filter(
            runs.machine_id == Machine.id,
            runs.status == "running"
        ).all()
        if Machine.in_service == 0:
            detail = "Out of order"
        for Run in Runs:
            if current_time > (Run.ends_at + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M"):
                detail = "Waiting for pickup"
        if Machine.in_service == 0:
            temp_Machine = {
                "id": Machine.id,
                "name": Machine.name,
                "block": Machine.block,
                "kind": Machine.kind,
                "detail": detail
            }
            response.append(temp_Machine)
    session.close()
    return response
#E10
def get_todays_usage(block):
    session = Session(engine)
    today_time = datetime.now().strftime("%Y-%m-%d") 
    
    results = session.query(
        machines.kind,
        func.count(runs.run_id)).join(runs, machines.id == runs.machine_id).filter(machines.block == block,runs.started_at.like(f"{today_time}%")
    ).group_by(
        machines.kind
    ).all() 
    washer_count = 0
    dryer_count = 0
    for row in results:
        kind, count = row
        if kind.lower() == "washer":
            washer_count = count
        elif kind.lower() == "dryer":
            dryer_count = count
            
    response = {
        "block": block,
        "washer_runs": washer_count,
        "dryer_runs": dryer_count
    }
    
    session.close()
    return response
    
    
           




            
            

    

    


