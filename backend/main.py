from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import uvicorn

from services.research_agent import ResearchAgent
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.real_billing_service import RealBillingService
from services.real_pathway_service import RealPathwayService
from models.database import get_db, init_db
from routes.auth import router as auth_router
from middleware.auth_middleware import get_current_user

# Load environment variables
load_dotenv()

app = FastAPI(title="Smart Research Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
research_agent = ResearchAgent()
document_processor = DocumentProcessor()
vector_store = VectorStore()
billing_service = RealBillingService()
pathway_service = RealPathwayService()

# Initialize database
init_db()

# Include auth router
app.include_router(auth_router)

class QuestionRequest(BaseModel):
    question: str
    include_web_search: bool = True
    include_live_data: bool = True

class ReportResponse(BaseModel):
    report_id: str
    question: str
    answer: str
    citations: List[dict]
    sources: List[str]
    usage_count: int
    credits_used: int
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Smart Research Assistant API is running!"}

@app.post("/api/research", response_model=ReportResponse)
async def generate_research_report(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Generate a research report based on user question"""
    try:
        user_id = current_user["user_id"]
        
        # Check user credits
        if not await billing_service.check_credits(user_id):
            raise HTTPException(status_code=402, detail="Insufficient credits")
        
        # Generate report using research agent
        report = await research_agent.generate_report(
            question=request.question,
            user_id=user_id,
            include_web_search=request.include_web_search,
            include_live_data=request.include_live_data
        )
        
        # Deduct credits
        await billing_service.deduct_credits(user_id, 1)
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process documents for research"""
    try:
        user_id = current_user["user_id"]
        processed_docs = []
        
        for file in files:
            # Save uploaded file
            file_path = f"uploads/{user_id}_{file.filename}"
            os.makedirs("uploads", exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Process document
            doc_data = await document_processor.process_document(file_path)
            
            # Store in vector database
            await vector_store.add_document(doc_data, user_id)
            
            # Store document metadata in SQL database
            from models.database import Document
            import uuid
            document = Document(
                document_id=str(uuid.uuid4()),
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_type=file.content_type or "application/octet-stream",
                file_size=len(content),
                pages=len(doc_data.get("pages", [])),
                status="processed"
            )
            db.add(document)
            db.commit()
            
            processed_docs.append({
                "filename": file.filename,
                "pages": len(doc_data.get("pages", [])),
                "status": "processed"
            })
        
        return {"message": "Documents uploaded successfully", "documents": processed_docs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usage")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get usage statistics for the current user"""
    try:
        user_id = current_user["user_id"]
        stats = await billing_service.get_usage_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": {
        "research_agent": "active",
        "vector_store": "active",
        "billing_service": "active",
        "pathway_service": "active"
    }}

@app.post("/api/billing/purchase")
async def purchase_credits(
    user_id: str,
    amount: int,
    payment_method: str = "card",
    db=Depends(get_db)
):
    """Purchase credits using Flexprice"""
    try:
        result = await billing_service.purchase_credits(user_id, amount, payment_method)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pathway/live-data")
async def get_live_data(query: str):
    """Get live data from Pathway and other sources"""
    try:
        live_data = await pathway_service.get_live_data(query)
        return {"live_data": live_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{user_id}")
async def get_user_documents(user_id: str, db=Depends(get_db)):
    """Get all documents for a user"""
    try:
        documents = await vector_store.get_user_documents(user_id)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: str = "default_user", db=Depends(get_db)):
    """Delete a document"""
    try:
        # This would need to be implemented in vector_store
        return {"message": "Document deletion not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pathway/freshness/{query}")
async def get_freshness_score(query: str):
    """Get freshness score for a query"""
    try:
        score = await pathway_service.get_freshness_score(query)
        return score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

