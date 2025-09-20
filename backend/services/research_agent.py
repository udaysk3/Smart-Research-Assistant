import google.generativeai as genai
from typing import List, Dict, Any
import asyncio
import json
import os
from datetime import datetime
import uuid

from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .web_search import WebSearchService
from .real_pathway_service import RealPathwayService

class ResearchAgent:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.web_search = WebSearchService()
        self.pathway_service = RealPathwayService()
    
    async def generate_report(
        self, 
        question: str, 
        user_id: str,
        include_web_search: bool = True,
        include_live_data: bool = True
    ) -> Dict[str, Any]:
        """Generate a comprehensive research report"""
        
        report_id = str(uuid.uuid4())
        citations = []
        sources = []
        
        # 1. Search uploaded documents
        doc_results = await self.vector_store.search(question, user_id, top_k=5)
        doc_context = self._format_document_context(doc_results)
        
        # 2. Web search (if enabled)
        web_context = ""
        if include_web_search:
            web_results = await self.web_search.search(question, num_results=5)
            web_context = self._format_web_context(web_results)
            citations.extend(web_results)
        
        # 3. Live data from Pathway (if enabled)
        live_context = ""
        if include_live_data:
            live_results = await self.pathway_service.get_live_data(question)
            live_context = self._format_live_context(live_results)
            citations.extend(live_results)
        
        # 4. Generate comprehensive report using Gemini
        prompt = self._create_research_prompt(question, doc_context, web_context, live_context)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            answer = response.text
        except Exception as e:
            answer = f"Error generating report: {str(e)}"
        
        # 5. Extract and format citations
        formatted_citations = self._extract_citations(citations)
        
        # 6. Compile sources
        sources = list(set([cite.get("source", "") for cite in citations if cite.get("source")]))
        
        return {
            "report_id": report_id,
            "question": question,
            "answer": answer,
            "citations": formatted_citations,
            "sources": sources,
            "usage_count": 1,
            "credits_used": 1,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_document_context(self, doc_results: List[Dict]) -> str:
        """Format document search results for the prompt"""
        if not doc_results:
            return "No relevant documents found in uploaded files."
        
        context = "Relevant information from uploaded documents:\n"
        for i, result in enumerate(doc_results, 1):
            context += f"{i}. {result.get('content', '')}\n"
            context += f"   Source: {result.get('source', 'Unknown document')}\n\n"
        
        return context
    
    def _format_web_context(self, web_results: List[Dict]) -> str:
        """Format web search results for the prompt"""
        if not web_results:
            return "No relevant web information found."
        
        context = "Current web information:\n"
        for i, result in enumerate(web_results, 1):
            context += f"{i}. {result.get('snippet', '')}\n"
            context += f"   Source: {result.get('link', '')}\n\n"
        
        return context
    
    def _format_live_context(self, live_results: List[Dict]) -> str:
        """Format live data results for the prompt"""
        if not live_results:
            return "No recent live data available."
        
        context = "Recent live data updates:\n"
        for i, result in enumerate(live_results, 1):
            context += f"{i}. {result.get('content', '')}\n"
            context += f"   Source: {result.get('source', '')}\n"
            context += f"   Updated: {result.get('timestamp', '')}\n\n"
        
        return context
    
    def _create_research_prompt(
        self, 
        question: str, 
        doc_context: str, 
        web_context: str, 
        live_context: str
    ) -> str:
        """Create a comprehensive prompt for the research report"""
        
        prompt = f"""
You are a Smart Research Assistant. Generate a comprehensive, evidence-based report answering the following question:

QUESTION: {question}

CONTEXT INFORMATION:

{doc_context}

{web_context}

{live_context}

INSTRUCTIONS:
1. Provide a clear, concise answer to the question
2. Use information from all available sources
3. Include specific citations in your response using [1], [2], etc.
4. If information is conflicting, mention the different perspectives
5. Highlight any recent updates or fresh information
6. Keep the response structured and easy to read
7. Aim for 200-500 words unless the question requires more detail

FORMAT YOUR RESPONSE AS:
- Executive Summary (2-3 sentences)
- Key Findings (bullet points with citations)
- Detailed Analysis (with citations)
- Recent Updates (if any)
- Sources Used

Remember to cite sources using [1], [2], etc. throughout your response.
"""
        return prompt
    
    def _extract_citations(self, citations: List[Dict]) -> List[Dict]:
        """Extract and format citations from all sources"""
        formatted_citations = []
        
        for i, citation in enumerate(citations, 1):
            formatted_citations.append({
                "id": i,
                "source": citation.get("source", "Unknown"),
                "url": citation.get("link", ""),
                "title": citation.get("title", ""),
                "snippet": citation.get("snippet", "")[:200] + "..." if len(citation.get("snippet", "")) > 200 else citation.get("snippet", ""),
                "timestamp": citation.get("timestamp", "")
            })
        
        return formatted_citations
