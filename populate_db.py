"""
Script to populate the Apeko database with real data.
"""
import sqlite3
import json
import datetime
import random
from hashlib import sha256

# Connect to the database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Clear existing data
tables = [
    'clients', 'properties', 'projects', 'rag_documents', 
    'rag_document_chunks', 'property_images', 'reports'
]

for table in tables:
    cursor.execute(f"DELETE FROM {table}")

# Add admin user if not exists
cursor.execute("SELECT id FROM users WHERE email = 'admin@apeko.com'")
if not cursor.fetchone():
    hashed_password = sha256('apeko2025'.encode()).hexdigest()
    cursor.execute("""
    INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('admin@apeko.com', hashed_password, 'Admin User', 'admin', 1, datetime.datetime.now(), datetime.datetime.now()))

# Add clients
clients = [
    ('John Smith', 'john.smith@example.com', '555-123-4567', 'Smith Properties LLC', '123 Business Ave, New York, NY', 'Regular client since 2023'),
    ('Emily Johnson', 'emily.johnson@example.com', '555-234-5678', 'Johnson Real Estate', '456 Market St, Los Angeles, CA', 'Prefers email communication'),
    ('Michael Brown', 'michael.brown@example.com', '555-345-6789', 'Brown Investments', '789 Finance Blvd, Chicago, IL', 'Looking for commercial properties'),
    ('Sarah Davis', 'sarah.davis@example.com', '555-456-7890', 'Davis Holdings', '101 Corporate Dr, Houston, TX', 'Interested in residential developments'),
    ('Robert Wilson', 'robert.wilson@example.com', '555-567-8901', 'Wilson Group', '202 Enterprise Way, Miami, FL', 'Focus on luxury properties'),
    ('Jennifer Martinez', 'jennifer.martinez@example.com', '555-678-9012', 'Martinez Realty', '303 Realty Row, Phoenix, AZ', 'Specializes in multi-family units'),
    ('David Thompson', 'david.thompson@example.com', '555-789-0123', 'Thompson Investments', '404 Investor St, Philadelphia, PA', 'Looking for long-term investments'),
    ('Lisa Garcia', 'lisa.garcia@example.com', '555-890-1234', 'Garcia Properties', '505 Development Ave, San Antonio, TX', 'New client, first project'),
    ('James Rodriguez', 'james.rodriguez@example.com', '555-901-2345', 'Rodriguez & Associates', '606 Partners Ln, San Diego, CA', 'Works with multiple investors'),
    ('Patricia Lee', 'patricia.lee@example.com', '555-012-3456', 'Lee Enterprises', '707 Enterprise Blvd, Dallas, TX', 'Expanding portfolio in 2025')
]

for client in clients:
    cursor.execute("""
    INSERT INTO clients (name, email, phone, company, address, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (*client, datetime.datetime.now(), datetime.datetime.now()))

# Add properties
properties = [
    ('123 Main St', 'New York', 'NY', '10001', 'residential', 2200, 0.25, 1998, 3, 2.5, 'Modern townhouse with garden', 
     json.dumps({'garage': True, 'pool': False, 'fireplace': True}), 40.7128, -74.0060),
    ('456 Oak Ave', 'Los Angeles', 'CA', '90001', 'residential', 3100, 0.5, 2005, 4, 3.0, 'Spacious family home in quiet neighborhood', 
     json.dumps({'garage': True, 'pool': True, 'fireplace': False}), 34.0522, -118.2437),
    ('789 Pine Rd', 'Chicago', 'IL', '60007', 'residential', 1800, 0.15, 1985, 2, 1.5, 'Cozy bungalow with recent renovations', 
     json.dumps({'garage': False, 'pool': False, 'fireplace': True}), 41.8781, -87.6298),
    ('101 Market St', 'San Francisco', 'CA', '94103', 'commercial', 5000, 0.1, 1978, None, None, 'Downtown retail space with high foot traffic', 
     json.dumps({'loading_dock': True, 'security_system': True, 'elevator': True}), 37.7749, -122.4194),
    ('202 Commerce Blvd', 'Houston', 'TX', '77002', 'commercial', 12000, 0.75, 2010, None, None, 'Modern office building with parking garage', 
     json.dumps({'parking': 50, 'conference_rooms': 5, 'cafeteria': True}), 29.7604, -95.3698),
    ('303 Industrial Way', 'Phoenix', 'AZ', '85001', 'industrial', 25000, 2.5, 2000, None, None, 'Warehouse with loading docks and office space', 
     json.dumps({'loading_docks': 4, 'ceiling_height': 24, 'office_space': 2500}), 33.4484, -112.0740),
    ('404 Condo Ln #301', 'Miami', 'FL', '33101', 'residential', 1200, None, 2015, 2, 2.0, 'Luxury condo with ocean view', 
     json.dumps({'balcony': True, 'gym': True, 'doorman': True}), 25.7617, -80.1918),
    ('505 Apartment Blvd #202', 'Seattle', 'WA', '98101', 'residential', 950, None, 2018, 1, 1.0, 'Modern apartment in downtown', 
     json.dumps({'washer_dryer': True, 'pet_friendly': True, 'rooftop': True}), 47.6062, -122.3321),
    ('606 Ranch Rd', 'Austin', 'TX', '78701', 'residential', 3500, 5.0, 1995, 4, 3.5, 'Ranch style home on large lot', 
     json.dumps({'barn': True, 'pond': True, 'guest_house': True}), 30.2672, -97.7431),
    ('707 Mall Way', 'Denver', 'CO', '80201', 'commercial', 15000, 1.0, 1990, None, None, 'Retail space in popular shopping center', 
     json.dumps({'foot_traffic': 'high', 'parking': 200, 'loading_area': True}), 39.7392, -104.9903),
    ('808 Office Park', 'Atlanta', 'GA', '30301', 'commercial', 8000, 0.5, 2008, None, None, 'Office space in business district', 
     json.dumps({'conference_rooms': 3, 'break_room': True, 'security': True}), 33.7490, -84.3880),
    ('909 Luxury Dr', 'Las Vegas', 'NV', '89101', 'residential', 4500, 0.3, 2020, 5, 4.5, 'Luxury home with pool and spa', 
     json.dumps({'pool': True, 'spa': True, 'home_theater': True}), 36.1699, -115.1398)
]

for prop in properties:
    cursor.execute("""
    INSERT INTO properties (address, city, state, zip_code, property_type, square_feet, lot_size, year_built, 
                          bedrooms, bathrooms, description, features, latitude, longitude, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (*prop, datetime.datetime.now(), datetime.datetime.now()))

# Add projects
statuses = ['pending', 'in_progress', 'completed', 'cancelled']
project_titles = [
    'Residential Appraisal', 'Commercial Valuation', 'Market Analysis', 
    'Investment Property Assessment', 'Pre-Purchase Appraisal', 
    'Refinance Appraisal', 'Estate Valuation', 'Tax Assessment Appeal', 
    'Divorce Settlement Appraisal', 'Insurance Valuation'
]

# Get client and property IDs
cursor.execute("SELECT id FROM clients")
client_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM properties")
property_ids = [row[0] for row in cursor.fetchall()]

# Create 20 projects
for i in range(1, 21):
    title = random.choice(project_titles)
    description = f"Project {i}: {title} - Detailed assessment required"
    status = random.choice(statuses)
    client_id = random.choice(client_ids)
    property_id = random.choice(property_ids)
    assigned_to = 1  # Admin user
    estimated_value = random.uniform(100000, 2000000)
    created_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 90))
    updated_date = created_date + datetime.timedelta(days=random.randint(1, 30))
    
    cursor.execute("""
    INSERT INTO projects (title, description, status, client_id, property_id, assigned_to, 
                        estimated_value, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, status, client_id, property_id, assigned_to, 
          estimated_value, created_date, updated_date))

# Add RAG documents
rag_documents = [
    ('USPAP 2025 Guidelines', 'The Uniform Standards of Professional Appraisal Practice (USPAP) are the generally recognized ethical and performance standards for the appraisal profession in the United States. USPAP was adopted by Congress in 1989, and contains standards for all types of appraisal services, including real estate, personal property, business and mass appraisal. Compliance is required for state-licensed and state-certified appraisers involved in federally-related real estate transactions. USPAP is updated every two years so that appraisers have the information they need to deliver unbiased and thoughtful opinions of value. The 2025 edition includes significant updates to reporting requirements and ethics provisions.', 'USPAP', 'regulation'),
    ('Residential Appraisal Best Practices', 'This document outlines the best practices for residential property appraisals. It covers inspection protocols, comparable selection criteria, adjustment methodologies, and reporting standards. Appraisers should conduct thorough inspections of all accessible areas of the subject property, measure the gross living area according to ANSI standards, and photograph all relevant features. Comparable selection should prioritize recent sales within the same neighborhood with similar physical characteristics. Adjustments should be market-derived and supported by paired sales analysis when possible. Reports should be clear, concise, and comply with all USPAP requirements.', 'Apeko Internal', 'appraisal_report'),
    ('Commercial Property Valuation Methods', 'This guide covers the three primary approaches to commercial property valuation: the Income Approach, Sales Comparison Approach, and Cost Approach. The Income Approach is typically given the most weight for income-producing properties and involves capitalizing the property\'s net operating income or discounting future cash flows. The Sales Comparison Approach uses recent sales of similar properties with adjustments for differences. The Cost Approach estimates the cost to replace the building plus land value minus depreciation. Reconciliation of these approaches should consider the property type, available data, and intended use of the appraisal.', 'Apeko Internal', 'appraisal_report'),
    ('Q1 2025 Market Analysis: Residential Sector', 'The residential real estate market in Q1 2025 showed strong growth with a 5.2% increase in median home prices nationwide. Housing inventory remains low at 3.2 months of supply, continuing to favor sellers in most markets. Mortgage rates have stabilized around 5.8% for 30-year fixed loans. Regional variations show the Southeast and Mountain West experiencing the strongest price appreciation, while the Northeast has seen more modest gains. New construction has increased by 8.3% year-over-year, but remains insufficient to meet demand in most metropolitan areas. The luxury market has shown signs of cooling with longer days on market for properties priced above $2 million.', 'Apeko Research', 'market_analysis'),
    ('Q1 2025 Market Analysis: Commercial Sector', 'The commercial real estate market in Q1 2025 continues to recover unevenly across sectors. Office vacancy rates remain elevated at 15.7% nationwide, with central business districts still struggling with remote work trends. Suburban office parks are showing better performance with 12.3% vacancy rates. The industrial sector remains robust with 3.5% vacancy rates and 7.2% year-over-year rent growth, driven by e-commerce and reshoring of manufacturing. Retail is showing signs of stabilization with vacancy rates declining to 6.8%, though regional malls continue to face challenges. Multi-family cap rates have increased slightly to 5.1% as interest rates have risen, but demand remains strong in growing metropolitan areas.', 'Apeko Research', 'market_analysis'),
    ('Property Tax Assessment Guidelines 2025', 'This document outlines the current guidelines for property tax assessments across major jurisdictions. Assessment ratios vary by state, ranging from 100% of market value to as low as 10% in some areas. Appeal deadlines typically fall 30-60 days after assessment notices are issued. Successful appeals generally require evidence of comparable sales, errors in property characteristics, or unequal assessment compared to similar properties. Many jurisdictions offer exemptions for primary residences, seniors, veterans, and agricultural use. Recent court decisions have emphasized the importance of uniformity in assessment practices and the need for transparency in valuation methodologies.', 'Tax Authorities Compilation', 'regulation'),
    ('Environmental Factors in Property Valuation', 'This report examines how environmental factors impact property values and appraisal practices. Flood zone designations can reduce property values by 5-15% depending on severity and insurance requirements. Proximity to environmental hazards such as contaminated sites can impact values by 10-30% depending on remediation status. Positive environmental factors like parks and water views can increase values by 5-25%. Climate change considerations are increasingly important, with properties in areas prone to sea level rise, wildfires, or extreme weather events facing potential long-term value impacts. Appraisers should document environmental conditions, research local regulations, and analyze market reactions to these factors.', 'Environmental Research Institute', 'property_data'),
    ('Appraisal Review Standards', 'This document establishes standards for appraisal review processes. Reviews should evaluate compliance with USPAP, client requirements, and assignment conditions. Technical reviews assess the adequacy of data, appropriateness of comparable selections, validity of adjustments, and soundness of conclusions. Administrative reviews confirm that reports contain required elements and meet formatting standards. Reviewers should maintain independence and objectivity, documenting their own scope of work and conclusions. When significant issues are identified, reviewers should provide specific references to applicable standards and clear explanations of deficiencies. The review process should be constructive and focused on maintaining quality and consistency.', 'Apeko Quality Control', 'other')
]

for doc in rag_documents:
    cursor.execute("""
    INSERT INTO rag_documents (title, content, source, document_type, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (*doc, datetime.datetime.now(), datetime.datetime.now()))
    
    # Get the document ID
    doc_id = cursor.lastrowid
    
    # Create chunks for the document (simplified)
    content = doc[1]
    chunk_size = 500
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for i, chunk_content in enumerate(chunks):
        # Mock embedding as a JSON array of 1536 dimensions with random values
        embedding = json.dumps([random.uniform(-1, 1) for _ in range(10)])  # Using 10 dims instead of 1536 for simplicity
        
        cursor.execute("""
        INSERT INTO rag_document_chunks (document_id, chunk_index, content, embedding, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, i, chunk_content, embedding, datetime.datetime.now(), datetime.datetime.now()))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database populated with real data successfully!")
