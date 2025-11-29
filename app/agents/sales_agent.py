"""
Multi-Agent System for Sales Analytics
Coordinates multiple specialized agents for comprehensive analysis
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from app.tools.analytics_tools import ALL_TOOLS
from app.core.config import settings
from app.core.logger import app_logger as logger
import time


class SalesAnalyticsAgent:
    """Main orchestrator agent for sales analytics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.AGENT_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.tools = ALL_TOOLS
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor"""
        
        system_prompt = """You are an advanced AI sales analytics assistant with expertise in business intelligence, 
            data analysis, and strategic planning. You have access to comprehensive sales data and analytical tools.
            Your capabilities include:
            1. Descriptive Analytics: Summarize what has happened in the business
            2. Diagnostic Analytics: Explain why things happened
            3. Predictive Analytics: Forecast what is likely to happen
            4. Prescriptive Analytics: Recommend what actions should be taken
            When responding to queries:
            - Always use the appropriate tools to fetch real data
            - Provide clear, actionable insights
            - Include specific numbers and metrics
            - Offer recommendations when appropriate
            - Be conversational but professional
            - If multiple analytics types are relevant, provide a comprehensive response
            Available tools:
            - get_sales_summary: Get overall sales metrics
            - analyze_time_trends: Analyze trends over time
            - analyze_by_category: Category performance analysis
            - analyze_by_region: Regional performance analysis
            - detect_anomalies: Find outliers and anomalies
            - analyze_correlations: Understand metric relationships
            - analyze_discount_impact: Discount effectiveness analysis
            - forecast_sales: Predict future sales
            - predict_customer_churn: Identify at-risk customers
            - identify_growth_opportunities: Find growth potential
            - optimize_pricing: Pricing strategy recommendations
            - optimize_inventory: Inventory management recommendations
            - recommend_marketing_strategy: Marketing budget allocation
            - recommend_retention_strategy: Customer retention strategies
            - get_action_plan: Comprehensive action plan
            Always provide insights in a clear, structured format."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.AGENT_VERBOSE,
            max_iterations=settings.MAX_ITERATIONS,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user query and return response"""
        try:
            start_time = time.time()
            
            # Add context to query if provided
            enhanced_query = query
            if context:
                enhanced_query = f"{query}\n\nAdditional context: {context}"
            
            # Execute agent
            logger.info(f"Processing query: {query}")
            result = await self.agent_executor.ainvoke({"input": enhanced_query})
            
            execution_time = time.time() - start_time
            
            # Extract insights and recommendations from the response
            insights = self._extract_insights(result['output'])
            recommendations = self._extract_recommendations(result['output'])
            analytics_type = self._determine_analytics_type(query)
            
            response = {
                'answer': result['output'],
                'analytics_type': analytics_type,
                'insights': insights,
                'recommendations': recommendations,
                'execution_time': round(execution_time, 2),
                'confidence': 0.85  # Placeholder confidence score
            }
            
            logger.info(f"Query processed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights from response"""
        insights = []
        
        # Simple extraction based on patterns
        keywords = ['increase', 'decrease', 'growth', 'decline', 'trend', 'highest', 'lowest', 'best', 'worst']
        sentences = text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                clean_sentence = sentence.strip()
                if clean_sentence and len(clean_sentence) > 20:
                    insights.append(clean_sentence)
        
        return insights[:5]  # Return top 5 insights
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from response"""
        recommendations = []
        
        # Look for recommendation patterns
        rec_keywords = ['recommend', 'should', 'suggest', 'consider', 'optimize', 'improve', 'focus on']
        sentences = text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in rec_keywords):
                clean_sentence = sentence.strip()
                if clean_sentence and len(clean_sentence) > 15:
                    recommendations.append(clean_sentence)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _determine_analytics_type(self, query: str) -> str:
        """Determine the type of analytics from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['forecast', 'predict', 'future', 'will', 'likely']):
            return 'predictive'
        elif any(word in query_lower for word in ['recommend', 'should', 'optimize', 'action', 'strategy']):
            return 'prescriptive'
        elif any(word in query_lower for word in ['why', 'cause', 'reason', 'impact', 'correlation']):
            return 'diagnostic'
        else:
            return 'descriptive'
    
    def reset_conversation(self):
        """Reset conversation memory"""
        self.memory.clear()
        logger.info("Conversation memory reset")


# Specialized agents for specific tasks
class DescriptiveAgent:
    """Agent specialized in descriptive analytics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,  
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.tools = [
            tool for tool in ALL_TOOLS 
            if tool.name in ['get_sales_summary', 'analyze_time_trends', 'analyze_by_category', 'analyze_by_region']
        ]
    
    async def analyze(self, query: str) -> str:
        """Perform descriptive analysis"""
        prompt = f"""As a descriptive analytics expert, analyze the following query using available data:
            Query: {query}
            Provide a comprehensive summary of what has happened, including key metrics and trends."""
        
        response = await self.llm.ainvoke(prompt)
        return response.content


class DiagnosticAgent:
    """Agent specialized in diagnostic analytics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.tools = [
            tool for tool in ALL_TOOLS 
            if tool.name in ['detect_anomalies', 'analyze_correlations', 'analyze_discount_impact']
        ]
    
    async def diagnose(self, query: str) -> str:
        """Perform diagnostic analysis"""
        prompt = f"""As a diagnostic analytics expert, investigate the following query:
            Query: {query}
            Explain why things happened, identify root causes, and analyze contributing factors."""
        
        response = await self.llm.ainvoke(prompt)
        return response.content


class PredictiveAgent:
    """Agent specialized in predictive analytics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.tools = [
            tool for tool in ALL_TOOLS 
            if tool.name in ['forecast_sales', 'predict_customer_churn', 'identify_growth_opportunities']
        ]
    
    async def predict(self, query: str) -> str:
        """Perform predictive analysis"""
        prompt = f"""As a predictive analytics expert, forecast outcomes for the following query:
            Query: {query}
            Provide predictions, forecasts, and likelihood assessments based on historical data."""
        
        response = await self.llm.ainvoke(prompt)
        return response.content


class PrescriptiveAgent:
    """Agent specialized in prescriptive analytics"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.4,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.tools = [
            tool for tool in ALL_TOOLS 
            if tool.name in ['optimize_pricing', 'optimize_inventory', 'recommend_marketing_strategy', 
                           'recommend_retention_strategy', 'get_action_plan']
        ]
    
    async def prescribe(self, query: str) -> str:
        """Provide prescriptive recommendations"""
        prompt = f"""As a prescriptive analytics expert, recommend actions for the following query:
            Query: {query}
            Provide specific, actionable recommendations with expected outcomes and priorities."""
        
        response = await self.llm.ainvoke(prompt)
        return response.content


# Global agent instance
sales_agent = SalesAnalyticsAgent()
