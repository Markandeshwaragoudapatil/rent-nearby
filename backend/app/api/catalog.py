from flask import Blueprint, jsonify, request, abort
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from ..extensions import db
from ..models import Category, Product

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.get("/categories")
def categories():
    rows = db.session.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.name)).all()
    return jsonify({"items": [{"id": str(row.id), "name": row.name, "slug": row.slug, "description": row.description} for row in rows]})

@catalog_bp.get("/products")
def products():
    query = select(Product).options(joinedload(Product.category), selectinload(Product.images), joinedload(Product.pricing)).where(Product.status == "ACTIVE")
    search = request.args.get("q", "").strip()
    locality = request.args.get("locality", "").strip()
    category = request.args.get("category", "").strip()
    if search:
        query = query.where(Product.title.ilike("%" + search.replace("%", "\\%").replace("_", "\\_") + "%"))
    if locality:
        query = query.where(Product.locality.ilike("%" + locality + "%"))
    if category:
        query = query.join(Product.category).where(Category.slug == category)
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        abort(400, description="page and per_page must be integers")
    total = db.session.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.session.scalars(query.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page)).unique().all()
    return jsonify({"items": [row.to_dict() for row in rows], "page": page, "per_page": per_page, "total": total})

@catalog_bp.get("/products/<uuid:product_id>")
def detail(product_id):
    product = db.session.scalar(select(Product).options(joinedload(Product.category), selectinload(Product.images), joinedload(Product.pricing)).where(Product.id == product_id, Product.status == "ACTIVE"))
    if product is None:
        abort(404)
    return jsonify(product.to_dict())
