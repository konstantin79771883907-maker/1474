from sqlmodel import SQLModel, create_engine, Session, select
from sqlmodel.pool import StaticPool
from app.models.db import User, Category, Ticket, Comment, Role

engine = create_engine(
    "sqlite:///school_crm.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize database with sample data"""
    with Session(engine) as session:
        # Check if already initialized
        if session.exec(select(User)).first():
            return
        
        # Create admin user
        admin = User(name="Admin", email="admin@school.edu", role=Role.ADMIN)
        session.add(admin)
        
        # Create support user
        support = User(name="Support Team", email="support@school.edu", role=Role.SUPPORT)
        session.add(support)
        
        # Create sample user
        user = User(name="John Teacher", email="teacher@school.edu", role=Role.USER)
        session.add(user)
        
        # Create categories
        tech_category = Category(name="Technical Issues", description="Computer, network, software problems")
        session.add(tech_category)
        
        facility_category = Category(name="Facilities", description="Building, room, equipment issues")
        session.add(facility_category)
        
        academic_category = Category(name="Academic Support", description="Curriculum, grading, student issues")
        session.add(academic_category)
        
        session.commit()
        session.refresh(admin)
        session.refresh(support)
        session.refresh(user)
        session.refresh(tech_category)
        session.refresh(facility_category)
        session.refresh(academic_category)
        
        # Create sample ticket
        ticket = Ticket(
            title="Projector not working in Room 101",
            description="The projector in Room 101 is not turning on. Tried different cables but no luck.",
            priority="high",
            status="open",
            author_id=user.id,
            category_id=tech_category.id
        )
        session.add(ticket)
        session.commit()
        
        print("Database initialized with sample data!")
