"""DeepSeek R1 AI Integration for ERP"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekR1Agent:
    """AI Agent powered by DeepSeek R1 for ERP automation"""
    
    def __init__(self, api_url: str = "http://localhost:11434/api/generate"):
        self.api_url = api_url
        self.model = "deepseek-r1:7b"
        logger.info(f"DeepSeek R1 Agent initialized with model: {self.model}")
    
    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek R1 API"""
        try:
            import requests
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"DeepSeek API error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Failed to call DeepSeek: {e}")
            return ""
    
    def analyze_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data and provide insights"""
        prompt = f"""
        Analyze the following financial data and provide key insights:
        
        Revenue: {data.get('revenue', 0)}
        Expenses: {data.get('expenses', 0)}
        Profit: {data.get('profit', 0)}
        Cash Balance: {data.get('cash_balance', 0)}
        
        Provide:
        1. Financial health assessment
        2. Key risks identified
        3. Recommendations for improvement
        4. Expected next quarter performance
        
        Keep response concise and actionable.
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "analysis": response,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def predict_cash_flow(self, historical_data: List[float]) -> Dict[str, Any]:
        """Predict future cash flow based on historical data"""
        prompt = f"""
        Based on the following historical cash flow data: {historical_data}
        
        Predict the next 3 months cash flow and identify:
        1. Expected cash flow trends
        2. Potential cash shortage periods
        3. Recommended actions
        
        Data points: {len(historical_data)} months
        """
        
        response = self._call_deepseek(prompt)
        
        return {
            "prediction": response,
            "confidence": "medium",
            "timestamp": datetime.now().isoformat()
        }

deepseek_agent = DeepSeekR1Agent()
