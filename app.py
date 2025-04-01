from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://maria:password@localhost/myflaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  

# Association for many-to-many relationship between Artist and Group
artist_group_association = db.Table(
    'artist_group',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

# Festival Model (One-to-Many relationship with Location)
class Festival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    poster = db.Column(db.String(255))  # Link to the festival poster image
    description = db.Column(db.Text)
    
    # Foreign Key linking to Location
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    
    # Relationships
    location = db.relationship('Location', back_populates='festivals')
    events = db.relationship('Event', back_populates='festival', lazy=True)
    performances = db.relationship('Performance', back_populates='festival', lazy=True)
    tickets = db.relationship('Ticket', back_populates='festival', lazy=True)

    def __repr__(self):
        return f'<Festival {self.name}>'

# Location Model (One-to-Many relationship with Festival)
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    coordinates = db.Column(db.String(100))  # Store coordinates as string (latitude, longitude)
    town = db.Column(db.String(100))
    country = db.Column(db.String(100))
    continent = db.Column(db.String(100))
    
    # Relationship to Festivals
    festivals = db.relationship('Festival', back_populates='location', lazy=True)

    def __repr__(self):
        return f'<Location {self.town}, {self.country}>'
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)  # Start time of the event
    end_time = db.Column(db.Time, nullable=False)    # End time of the event
    building = db.Column(db.String(100))            # Building or stage name
    duration = db.Column(db.Integer)                # Maximum duration in hours (e.g., 12)

    # Foreign Keys
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'), nullable=False)
    
    # Relationships
    festival = db.relationship('Festival', back_populates='events')
    staff = db.relationship('Staff', back_populates='event', lazy=True)
    tickets = db.relationship('Ticket', back_populates='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.date} at {self.building}>'

class BuildingStage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    max_capacity = db.Column(db.Integer)
    image = db.Column(db.String(255))

    # Relationships
    technical_equipment = db.relationship('TechnicalEquipmentAssignment', back_populates='building_stage')
    staff = db.relationship('StaffAssignment', back_populates='building_stage')
    performances = db.relationship('Performance', back_populates='building_stage')

    def __repr__(self):
        return f'<BuildingStage {self.name}>'
    
class TechnicalEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # E.g., "Speakers", "Lights"
    description = db.Column(db.Text)                  # Description
    image = db.Column(db.String(255))                # Image (link to image file)

    # Relationships
    building_stages = db.relationship('TechnicalEquipmentAssignment', back_populates='technical_equipment')

    def __repr__(self):
        return f'<TechnicalEquipment {self.name}>'

class TechnicalEquipmentAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of equipment in this building/stage

    # Foreign Keys
    building_stage_id = db.Column(db.Integer, db.ForeignKey('building_stage.id'), nullable=False)
    technical_equipment_id = db.Column(db.Integer, db.ForeignKey('technical_equipment.id'), nullable=False)

    # Relationships
    building_stage = db.relationship('BuildingStage', back_populates='technical_equipment')
    technical_equipment = db.relationship('TechnicalEquipment', back_populates='building_stages')

    def __repr__(self):
        return f'<TechnicalEquipmentAssignment {self.technical_equipment.name} x {self.quantity}>'
    
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Could be dropdown with choices
    role = db.Column(db.String(100), nullable=False)     # E.g., "Manager", "Technician", "Volunteer"
    experience_level = db.Column(db.String(100), nullable=False) # Scale from beginner to expert
    
    # Foreign Keys
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    # Relationships
    event = db.relationship('Event', back_populates='staff')
    building_stages = db.relationship('StaffAssignment', back_populates='staff')
    performances = db.relationship('Performance', back_populates='staff')

    def __repr__(self):
        return f'<Staff {self.name}, Role: {self.role}>'
    
class StaffAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    building_stage_id = db.Column(db.Integer, db.ForeignKey('building_stage.id'), nullable=False)
    
    # Relationships
    staff = db.relationship('Staff', back_populates='building_stages')
    building_stage = db.relationship('BuildingStage', back_populates='staff')

    def __repr__(self):
        return f'<StaffAssignment {self.staff.name} at {self.building_stage.name}>'

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    date_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes, max 180
    cancelled = db.Column(db.Boolean, default=False)
    is_sold_out = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    building_stage_id = db.Column(db.Integer, db.ForeignKey('building_stage.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'), nullable=False)
    
    # Relationships
    artist = db.relationship('Artist', back_populates='performances')
    group = db.relationship('Group', back_populates='performances')
    building_stage = db.relationship('BuildingStage', back_populates='performances')
    staff = db.relationship('Staff', back_populates='performances')
    festival = db.relationship('Festival', back_populates='performances')
    ratings = db.relationship('Rating', back_populates='performance', lazy=True)
    tickets = db.relationship('Ticket', back_populates='performance', lazy=True)
    resale_queue = db.relationship('ResaleQueue', back_populates='performance', lazy=True)

    def __repr__(self):
        return f'<Performance {self.date_time} at {self.building_stage.name}>'

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)    
    # Relationships
    groups = db.relationship('Group', secondary=artist_group_association, back_populates='artists')
    performances = db.relationship('Performance', back_populates='artist')
    artist_info = db.relationship('ArtistGroupInfo', back_populates='artist', uselist=False)

    def __repr__(self):
        return f'<Artist {self.name}>'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    date_of_creation = db.Column(db.Date)    
   
    # Relationships
    artists = db.relationship('Artist', secondary=artist_group_association, back_populates='groups')
    performances = db.relationship('Performance', back_populates='group')
    group_info = db.relationship('ArtistGroupInfo', back_populates='group', uselist=False)

    def __repr__(self):
        return f'<Group {self.name}>'

class ArtistGroupInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    musical_category = db.Column(db.String(100))
    musical_subcategory = db.Column(db.String(100))
    website = db.Column(db.String(255))
    instagram = db.Column(db.String(100))
    image = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    # Foreign Keys (only one of these will be non-null)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    
    # Relationships
    artist = db.relationship('Artist', back_populates='artist_info')
    group = db.relationship('Group', back_populates='group_info')

    def __repr__(self):
        return f'<ArtistGroupInfo for {"Artist" if self.artist_id else "Group"}>'

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    
    # Relationships
    tickets = db.relationship('Ticket', back_populates='visitor')
    ratings = db.relationship('Rating', back_populates='visitor')
    resale_requests = db.relationship('ResaleQueue', back_populates='visitor')

    def __repr__(self):
        return f'<Visitor {self.first_name} {self.last_name}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # general, vip
    date_of_payment = db.Column(db.DateTime, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    barcode = db.Column(db.String(13), unique=True)  # EAN13
    status = db.Column(db.String(20), default='valid')  # status options: 'valid', 'used'
    
    resale_status = db.Column(db.String(20), default='not_for_resale') # not for resale, 
    #available, sold

    # Foreign Keys
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'), nullable=False)
    
    # Relationships
    event = db.relationship('Event', back_populates='tickets')
    performance = db.relationship('Performance', back_populates='tickets')
    owner = db.relationship('Visitor', back_populates='tickets', foreign_keys=[owner_id])
    festival = db.relationship('Festival', back_populates='tickets')
    resale_offers = db.relationship('ResaleQueue', back_populates='ticket') # one to many 

    def __repr__(self):
        return f'<Ticket {self.barcode} - {self.category}>'

class ResaleQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    is_seller = db.Column(db.Boolean, nullable=False)  # True for seller, False for buyer

    # Foreign keys
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.id'), nullable=False)
    ticket_category = db.Column(db.String(50), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

    # Relationships
    performance = db.relationship('Performance', back_populates='resale_queue')
    visitor = db.relationship('Visitor', back_populates='resale_requests')
    ticket = db.relationship('Ticket', back_populates='resale_offers')

    def __repr__(self):
        return f'<TicketResale for ticket {self.ticket_id}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_interpretation = db.Column(db.Integer, nullable=False)  # 1-5 
    sound_quality = db.Column(db.Integer, nullable=False)        # 1-5 
    lighting_effects = db.Column(db.Integer, nullable=False)       # 1-5
    stage_presence = db.Column(db.Integer, nullable=False)        # 1-5 
    organization = db.Column(db.Integer, nullable=False)          # 1-5 
    overall_impression = db.Column(db.Integer, nullable=False)    # 1-5 
    comments = db.Column(db.Text)
    
    # Foreign Keys
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.id'), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
    
    # Relationships
    performance = db.relationship('Performance', back_populates='ratings')
    visitor = db.relationship('Visitor', back_populates='ratings')

    def __repr__(self):
        return f'<Rating for performance {self.performance_id} by visitor {self.visitor_id}>'

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)


# source myenv/bin/activate
# python3 app.py
# flask db migrate -m 'message'
# flask db upgrade 
# eralchemy -i 'mysql+pymysql://maria:password@localhost/myflaskdb' -o erd.png
