import click
from .extensions import db
from .models import Category

@click.command("seed-categories")
def seed_categories():
    initial = [
        ("Electronics", "electronics", "Cameras, audio and useful electronics."),
        ("Tools & Equipment", "tools-equipment", "Repair, cleaning and gardening tools."),
        ("Event Equipment", "event-equipment", "Projectors, speakers and event accessories."),
    ]
    for name, slug, description in initial:
        if not db.session.scalar(db.select(Category).where(Category.slug == slug)):
            db.session.add(Category(name=name, slug=slug, description=description))
    db.session.commit()
    click.echo("Default categories are ready.")

def register_commands(app):
    app.cli.add_command(seed_categories)
