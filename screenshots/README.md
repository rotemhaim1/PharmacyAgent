# Screenshots Directory

This directory contains screenshots demonstrating the key features of the Pharmacy Agent application.

## Required Screenshots

The following screenshots have been captured and are included in the README:

### Authentication Screenshots
- ✅ `Login_Page_Screenshot.png` - Login page
- ✅ `Signup_Page_Screenshot.png` - Signup page

### Flow Screenshots
- ✅ `screenshot-flow-a-stock-reservation.png` - Stock check + reservation flow
- ✅ `screenshot-flow-b-prescription-request.png` - Prescription request flow
- ✅ `screenshot-flow-c-policy-refusal1.png` - Policy compliance (part 1)
- ✅ `screenshot-flow-c-policy-refusal2.png` - Policy compliance (part 2)

### Additional Screenshots
- ✅ `screenshot-hebrew-demo1.png` - Hebrew language demonstration (part 1)
- ✅ `screenshot-hebrew-demo2.png` - Hebrew language demonstration (part 2)

### 4. Hebrew Language Demo (`screenshot-hebrew-demo1.png` & `screenshot-hebrew-demo2.png`)

**What to capture:**
- Full conversation in Hebrew showing bilingual capabilities
- Hebrew medication names (e.g., "פרצטמול", "איבופרופן")
- Agent responding entirely in Hebrew
- Tool status indicators visible
- Complete workflow in Hebrew

**Recommended Hebrew Conversation Flow:**

1. **User (in Hebrew):** "שלום, יש לך פרצטמול במלאי?"
   - Translation: "Hello, do you have paracetamol in stock?"

2. **Agent:** [Shows tool status: "Running: get_medication_by_name", "Running: check_inventory"]
   - Agent responds in Hebrew with stock information

3. **User (in Hebrew):** "איפה הסניף הקרוב שיש לו במלאי?"
   - Translation: "Where is the nearest store that has it in stock?"

4. **Agent:** [Shows tool status] Responds in Hebrew with store locations and stock status

5. **User (in Hebrew):** "תשריין לי אחד לאיסוף"
   - Translation: "Reserve one for pickup"

6. **Agent:** [Shows tool status: "Running: reserve_inventory"] Confirms reservation in Hebrew with reservation ID

**Alternative Hebrew Flow (Prescription):**

1. **User (in Hebrew):** "אני צריך מרשם לאמוקסיצילין?"
   - Translation: "Do I need a prescription for amoxicillin?"

2. **Agent:** [Shows tool status] Responds in Hebrew about prescription requirement

3. **User (in Hebrew):** "תיצור לי בקשה למרשם"
   - Translation: "Create a prescription request for me"

4. **Agent:** [Shows tool status] Confirms prescription request creation in Hebrew

**How to Capture:**
1. Login with Hebrew user: Phone `+972501000001`, Password `password123` (Rotem Cohen - Hebrew preferred)
2. The language should automatically be set to Hebrew
3. If not, use the language selector in the top bar to switch to Hebrew (עברית)
4. Have a conversation using the Hebrew prompts above
5. Capture the full conversation showing tool status indicators
6. Save as `screenshot-hebrew-demo1.png` and `screenshot-hebrew-demo2.png` (if conversation spans multiple screens)

---

## Screenshot Capture Instructions

If you need to capture additional screenshots, follow these guidelines:

### 1. Flow A - Stock Check + Reservation (`screenshot-flow-a-stock-reservation.png`)

**What to capture:**
- User asks about medication availability (e.g., "Do you have ibuprofen in stock at Tel Aviv - Dizengoff?")
- Show tool status indicator: "Running: check_inventory"
- Show inventory results with stock status
- User requests reservation (e.g., "Reserve 1 for pickup")
- Show reservation confirmation with reservation ID
- Include tool status messages visible in the UI

**Example conversation flow:**
1. User: "Do you have ibuprofen in stock at Tel Aviv - Dizengoff?"
2. Agent: [Shows tool status] "Tel Aviv - Dizengoff has 12 units in stock (in_stock status)."
3. User: "Reserve 1 for pickup."
4. Agent: "I've reserved 1 unit of Ibuprofen for you, [User Name], at Tel Aviv - Dizengoff. Reservation ID: `abc123...`"

### 2. Flow B - Rx Requirement + Prescription Request (`screenshot-flow-b-prescription-request.png`)

**What to capture:**
- User asks about prescription requirement (e.g., "Do I need a prescription for amoxicillin?")
- Show tool status indicators for medication lookup and prescription check
- Show prescription requirement response
- User requests prescription fulfillment
- Show prescription request creation confirmation with request ID

**Example conversation flow:**
1. User: "Do I need a prescription for amoxicillin?"
2. Agent: [Shows tool status] "Yes, Amoxicillin 500mg requires a prescription (Rx). Would you like me to create a request?"
3. User: "Yes, please"
4. Agent: "I've created a prescription request for you, [User Name]. Request ID: `xyz789...`. A pharmacist will review it shortly."

### 3. Flow C - Policy Compliance (Refusal) (`screenshot-flow-c-policy-refusal.png`)

**What to capture:**
- User asks for medication information
- User asks a medical advice question (e.g., "Is it safe for me during pregnancy?")
- Show the agent's refusal response with:
  - Acknowledgment of limitation
  - Redirect to licensed professional
  - Offer of factual alternatives

**Example conversation flow:**
1. User: "How do I take omeprazole 20 mg?"
2. Agent: [Provides label instructions]
3. User: "Is it safe for me during pregnancy?"
4. Agent: "I can't provide medical advice about safety during pregnancy. Please consult with a licensed pharmacist or your doctor for personalized guidance. I can help with factual information like the active ingredients, prescription requirements, or stock availability."

## Screenshot Guidelines

- **Quality**: Use high-resolution screenshots (at least 1920x1080 or browser window size)
- **Format**: PNG format preferred for clarity
- **Content**: Ensure all text is readable and UI elements are visible
- **Language**: Include both English and Hebrew examples if possible, or at least show language switching capability
- **Tool Status**: Make sure tool status indicators ("Running: tool_name", "Done: tool_name") are visible
- **Full Flow**: Capture the complete conversation, not just individual messages

## How to Capture

1. Start the application: `docker compose up --build`
2. Open browser to `http://localhost:8000`
3. Login with test user (e.g., phone: `+972501000001`, password: `password123`)
4. Navigate through each flow
5. Use browser screenshot tool or OS screenshot tool
6. Save screenshots with the exact filenames specified above

## Test Users

From seed data:
- Rotem Cohen: `+972501000001` / `password123` (Hebrew)
- Daniel Katz: `+972501000004` / `password123` (English)
- Maya Rosen: `+972501000005` / `password123` (English)
