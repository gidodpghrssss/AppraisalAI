from app.db.session import SessionLocal
from app.models.client import Client
from app.models.property import Property
from app.models.project import Project, ProjectStatus
import datetime

# Create a database session
db = SessionLocal()

# Add a test client if none exists
client_count = db.query(Client).count()
if client_count == 0:
    new_client = Client(
        name='Test Client', 
        email='test@example.com', 
        phone='123-456-7890', 
        address='123 Test St, Testville'
    )
    db.add(new_client)
    db.commit()
    print('Client added successfully!')
else:
    print(f'Using existing client. Total clients: {client_count}')

# Get the first client
client = db.query(Client).first()

# Add a test property
new_property = Property(
    address='456 Test Ave', 
    city='Testville', 
    state='TS', 
    zip_code='12345', 
    property_type='Residential', 
    bedrooms=3, 
    bathrooms=2, 
    square_feet=2000, 
    year_built=2010
)
db.add(new_property)
db.commit()
print('Property added successfully!')

# Add a test project
new_project = Project(
    title='Test Appraisal', 
    description='Test appraisal for a residential property', 
    status=ProjectStatus.IN_PROGRESS, 
    estimated_value=450000, 
    client_id=client.id, 
    property_id=new_property.id, 
    created_at=datetime.datetime.now(), 
    updated_at=datetime.datetime.now()
)
db.add(new_project)
db.commit()
print('Project added successfully!')

# Add a completed project from last month
last_month = datetime.datetime.now() - datetime.timedelta(days=30)
completed_property = Property(
    address='789 Past Lane', 
    city='Oldtown', 
    state='TS', 
    zip_code='54321', 
    property_type='Commercial', 
    bedrooms=0, 
    bathrooms=2, 
    square_feet=5000, 
    year_built=2005
)
db.add(completed_property)
db.commit()

completed_project = Project(
    title='Completed Commercial Appraisal', 
    description='Completed appraisal for a commercial property', 
    status=ProjectStatus.COMPLETED, 
    estimated_value=850000, 
    client_id=client.id, 
    property_id=completed_property.id, 
    created_at=last_month, 
    updated_at=last_month + datetime.timedelta(days=15)
)
db.add(completed_project)
db.commit()
print('Completed project added successfully!')

# Add a pending project
pending_property = Property(
    address='321 Future Blvd', 
    city='Newville', 
    state='TS', 
    zip_code='67890', 
    property_type='Land', 
    bedrooms=0, 
    bathrooms=0, 
    square_feet=10000, 
    year_built=0
)
db.add(pending_property)
db.commit()

pending_project = Project(
    title='Pending Land Appraisal', 
    description='Pending appraisal for an undeveloped land', 
    status=ProjectStatus.DRAFT, 
    estimated_value=250000, 
    client_id=client.id, 
    property_id=pending_property.id, 
    created_at=datetime.datetime.now() - datetime.timedelta(days=5), 
    updated_at=datetime.datetime.now() - datetime.timedelta(days=5)
)
db.add(pending_project)
db.commit()
print('Pending project added successfully!')

print('All test data added successfully!')
