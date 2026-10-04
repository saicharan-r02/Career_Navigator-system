import os
from datetime import datetime
from typing import Dict,Any,List,Optional

from sqlalchemy import create_engine,Column,Integer,Float,String,Boolean,DateTime,JSON,ForeignKey,func
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,scoped_session

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR,"career_navigator.db")
DATABASE_URI=f"sqlite:///{DB_PATH}"

engine=create_engine(DATABASE_URI,connect_args={"check_same_thread": False})
SessionLocal=scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
Base=declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), default="Student")
    email = Column(String(120), unique=True, index=True, nullable=False)
    branch = Column(String(50), default="CSE")
    academic_year = Column(String(20), default="3rd Year")
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship("CareerAssessment", back_populates="student", cascade="all, delete-orphan")


class CareerAssessment(Base):
    __tablename__ = "career_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    predicted_role = Column(String(100), nullable=False)
    pillar_stats = Column(JSON, default=dict)
    grades_snapshot = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="assessments")
    milestones = relationship("RoadmapMilestone", back_populates="assessment", cascade="all, delete-orphan")


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("career_assessments.id"), nullable=False)
    phase_index = Column(Integer, nullable=False)
    phase_title = Column(String(150), nullable=False)
    milestone_content = Column(String(500), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    assessment = relationship("CareerAssessment", back_populates="milestones")


def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"[OK] Career Navigator database initialized at: {DB_PATH}")


def save_student_assessment(
    email: str,
    full_name: str,
    branch: str,
    academic_year: str,
    grades: Dict[str, Any],
    predicted_role: str,
    pillar_stats: Dict[str, float],
    roadmap: List[str]
) -> int:
    """Saves student profile, academic assessment, and seeds interactive roadmap tasks."""
    session = SessionLocal()
    try:
        student = session.query(Student).filter(Student.email == email).first()
        if not student:
            student = Student(
                full_name=full_name or "Student",
                email=email,
                branch=branch or "Engineering",
                academic_year=academic_year or "3rd Year"
            )
            session.add(student)
            session.flush()
        else:
            if branch:
                student.branch = branch
            if academic_year:
                student.academic_year = academic_year

        assessment = CareerAssessment(
            student_id=student.id,
            predicted_role=predicted_role,
            pillar_stats=pillar_stats,
            grades_snapshot=grades
        )
        session.add(assessment)
        session.flush()

        for idx, phase_text in enumerate(roadmap):
            lines = phase_text.strip().split("\n")
            title = lines[0] if lines else f"Phase {idx}"
            content = "\n".join(lines[1:]) if len(lines) > 1 else phase_text
            milestone = RoadmapMilestone(
                assessment_id=assessment.id,
                phase_index=idx,
                phase_title=title,
                milestone_content=content,
                is_completed=False
            )
            session.add(milestone)

        session.commit()
        return assessment.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_student_profile_and_history(email: str) -> Optional[Dict[str, Any]]:
    session = SessionLocal()
    try:
        student = session.query(Student).filter(Student.email == email).first()
        if not student:
            return None

        history = []
        for a in sorted(student.assessments, key=lambda x: x.created_at, reverse=True):
            milestones = [
                {
                    "milestone_id": m.id,
                    "phase_index": m.phase_index,
                    "phase_title": m.phase_title,
                    "content": m.milestone_content,
                    "is_completed": m.is_completed,
                    "completed_at": m.completed_at.strftime("%Y-%m-%d %H:%M:%S") if m.completed_at else None
                }
                for m in sorted(a.milestones, key=lambda x: x.phase_index)
            ]
            history.append({
                "assessment_id": a.id,
                "predicted_role": a.predicted_role,
                "pillar_stats": a.pillar_stats,
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
                "milestones": milestones,
                "completed_count": sum(1 for m in milestones if m["is_completed"]),
                "total_milestones": len(milestones)
            })

        return {
            "student_id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "branch": student.branch,
            "academic_year": student.academic_year,
            "assessments": history
        }
    finally:
        session.close()


def toggle_roadmap_milestone(milestone_id: int, is_completed: bool) -> bool:
    session = SessionLocal()
    try:
        milestone = session.query(RoadmapMilestone).filter(RoadmapMilestone.id == milestone_id).first()
        if not milestone:
            return False

        milestone.is_completed = is_completed
        milestone.completed_at = datetime.utcnow() if is_completed else None
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_platform_analytics() -> Dict[str, Any]:
    """Generates aggregate career trend statistics across all student assessments."""
    session = SessionLocal()
    try:
        total_students = session.query(func.count(Student.id)).scalar() or 0
        total_assessments = session.query(func.count(CareerAssessment.id)).scalar() or 0

        role_counts = (
            session.query(CareerAssessment.predicted_role, func.count(CareerAssessment.id))
            .group_by(CareerAssessment.predicted_role)
            .all()
        )
        role_dist = {r[0]: r[1] for r in role_counts}

        branch_counts = (
            session.query(Student.branch, func.count(Student.id))
            .group_by(Student.branch)
            .all()
        )
        branch_dist = {b[0]: b[1] for b in branch_counts}

        total_tasks = session.query(func.count(RoadmapMilestone.id)).scalar() or 0
        completed_tasks = (
            session.query(func.count(RoadmapMilestone.id))
            .filter(RoadmapMilestone.is_completed == True)
            .scalar() or 0
        )

        return {
            "total_students": total_students,
            "total_assessments": total_assessments,
            "role_distribution": role_dist,
            "branch_distribution": branch_dist,
            "task_completion": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate_pct": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
            }
        }
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
