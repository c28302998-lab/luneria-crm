import re

with open("backend/app/api/shift_reports.py", "r") as f:
    content = f.read()

if "Notification" not in content:
    content = content.replace("from app.models.models import", "from app.models.models import Notification,")

old_code = """    except Exception as e:
        print(f"Failed to schedule shift date update: {e}")
        
    return new_report"""

new_code = """    except Exception as e:
        print(f"Failed to schedule shift date update: {e}")
        
    # Send notification to Admin
    from app.models.models import Candidate, Worker
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if candidate:
        worker_record = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
        if worker_record and worker_record.admin_id:
            notif = Notification(
                user_id=worker_record.admin_id,
                type="Новый отчет",
                message=f"Работник {candidate.first_name} сдал отчет на сумму ${report_in.amount}."
            )
            db.add(notif)
            db.commit()
            
    return new_report"""

content = content.replace(old_code, new_code)

with open("backend/app/api/shift_reports.py", "w") as f:
    f.write(content)
