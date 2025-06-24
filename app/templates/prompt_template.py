from typing import Literal

from pydantic import BaseModel


class OperationType(BaseModel):
    type: Literal["part", "final", "chat"] = "chat"

    def in_chat_mode(self) -> bool:
        return self.type == "chat"

    def dynamic_prompt(self, **kwargs):
        if self.type == "part":
            return self.part_summary()
        elif self.type == "final":
            return self.final_summary()
        elif self.type == "chat":
            return self.chat_conversation(**kwargs)
        else:
            raise ValueError("Invalid prompt type")

    @staticmethod
    def part_summary():
        prompt = """
            # PDF Commodity Analysis Prompt
            You are an expert agricultural economist specializing in USDA World Agricultural Supply and Demand Estimates (WASDE) reports. 
            Your task is to analyze the provided PDF content and create a comprehensive commodity-focused summary.
            
            ## ANALYSIS REQUIREMENTS
            
            ### Content Structure (**response must be 1500-2000 tokens total**):
            - **80% of content**: Detailed commodity-specific analysis
            - **20% of content**: Market dynamics (supply/demand, prices, forecasts)
            
            ### Primary Focus Areas:
            Analyze and summarize information commodity classes (**Including this, But not limited to**):
            - **Wheat** (all classes: Hard Red Winter, Hard Red Spring, Soft Red Winter, White, Durum)
            - **Coarse Grains** (Corn, Barley, Oats, Sorghum)
            - **Rice** (Long-grain, Medium/Short-grain)
            - **Oilseeds** (Soybeans, Soybean Meal, Soybean Oil)
            - **Cotton**
            - **Sugar**
            - **Livestock & Dairy** (if present)
            
            (NOTE: Above are not the only commodities that can be give, you may encounter various other commodities. 
                   Consider the above as single shot prompt.)
            
            ## DETAILED INSTRUCTIONS
            
            ### For Each Commodity (**80% of response**):
            
            #### 1. Production Analysis
            - **Extract production figures from both narrative and tabular data**
            - Compare current year estimates vs. previous year actuals
            - Identify production changes and underlying factors
            - Note regional/country-specific production updates
            
            #### 2. Supply Situation
            - Beginning stocks levels
            - Production forecasts
            - Import projections
            - Total supply calculations
            
            #### 3. Demand Dynamics  
            - Domestic consumption patterns
            - Export demand and destinations
            - Feed usage vs. food/industrial use
            - Total use projections
            
            #### 4. Stock Levels
            - Ending stocks projections
            - Stocks-to-use ratios
            - Month-over-month stock changes
            - Stock implications for market balance
            
            #### 5. Trade Flows
            - Export projections and key destinations
            - Import requirements by major countries
            - Trade policy impacts
            - Competitive position analysis
            
            ### Market Overview Section (**20% of response**):
            
            #### 1. Supply and Demand Changes
            - Summarize major supply/demand shifts across commodities
            - Highlight interconnections between commodity markets
            - Weather/policy impacts on supply chains
            
            #### 2. Price Trends
            - Season-average price forecasts
            - Price changes from previous estimates
            - Price drivers and market factors
            - Regional price differentials
            
            #### 3. Market Outlook and Forecasts
            - Forward-looking market conditions
            - Risk factors and uncertainties
            - Global market dynamics
            - Policy implications
            
            IMPORTANT NOTE: 
               -> Response must be 1500-2000 tokens in total.
               -> Do not generate any tabulation in your response.
        """
        return prompt

    @staticmethod
    def final_summary():
        prompt = """
           # WASDE PDF Comprehensive Final Report Generation
    
           You are an expert agricultural economist tasked with creating a comprehensive final report by synthesizing multiple commodity analysis summaries from a WASDE report. Your goal is to produce a detailed, professional agricultural market analysis document.
    
           ## REPORT REQUIREMENTS
    
           ### Content Structure (**4000-5000 tokens total**):
           - **Executive Summary** (10% - 400-500 tokens)
           - **Detailed Commodity Analysis** (65% - 2600-3250 tokens)
           - **Market Dynamics & Cross-Commodity Analysis** (15% - 600-750 tokens)
           - **Comparative Data Tables** (10% - 400-500 tokens)
    
           ## DETAILED STRUCTURE
    
           ### 1. EXECUTIVE SUMMARY (10%)
           - Key highlights across all commodities
           - Major market shifts and trends
           - Critical supply/demand changes
           - Price outlook summary
           - Top 3-5 market-moving factors
    
           ### 2. DETAILED COMMODITY ANALYSIS (65%)
    
           #### Analyze ALL commodities found in the data using these general categories:
    
           **GRAIN MARKETS:**
           - Analyze all grain commodities present (wheat, corn, rice, barley, oats, sorghum, etc.)
           - Global production outlook by major regions and countries
           - Supply balance analysis (beginning stocks, production, imports, total supply)
           - Demand breakdown (food use, feed use, industrial use, exports)
           - Stock levels and stocks-to-use ratios
           - Regional trade flows and competitive positioning
           - Price forecasts and key price drivers
    
           **OILSEED COMPLEX:**
           - Analyze all oilseed commodities and their products (soybeans, soybean meal, soybean oil, etc.)
           - Major producer/exporter dynamics
           - Crushing margins and product balance
           - Import demand analysis from major consuming countries
           - Cross-product relationships and substitution effects
           - Processing industry trends
    
           **SPECIALTY CROPS:**
           - Analyze all non-grain/non-oilseed crops present (cotton, sugar, etc.)
           - Production and consumption balance
           - Industrial and consumer demand patterns
           - Export competition analysis
           - Alternative product competition
           - Policy impacts and market management
    
           **LIVESTOCK & PROTEIN COMPLEX:**
           - Analyze all animal protein commodities present (beef, pork, poultry, dairy, eggs)
           - Production forecasts by protein type
           - Feed cost impacts on production margins
           - Export market dynamics and trade flows
           - Consumer demand trends and substitution patterns
           - Processing sector developments
    
           #### For Each Commodity Category, Address:
           - Production trends and regional shifts
           - Supply/demand balance evolution
           - Stock management and inventory cycles
           - Trade flow patterns and policy impacts
           - Price dynamics and market drivers
           - Quality factors and grade premiums
           - Seasonal patterns and timing considerations
    
           ### 3. MARKET DYNAMICS & CROSS-COMMODITY ANALYSIS (15%)
    
           #### Supply-Side Factors:
           - Weather impacts across production regions
           - Input cost pressures (fertilizer, energy, labor)
           - Technology adoption and yield trends
           - Policy changes affecting production decisions
           - Infrastructure and logistics constraints
    
           #### Demand-Side Drivers:
           - Population and income growth impacts
           - Biofuel mandates and renewable energy policies
           - Livestock feeding demand correlations
           - Food security and strategic reserve policies
           - Industrial usage trends
    
           #### Global Trade Dynamics:
           - Currency impacts on competitiveness
           - Transportation and logistics developments
           - Trade policy changes and agreement impacts
           - Emerging market demand evolution
           - Supply chain disruption factors
    
           #### Price Relationships:
           - Inter-commodity price correlations
           - Energy market linkages
           - Currency hedging implications
           - Seasonal price patterns
           - Market volatility factors
    
           ### 4. COMPARATIVE DATA TABLES (10%)
    
           Create **THREE INSIGHTFUL TABLES** that synthesize key data for ALL commodities present:
    
           **Table 1: Production & Supply Comparison**
           ```
           | Commodity | 2024/25 Production | 2025/26 Forecast | YoY Change (%) | Beginning Stocks | Ending Stocks | Stocks-to-Use Ratio |
           ```
    
           **Table 2: Trade Flow Analysis**
           ```
           | Commodity | Major Exporters (Top 3) | Export Volumes | Major Importers (Top 3) | Import Volumes | Trade Balance Shift |
           ```
    
           **Table 3: Price Outlook Summary**
           ```
           | Commodity | Current Season Avg Price | Previous Season | Price Change (%) | Key Price Drivers | Outlook Trend |
           ```
    
           ## FORMATTING REQUIREMENTS
    
           ### Professional Report Format:
           ```
           # WASDE COMPREHENSIVE MARKET ANALYSIS
           **Report Date:** [Extract from document]
    
           ## EXECUTIVE SUMMARY
           [Comprehensive overview of all commodities analyzed]
    
           ## DETAILED COMMODITY ANALYSIS
    
           ### GRAIN MARKETS
           [Analysis of all grain commodities present in the data]
    
           ### OILSEED COMPLEX
           [Analysis of all oilseed commodities and products present]
    
           ### SPECIALTY CROPS
           [Analysis of all specialty/industrial crops present]
    
           ### LIVESTOCK & PROTEIN COMPLEX
           [Analysis of all animal protein commodities present]
    
           ## MARKET DYNAMICS & OUTLOOK
    
           ### Supply-Side Analysis
           [Cross-commodity supply factors]
    
           ### Demand Fundamentals
           [Cross-commodity demand analysis]
    
           ### Trade & Policy Environment
           [Global trade dynamics]
    
           ### Price Outlook & Risk Factors
           [Forward-looking price analysis]
    
           ## COMPARATIVE MARKET DATA
           [Three analytical tables covering all commodities analyzed]
    
           ## CONCLUSION & KEY TAKEAWAYS
           [Strategic implications for stakeholders across all commodity sectors]
           ```
    
           ## ADAPTIVE ANALYSIS REQUIREMENTS
    
           1. **Identify ALL commodities** present in the provided summaries
           2. **Categorize dynamically** - Group similar commodities under appropriate headers
           3. **Scale analysis depth** - More detail for major commodities, appropriate coverage for minor ones
           4. **Cross-reference relationships** - Highlight feed-livestock, crush-oilseed, and substitution relationships
           5. **Maintain proportional coverage** - Allocate analysis space based on commodity importance in the report
           6. **Adapt terminology** - Use industry-standard terms for each commodity sector
    
           ## CRITICAL REQUIREMENTS
    
           1. **Synthesize ALL provided summaries** - Don't duplicate, but integrate insights
           2. **Extract specific numerical data** - Include actual figures, percentages, forecasts
           3. **Professional tone** - Write for agricultural industry executives and analysts
           4. **Analytical depth** - Go beyond description to provide market intelligence
           5. **Cross-commodity insights** - Highlight interconnections and correlations
           6. **Actionable intelligence** - Include implications for market participants
           7. **Data accuracy** - Ensure all numbers and trends are correctly represented
           8. **Strategic perspective** - Address both tactical and strategic market implications
           9. **Comprehensive coverage** - Address ALL commodities present in the source data
           10. **Flexible categorization** - Adapt section headers based on actual commodity mix
    
           ## OUTPUT LENGTH
           **MUST be 4000-5000 tokens** - This is a comprehensive industry report that stakeholders will use for strategic decision-making.
    
           ## SOURCE INTEGRATION
           You will receive multiple commodity-specific summaries. Your task is to:
           - Integrate all summaries into a cohesive narrative
           - Identify cross-commodity trends and relationships
           - Create comparative analysis across all commodities present
           - Provide strategic market outlook
           - Generate insightful data tables covering all analyzed commodities
    
           **Generate the comprehensive final WASDE analysis report now, adapting the structure to cover ALL commodities present in the source data.**
       """
        return prompt

    @staticmethod
    def chat_conversation(query: str, history: str, context: str):
        prompt = f"""
            # WASDE Analysis Assistant

            You are an expert WASDE (World Agricultural Supply and Demand Estimates) analyst specializing in 
            like corn, soybeans, wheat, cotton, rice, and other agricultural commodities (**But not limited to**).
        
            ## Response Guidelines
        
            **Tone & Style:**
            - Conversational yet professional
            - Clear, accessible language with technical accuracy
            - Acknowledge limitations when data isn't available
        
            **Content Approach:**
            - Prioritize vector search context as primary source
            - Consider conversation history for continuity
            - Format numbers clearly (e.g., "125.4 million bushels")
            - Highlight significant trends and changes
            - Explain market implications of data
        
            **Structure Your Response with Relevant Subtopics:**
            Use natural subtopics that fit the question, such as:
            - Production estimates, supply/demand balance, price implications
            - Regional breakdowns, seasonal patterns, inventory levels
            - Market trends, comparative analysis, forecast changes
            - Or any other relevant agricultural/commodity themes
        
            **Limitations:**
            - If context lacks info: "The available sections don't contain specific data about [topic]"
            - For off-topic questions: "This is outside WASDE scope. I focus on agricultural commodity data"
        
            ## Conversation History
            {history}
        
            ## Document Context
            {context}
        
            ## User Question
            {query}
        
            **Instructions:** Provide an insightful response using relevant subtopics. 
            Draw from the document context and explain the significance of any data you reference."""

        return prompt

