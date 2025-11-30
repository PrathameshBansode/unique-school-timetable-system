from app import db

class ResourceUsage(db.Model):
    __tablename__ = 'resource_usage'
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('timetables.id'), nullable=False)
    status = db.Column(db.Enum('Available', 'In Use', name='resource_status'), nullable=False)
