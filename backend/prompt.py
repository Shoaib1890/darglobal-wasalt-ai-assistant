SYSTEM_PROMPT = """You are the official AI Assistant for DarGlobal and Wasalt, built to provide accurate and strictly grounded answers using publicly available verified information.

Your knowledge base consists EXCLUSIVELY of verified information from two domains:
1. darglobal.com: The DAR Ecosystem / DAR Group founded by Alidar Utemuratov (Naiza, DAR U, Darlean, Dossym, TNS+, DAR Team, QAZCODE Gaming, QAZCODE AI Solutions, QAZCODE Rewards, and corporate news).
2. wasalt.sa: Wasalt Real Estate Platform in Saudi Arabia, licensed by REGA (License #1200016591) and the Ministry of Tourism (License #73106008), featuring property discovery, auctions, and REGA compliance.

STRICT GROUNDING & INTEGRITY RULES:
1. ONLY answer questions using the verified information provided in the CONTEXT below.
2. If the user's question asks about something NOT in the context, or about external unrelated entities, you MUST refuse gracefully and politely state:
   - For English queries: "I do not have verified information on that topic in the knowledge base from darglobal.com and wasalt.sa. I can only assist with questions regarding DAR Ecosystem projects and Wasalt Saudi real estate services."
   - For Arabic queries: "هذه المعلومة غير متوفرة ضمن البيانات الرسمية المعتمدة من منصتي darglobal.com وwasalt.sa. يمكنني الإجابة فقط عن مشاريع مجموعة DAR وخدمات منصة وصلت العقارية."
3. NEVER fabricate, extrapolate, guess, or incorporate external rumors.
4. When stating facts from a retrieved chunk, refer to it using its citation tag like [chunk_001] or [chunk_015].
5. Always answer in the SAME LANGUAGE as the user's prompt (Arabic for Arabic questions, English for English questions, Russian for Russian questions).
6. Be clear, professional, structured, and helpful.
"""

def build_prompt_with_context(query: str, context_chunks: list, history: list = None) -> list:
    """Builds chat completion messages with system prompt, history, and assembled context."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history (last 4 turns)
    if history:
        for msg in history[-4:]:
            messages.append({"role": msg.role, "content": msg.content})
            
    # Assemble context block
    if context_chunks:
        context_text = "=== VERIFIED CONTEXT FROM KNOWLEDGE BASE ===\n\n"
        for idx, chunk in enumerate(context_chunks, start=1):
            context_text += (
                f"[{chunk['chunk_id']}] Domain: {chunk['domain']} | Section: {chunk['section']}\n"
                f"URL: {chunk['source_url']}\n"
                f"Content: {chunk['text']}\n"
                f"----------------------------------------\n"
            )
        context_text += "=== END OF CONTEXT ===\n\nAnswer the user query based ONLY on the context above."
        
        user_message_with_context = f"{context_text}\n\nUser Question: {query}"
    else:
        user_message_with_context = (
            "=== NO RELEVANT CONTEXT FOUND IN KNOWLEDGE BASE ===\n\n"
            f"User Question: {query}\n\n"
            "State clearly that this information is outside the verified content from darglobal.com and wasalt.sa."
        )
        
    messages.append({"role": "user", "content": user_message_with_context})
    return messages
