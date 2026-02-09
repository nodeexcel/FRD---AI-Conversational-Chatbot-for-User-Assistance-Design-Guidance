"""Text-to-SQL agent for natural language database queries with real PostgreSQL."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncpg
import logging
import json

from app.config import settings
from app.core.llm.openai_client_v3 import openai_client_v3 as openai_client

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Database query result."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    sql_query: str


class SQLAgent:
    """Text-to-SQL agent for converting natural language to SQL queries."""
    
    def __init__(self):
        """Initialize the SQL agent."""
        self.pool: Optional[asyncpg.Pool] = None
        self.schema_info = {}
        self._initialized = False
        self._use_mock = False
        logger.info("SQL agent initialized")
    
    async def initialize(self):
        """Initialize PostgreSQL connection pool."""
        if self._initialized:
            return
        
        try:
            # Create async connection pool
            self.pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=2,
                max_size=10
            )
            
            # Load schema information
            await self._load_schema()
            
            self._initialized = True
            logger.info(f"SQL agent connected to PostgreSQL with {len(self.schema_info)} tables")
            
        except Exception as e:
            logger.warning(f"PostgreSQL not available: {e}. Using mock mode.")
            self._use_mock = True
            self._initialized = True
            self._setup_mock_schema()
    
    def _setup_mock_schema(self):
        """Setup mock schema for when PostgreSQL is not available."""
        self.schema_info = {
            "products": {
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "category", "type": "VARCHAR"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "fabric_type", "type": "VARCHAR"},
                    {"name": "color", "type": "VARCHAR"},
                    {"name": "price", "type": "DECIMAL"},
                    {"name": "occasion", "type": "VARCHAR"},
                    {"name": "availability", "type": "BOOLEAN"}
                ],
                "primary_keys": ["id"],
                "foreign_keys": []
            }
        }
    
    async def _load_schema(self):
        """Load database schema information."""
        if not self.pool or self._use_mock:
            return
        
        try:
            async with self.pool.acquire() as conn:
                # Get table names
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                for table in tables:
                    table_name = table["table_name"]
                    
                    # Get columns
                    columns = await conn.fetch(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = $1
                        ORDER BY ordinal_position
                    """, table_name)
                    
                    # Get primary keys
                    pk = await conn.fetch(f"""
                        SELECT a.attname as column_name
                        FROM pg_index i
                        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                        WHERE i.indrelid = $1::regclass AND i.indisprimary
                    """, table_name)
                    
                    # Get foreign keys
                    fks = await conn.fetch(f"""
                        SELECT 
                            kcu.column_name,
                            ccu.table_name AS referenced_table,
                            ccu.column_name AS referenced_column
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                            AND ccu.table_schema = tc.table_schema
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                            AND tc.table_name = $1
                    """, table_name)
                    
                    self.schema_info[table_name] = {
                        "columns": [
                            {
                                "name": col["column_name"],
                                "type": col["data_type"],
                                "nullable": col["is_nullable"] == "YES"
                            }
                            for col in columns
                        ],
                        "primary_keys": [pk_col["column_name"] for pk_col in pk],
                        "foreign_keys": [
                            {
                                "columns": [fk["column_name"]],
                                "referred_table": fk["referenced_table"],
                                "referred_columns": [fk["referenced_column"]]
                            }
                            for fk in fks
                        ]
                    }
                    
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
    
    async def execute(
        self,
        natural_query: str,
        entities: Optional[List[Dict]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a natural language database query."""
        try:
            # Initialize if not done
            if not self._initialized:
                await self.initialize()
            
            # Step 1: Generate SQL from natural language using OpenAI
            sql_query = await self._generate_sql(natural_query, entities)
            
            # Step 2: Validate the query
            validation = self.validate_query(sql_query)
            if not validation["valid"]:
                return {
                    "error": validation.get("error", "Invalid query"),
                    "sql_query": sql_query,
                    "results": [],
                    "row_count": 0
                }
            
            # Step 3: Execute the query
            if self._use_mock:
                result = self._get_mock_results(sql_query, natural_query)
            else:
                result = await self._execute_sql(sql_query)
            
            # Step 4: Format results
            return {
                "sql_query": sql_query,
                "results": result.rows,
                "columns": result.columns,
                "row_count": result.row_count,
                "intent": self._extract_intent(natural_query),
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {
                "error": str(e),
                "sql_query": sql_query if 'sql_query' in locals() else None,
                "results": [],
                "row_count": 0
            }
    
    def _get_mock_results(self, sql: str, query: str) -> QueryResult:
        """Return mock results when PostgreSQL is not available."""
        query_lower = query.lower()
        
        # Count queries
        if "count" in query_lower or "how many" in query_lower:
            if "summer" in query_lower:
                return QueryResult(
                    columns=["count"],
                    rows=[{"count": 3}],
                    row_count=1,
                    sql_query=sql
                )
            elif "red" in query_lower:
                return QueryResult(
                    columns=["count"],
                    rows=[{"count": 2}],
                    row_count=1,
                    sql_query=sql
                )
            else:
                return QueryResult(
                    columns=["count"],
                    rows=[{"count": 10}],
                    row_count=1,
                    sql_query=sql
                )
        
        # List queries
        return QueryResult(
            columns=["id", "name", "category", "price", "color"],
            rows=[
                {"id": 1, "name": "Blue Cotton Summer Dress", "category": "summer_dress", "price": 79.99, "color": "blue"},
                {"id": 2, "name": "Yellow Rayon Summer Suit", "category": "summer_suit", "price": 69.99, "color": "yellow"},
                {"id": 3, "name": "Red Silk Evening Gown", "category": "evening_gown", "price": 349.99, "color": "red"}
            ],
            row_count=3,
            sql_query=sql
        )
    
    async def _generate_sql(
        self,
        query: str,
        entities: Optional[List[Dict]] = None
    ) -> str:
        """Generate SQL query from natural language using OpenAI or rule-based fallback."""
        
        # Build schema context
        schema_context = ""
        for table_name, info in self.schema_info.items():
            columns = ", ".join([col["name"] for col in info["columns"]])
            schema_context += f"Table: {table_name}\nColumns: {columns}\n\n"
        
        # Build entity filters
        filters = {}
        if entities:
            for entity in entities:
                entity_type = entity.get("type", "")
                entity_value = entity.get("value", "")
                if entity_type in ["color", "fabric", "category", "occasion"]:
                    filters[entity_type] = entity_value
        
        # Try OpenAI first
        try:
            prompt = f"""You are a SQL expert for a dress fashion chatbot. 

Schema:
{schema_context}

User Query: {query}

Entities detected:
{json.dumps(filters, indent=2) if filters else "None"}

Generate a valid PostgreSQL SELECT query that answers the user's question.
IMPORTANT: Always start the query with "SELECT" keyword (uppercase).
Return ONLY the SQL query, no explanations.

CRITICAL RULES:
1. Always use "SELECT" at the start (not "COUNT")
2. Use ILIKE with wildcards (%) for ALL text matching - this is case-insensitive
3. For category searches like "dresses", use: category ILIKE '%dress%'
4. For color searches like "blue", use: color ILIKE '%blue%'
5. For "show me [color] dresses", search BOTH color AND category
6. Use LIMIT 10 unless specified otherwise
7. For counts, use: SELECT COUNT(*) FROM table
8. Return only SELECT queries (no INSERT/UPDATE/DELETE)
9. Use proper table and column names from the schema

Examples:
- "blue dresses" -> SELECT * FROM products WHERE category ILIKE '%dress%' AND color ILIKE '%blue%'
- "red dress" -> SELECT * FROM products WHERE category ILIKE '%dress%' AND color ILIKE '%red%'
- "formal wear" -> SELECT * FROM products WHERE occasion ILIKE '%formal%'
- "silk fabric" -> SELECT * FROM products WHERE fabric_type ILIKE '%silk%'

SQL Query:"""

            response = await openai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a SQL expert. Return ONLY the SQL query.",
                max_tokens=200
            )
            
            sql = response.text.strip()
            
            # Clean up any markdown formatting
            if sql.startswith("```sql"):
                sql = sql[7:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            
            sql = sql.strip()
            
            logger.info(f"Generated SQL (OpenAI): {sql}")
            return sql
            
        except Exception as e:
            logger.warning(f"OpenAI SQL generation failed, using rule-based fallback: {e}")
            
            # Fallback to rule-based SQL generation
            return self._generate_sql_fallback(query, filters)
    
    def _generate_sql_fallback(self, query: str, filters: Dict) -> str:
        """Generate SQL using simple rules when OpenAI is unavailable."""
        query_lower = query.lower()
        
        # Check for count queries
        if "count" in query_lower or "how many" in query_lower:
            return "SELECT COUNT(*) FROM products"
        
        # Check for price range queries
        if "under" in query_lower or "less than" in query_lower:
            import re
            match = re.search(r'under\s+\$?(\d+)', query_lower)
            if match:
                max_price = match.group(1)
                return f"SELECT * FROM products WHERE price <= {max_price} LIMIT 10"
            
            match = re.search(r'less than\s+\$?(\d+)', query_lower)
            if match:
                max_price = match.group(1)
                return f"SELECT * FROM products WHERE price <= {max_price} LIMIT 10"
        
        # Check for minimum price queries
        if "over" in query_lower or "more than" in query_lower:
            import re
            match = re.search(r'over\s+\$?(\d+)', query_lower)
            if match:
                min_price = match.group(1)
                return f"SELECT * FROM products WHERE price >= {min_price} LIMIT 10"
        
        # Check for color filter
        color = filters.get("color") or self._extract_color(query_lower)
        if color:
            return f"SELECT * FROM products WHERE color ILIKE '%{color}%' LIMIT 10"
        
        # Check for category filter
        category = filters.get("category")
        if category:
            return f"SELECT * FROM products WHERE category ILIKE '%{category}%' LIMIT 10"
        
        # Check for fabric filter
        fabric = filters.get("fabric") or self._extract_fabric(query_lower)
        if fabric:
            return f"SELECT * FROM products WHERE fabric_type ILIKE '%{fabric}%' LIMIT 10"
        
        # Check for occasion filter
        occasion = filters.get("occasion")
        if occasion:
            return f"SELECT * FROM products WHERE occasion ILIKE '%{occasion}%' LIMIT 10"
        
        # Default: return all products
        if "all" in query_lower or "show" in query_lower or "list" in query_lower:
            return "SELECT * FROM products LIMIT 10"
        
        # Generic search
        return "SELECT * FROM products LIMIT 10"
    
    def _extract_color(self, query: str) -> Optional[str]:
        """Extract color from query."""
        colors = ["red", "blue", "green", "yellow", "black", "white", "pink", "purple", "orange", "brown", "gray", "grey"]
        for color in colors:
            if color in query:
                return color
        return None
    
    def _extract_fabric(self, query: str) -> Optional[str]:
        """Extract fabric type from query."""
        fabrics = ["cotton", "silk", "rayon", "linen", "wool", "polyester", "chiffon", "velvet", "denim", "satin"]
        for fabric in fabrics:
            if fabric in query:
                return fabric
        return None
    
    async def _execute_sql(self, sql: str) -> QueryResult:
        """Execute SQL query against PostgreSQL database."""
        if not self.pool:
            raise Exception("Database not initialized")
        
        sql_lower = sql.lower().strip()
        
        # Check if it's a valid query type - check if ANY allowed pattern appears
        allowed_patterns = ["select", "count", "sum", "avg", "min", "max"]
        if not any(pattern in sql_lower for pattern in allowed_patterns):
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                sql_query=sql
            )
        
        try:
            async with self.pool.acquire() as conn:
                # Execute query
                result = await conn.fetch(sql)
                
                if not result:
                    return QueryResult(
                        columns=[],
                        rows=[],
                        row_count=0,
                        sql_query=sql
                    )
                
                # Get column names
                columns = list(result[0].keys())
                
                # Get rows as dictionaries
                rows = []
                for row in result:
                    row_dict = {}
                    for key, value in row.items():
                        if hasattr(value, 'isoformat'):
                            row_dict[key] = value.isoformat()
                        elif isinstance(value, list):
                            row_dict[key] = str(value)
                        else:
                            row_dict[key] = value
                    rows.append(row_dict)
                
                return QueryResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                    sql_query=sql
                )
                
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                sql_query=sql
            )
    
    def _extract_intent(self, query: str) -> str:
        """Extract SQL intent from query."""
        query_lower = query.lower()
        
        if "count" in query_lower or "how many" in query_lower:
            return "count"
        elif "list" in query_lower or "show" in query_lower or "find" in query_lower:
            return "select"
        elif "average" in query_lower:
            return "aggregate"
        elif "total" in query_lower or "sum" in query_lower:
            return "aggregate"
        else:
            return "select"
    
    def validate_query(self, sql: str) -> Dict[str, Any]:
        """Validate a SQL query for security and syntax."""
        sql_lower = sql.lower().strip()
        
        # Allow SELECT queries and aggregate queries (COUNT, SUM, AVG, MIN, MAX)
        # Check if ANY allowed pattern appears in the SQL (not just at start)
        allowed_patterns = ["select", "count", "sum", "avg", "min", "max"]
        if not any(pattern in sql_lower for pattern in allowed_patterns):
            return {
                "valid": False,
                "error": "Only SELECT queries and aggregate functions (COUNT, SUM, AVG, MIN, MAX) are allowed",
                "warnings": []
            }
        
        # Check for dangerous keywords
        dangerous = ["drop", "truncate", "delete", "insert", "update", "alter", "create", "grant", "revoke"]
        for keyword in dangerous:
            if keyword in sql_lower:
                return {
                    "valid": False,
                    "error": f"Dangerous keyword '{keyword}' not allowed",
                    "warnings": []
                }
        
        # Check for semicolons (multiple statements)
        if ";" in sql and sql.count(";") > 1:
            return {
                "valid": False,
                "error": "Multiple statements not allowed",
                "warnings": []
            }
        
        return {
            "valid": True,
            "sql": sql,
            "warnings": []
        }
    
    async def get_products(
        self,
        category: Optional[str] = None,
        color: Optional[str] = None,
        fabric: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        occasion: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get products with filters."""
        if self._use_mock:
            return {
                "results": [
                    {"id": 1, "name": "Blue Cotton Summer Dress", "category": "summer_dress", "price": 79.99, "color": "blue"},
                    {"id": 2, "name": "Yellow Rayon Summer Suit", "category": "summer_suit", "price": 69.99, "color": "yellow"}
                ],
                "row_count": 2
            }
        
        try:
            if not self._initialized:
                await self.initialize()
            
            conditions = ["1=1"]
            params = {}
            
            if category:
                conditions.append("category ILIKE :category")
                params["category"] = f"%{category}%"
            
            if color:
                conditions.append("color ILIKE :color")
                params["color"] = f"%{color}%"
            
            if min_price is not None:
                conditions.append("price >= :min_price")
                params["min_price"] = min_price
            
            if max_price is not None:
                conditions.append("price <= :max_price")
                params["max_price"] = max_price
            
            sql = f"""
                SELECT id, name, category, description, fabric_type, color, price, occasion, availability
                FROM products
                WHERE {' AND '.join(conditions)}
                AND availability = TRUE
                ORDER BY price ASC
                LIMIT :limit
            """
            params["limit"] = limit
            
            async with self.pool.acquire() as conn:
                result = await conn.fetch(sql, **params)
                
                rows = [dict(row) for row in result]
                
                return {
                    "results": rows,
                    "row_count": len(rows)
                }
                
        except Exception as e:
            logger.error(f"Get products error: {e}")
            return {"error": str(e), "results": [], "row_count": 0}
    
    async def get_product_count(self, category: Optional[str] = None) -> int:
        """Get product count."""
        if self._use_mock:
            return 10
        
        try:
            if not self._initialized:
                await self.initialize()
            
            sql = "SELECT COUNT(*) as count FROM products"
            params = {}
            
            if category:
                sql = "SELECT COUNT(*) as count FROM products WHERE category ILIKE :category"
                params["category"] = f"%{category}%"
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(sql, **params)
                return result["count"]
                
        except Exception as e:
            logger.error(f"Get product count error: {e}")
            return 0
    
    async def get_inventory_status(self) -> Dict[str, Any]:
        """Get inventory status summary."""
        if self._use_mock:
            return {
                "total_products": 10,
                "by_category": [
                    {"category": "summer_dress", "count": 3},
                    {"category": "evening_gown", "count": 2}
                ],
                "by_price_range": [
                    {"range": "Budget (<$50)", "count": 2},
                    {"range": "Mid-range ($50-$100)", "count": 4}
                ]
            }
        
        try:
            if not self._initialized:
                await self.initialize()
            
            async with self.pool.acquire() as conn:
                # Total products
                total = await conn.fetchval("SELECT COUNT(*) FROM products WHERE availability = TRUE")
                
                # By category
                by_category = await conn.fetch("""
                    SELECT category, COUNT(*) as count 
                    FROM products 
                    WHERE availability = TRUE 
                    GROUP BY category 
                    ORDER BY count DESC
                """)
                
                # By price range
                price_ranges = await conn.fetch("""
                    SELECT 
                        CASE 
                            WHEN price < 50 THEN 'Budget (<$50)'
                            WHEN price < 100 THEN 'Mid-range ($50-$100)'
                            WHEN price < 200 THEN 'Premium ($100-$200)'
                            ELSE 'Luxury (>$200)'
                        END as price_range,
                        COUNT(*) as count
                    FROM products 
                    WHERE availability = TRUE 
                    GROUP BY price_range
                """)
                
                return {
                    "total_products": total,
                    "by_category": [{"category": row["category"], "count": row["count"]} for row in by_category],
                    "by_price_range": [{"range": row["price_range"], "count": row["count"]} for row in price_ranges]
                }
                
        except Exception as e:
            logger.error(f"Get inventory status error: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check SQL agent health."""
        return {
            "status": "healthy" if self._initialized else "not initialized",
            "database": "postgresql" if not self._use_mock else "mock",
            "tables_count": len(self.schema_info)
        }
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()


# Export agent instance
sql_agent = SQLAgent()
