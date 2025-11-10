INTENT_ROUTER_TEMPLATE =  """
                            You are an intent classifier for a library chatbot system.
                            Analyze the user query and classify it into ONE of these intents:
                             User Query: "{query}"
                            1. "sql_query" - Questions about:
                               - Book availability, locations, authors, publishers
                               - Member information, loans, fines, reservations
                               - Library branches, sections, staff
                               - Events, maintenance logs
                               - Any structured data in the database
                            
                            2. "rag_query" - Questions about:
                               - Book content, summaries, themes
                               - Research help from PDF documents
                               - Information within digital assets/archives
                               - Literary analysis or book recommendations based on content
                            
                            3. "general_chat" - Questions about:
                               - Greetings, small talk
                               - Library policies (general)
                               - Opening hours, contact info
                               - General guidance
                            
                            4. "hybrid" - Questions requiring both database info AND document content
                            
                            User Query: {state['user_query']}
                            
                            Respond in JSON as:
                                {{"intent": "<sql_query" | "rag_query" | "general_chat>", "reasoning": "<brief reason>"}}
                            """
DB_SCHEMA = """
            DATABASE SCHEMA:
            
            CHAINS: id, name, headquarters, established_year
            BRANCHES: id, chain_id, name, city, address, phone
            SECTIONS: id, name, branch_id, description
            SHELVES: id, code, section_id, capacity
            
            AUTHORS: id, name, nationality, birth_year, biography
            PUBLISHERS: id, name, country, established
            BOOKS: id, title, isbn, author_id, publisher_id, shelf_id, category, total_copies, available_copies, published_year, language
            
            MEMBERS: id, name, email, membership_type, join_date, is_active
            SESSIONS: id, session_id, ip_address, user_agent, expires_at
            CONVERSATIONS: id, session_id, title, created_at
            CHAT_MESSAGES: id, conversation_id, role, content, intent, created_at
            
            LOANS: id, member_id, book_id, issued_date, due_date, returned_date
            FINES: id, member_id, amount, reason, status, issued_date
            RESERVATIONS: id, member_id, book_id, reserved_date, status
            REVIEWS: id, member_id, book_id, rating, comment, created_at
            
            DIGITAL_ASSETS: id, title, file_path, uploaded_date, description, source_type, embedding_id
            ASSET_TAGS: id, asset_id, tag
            
            STAFF_ROLES: id, name, description
            STAFF: id, name, email, branch_id, role_id
            CHAT_SESSIONS: id, member_id, query, response, source, timestamp
            HITL_REVIEWS: id, chat_session_id, reviewer_id, status, notes, reviewed_at
            
            EVENTS: id, branch_id, title, description, event_date
            MAINTENANCE_LOGS: id, branch_id, equipment, description, status, logged_at
            
            RELATIONSHIPS:
            - Books -> Authors, Publishers, Shelves
            - Loans -> Members, Books
            - Reservations -> Members, Books
            - Reviews -> Members, Books
            - Branches -> Chains
            - Sections -> Branches
            - Shelves -> Sections
            """