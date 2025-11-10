import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Project, Publication, BlogPost, ContactMessage

app = FastAPI(title="Muhamad Juwandi Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or ("✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set")
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Seed/sample content endpoints
@app.post("/seed", tags=["admin"])
async def seed_content():
    """Seed database with sample projects, publications, and blog posts."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Only seed if empty
    if db["project"].count_documents({}) == 0:
        samples: List[Project] = [
            Project(
                title="Customer Churn Prediction",
                slug="customer-churn-prediction",
                summary="Predict churn with explainable ML to prioritize retention actions.",
                domain="ML",
                stack=["Python", "scikit-learn", "XGBoost", "SHAP"],
                year=2023,
                problem="Identify customers likely to churn in the next 60 days.",
                approach="Feature engineering + gradient boosting with class-weighting and calibration.",
                dataset="Telco churn dataset + proprietary CRM features.",
                model="XGBoost with Bayesian optimization; SHAP for interpretability.",
                results="AUC 0.89, recall 76% at 15% alert rate.",
                impact="Reduced churn by 5.2% in pilot, saving ~$1.1M ARR.",
                github_url="https://github.com/",
                tags=["classification", "retention", "explainability"],
                plotly_fig={
                    "data": [{"type": "bar", "x": ["Contract", "Tenure", "MonthlyCharges"], "y": [0.34, 0.27, 0.18]}],
                    "layout": {"title": "Top Features (SHAP)"}
                }
            ),
            Project(
                title="Demand Forecasting with Hierarchical Time Series",
                slug="demand-forecasting-hts",
                summary="Weekly forecasts across 120 SKUs with reconciliation and uncertainty.",
                domain="Time Series",
                stack=["Python", "Prophet", "statsmodels", "scikit-learn"],
                year=2022,
                problem="Improve inventory planning across regions and SKUs.",
                approach="Feature-rich SARIMAX + gradient boosting for residuals; hierarchical reconciliation.",
                dataset="Sales transactions 3 years + promo calendar.",
                model="SARIMAX + LightGBM residual model.",
                results="MAPE 8.6% overall; stockouts down 23%.",
                impact="Saved $420k in holding and lost sales.",
                github_url="https://github.com/",
                tags=["forecasting", "inventory", "hts"],
            ),
            Project(
                title="Interactive Mobility Dashboard",
                slug="mobility-dashboard",
                summary="City mobility patterns explored via interactive geovisualizations.",
                domain="Visualization",
                stack=["Python", "Altair", "Deck.gl"],
                year=2024,
                problem="Understand peak congestion corridors.",
                approach="Aggregated GPS pings and derived OD matrices; built interactive views.",
                dataset="1.2B GPS pings over 6 months.",
                model="Clustering + KDE for hotspots.",
                results="Revealed 3 critical choke points.",
                impact="Informed signal timing policy saving ~8% commute time.",
                github_url="https://github.com/",
                tags=["geospatial", "altair", "dashboard"],
            ),
        ]
        for p in samples:
            create_document("project", p)

    if db["publication"].count_documents({}) == 0:
        pubs = [
            {
                "title": "Storytelling with Data: From Insight to Impact",
                "venue": "Global Data Summit",
                "year": 2024,
                "authors": ["Muhamad Juwandi"],
                "slides_url": "https://slides.com/",
                "kind": "talk",
            },
            {
                "title": "Robust ML Pipelines with MLOps",
                "venue": "PyData",
                "year": 2023,
                "authors": ["Muhamad Juwandi"],
                "slides_url": "https://slides.com/",
                "kind": "workshop",
            },
        ]
        for pub in pubs:
            create_document("publication", pub)

    if db["blogpost"].count_documents({}) == 0:
        posts = [
            {
                "title": "Designing Ethical AI Systems",
                "slug": "ethical-ai",
                "excerpt": "Principles and practical checklists for responsible ML.",
                "body": "Long-form body in Markdown or MDX.",
                "topics": ["ethics", "ai"],
                "published_at": "2024-05-11",
            },
            {
                "title": "Visualization Patterns that Clarify",
                "slug": "viz-patterns",
                "excerpt": "Choosing encodings that match mental models.",
                "body": "Post content...",
                "topics": ["viz", "design"],
                "published_at": "2024-03-03",
            },
            {
                "title": "From Notebook to Production",
                "slug": "notebook-to-prod",
                "excerpt": "A compact guide to MLOps for data scientists.",
                "body": "Post content...",
                "topics": ["mlops", "devops"],
                "published_at": "2023-11-18",
            },
            {
                "title": "R + Python for Analytics",
                "slug": "r-plus-python",
                "excerpt": "Leverage strengths of both ecosystems.",
                "body": "Post content...",
                "topics": ["r", "python"],
                "published_at": "2023-07-07",
            },
        ]
        for post in posts:
            create_document("blogpost", post)

    return {"status": "ok"}

# Public read endpoints
@app.get("/projects", response_model=List[Project])
async def list_projects(domain: Optional[str] = None, year: Optional[int] = None, q: Optional[str] = None):
    if db is None:
        return []
    query = {}
    if domain:
        query["domain"] = domain
    if year:
        query["year"] = year
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"summary": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    docs = get_documents("project", query)
    # Coerce to Pydantic
    return [Project(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

@app.get("/publications", response_model=List[Publication])
async def list_publications():
    if db is None:
        return []
    docs = get_documents("publication", {})
    return [Publication(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

@app.get("/blog", response_model=List[BlogPost])
async def list_blog():
    if db is None:
        return []
    docs = get_documents("blogpost", {})
    return [BlogPost(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

# Contact form endpoint
class ContactResponse(BaseModel):
    status: str

@app.post("/contact", response_model=ContactResponse)
async def submit_contact(msg: ContactMessage):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    create_document("contactmessage", msg)
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
