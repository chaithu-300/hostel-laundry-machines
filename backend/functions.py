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

def add_machines(name, block, kind, cycles_minutes, in_service):
    session = Session(engine)
    new_machine = machines(
        name = name,
        block = block,
        kind = kind,
        cycles_minutes = cycles_minutes,
        in_service = in_service
    )
    session.add(new_machine)
    session.commit()

    response = {
        "id": new_machine.id,
        "name": new_machine.name,
        "block": new_machine.block,
        "kind": new_machine.kind,
        "cycles_minutes": new_machine.cycles_minutes,
        "in_service": new_machine.in_service
    }
    session.close()
    return response

def get_machines_by_id(machine_id):
    session = Session(engine)
    machine = session.get(machines, machine_id)
    if machine is None:
        raise HTTPException(status_code = 404, detail = "Can't find machine with the given ID")
    response = {
        "id": machine.id,
        "name": machine.name,
        "block": machine.block,
        "kind": machine.kind,
        "cycles_minutes": machine.cycles_minutes,
        "in_service": machine.in_service
    }
    session.close()
    return response

def get_machines(block = False, kind = False):
    session = Session(engine)
    Machines = session.query(machines).all()
    response = []
    for Machine in Machines:
        temp_Machine = {
            "id": Machine.id,
            "name": Machine.name,
            "block": Machine.block,
            "kind": Machine.kind,
            "cycles_minutes": Machine.cycles_minutes,
            "in_service": Machine.in_service
        }
        response.append(temp_Machine)
    session.close()
    return response

def update_machines(in_service, machine_id):
    session = Session(engine)
    machine = session.query(machines).filter(machines.id == machine_id)
    if machine is None:
        raise HTTPException(status_code = 404, detail = "Can't find machine with the given ID")
    machine.in_service = in_service
    session.commit()
    response = {
        "Machine status updated successfully"
    }
    session.close()
    return response 

def get_Active_Runs_By_RollNumber(roll_no, status = "Running"):
    session = Session(engine)
    run = session.get(runs, roll_no)
    if run is None:
        raise HTTPException(status_code = 404, detail = "Can't find any active runs for the given roll number")
    response = {
        "run_id": run.run_id,
        "machine_id": run.machine_id,
        "roll_no": run.roll_no,
        "started_at": run.started_at,
        "ends_at": run.ends_at,
        "collected_at": run.collected_at,
        "status": run.status
    }
    session.close()
    return response 

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


    
    
           




            
            

    

    


