import os
import streamlit as st
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Pydantic Schema
class BillItem(BaseModel):
    item_name: str = Field(description="Name of the food or drink item")
    quantity: int = Field(description="Quantity ordered", default=1)
    price: float = Field(description="Total price for this line item")

class ExtractedBill(BaseModel):
    items: list[BillItem]
    subtotal: float
    tax: float = Field(description="Total GST or tax amount", default=0.0)
    service_charge: float = Field(description="Service charge or tips", default=0.0)
    discounts: float = Field(description="Total discount applied", default=0.0)
    printed_total: float = Field(description="Grand total displayed on paper")

# 2. Vision API Processing
def analyze_receipt(image: Image.Image) -> ExtractedBill:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY environment variable is missing!")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    prompt = (
        "Extract line items, quantity, prices, subtotal, tax, "
        "service charges, discounts, and total from this bill image. "
        "Set missing numeric values to 0.0."
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedBill,
        ),
    )
    return response.parsed

# 3. Proportional Split Math
def calculate_splits(bill: ExtractedBill, assignments: dict, people: list):
    person_subtotals = {p: 0.0 for p in people}
    
    for idx, item in enumerate(bill.items):
        assigned = assignments.get(idx, [])
        if assigned:
            split_amount = item.price / len(assigned)
            for p in assigned:
                person_subtotals[p] += split_amount

    net_extras = bill.tax + bill.service_charge - bill.discounts
    calculated_subtotal = sum(item.price for item in bill.items)
    
    breakdown = {}
    for p in people:
        p_sub = person_subtotals[p]
        ratio = (p_sub / calculated_subtotal) if calculated_subtotal > 0 else 0
        p_extra = net_extras * ratio
        breakdown[p] = {
            "subtotal": round(p_sub, 2),
            "extra_fees": round(p_extra, 2),
            "final_total": round(p_sub + p_extra, 2)
        }
    return breakdown, round(calculated_subtotal, 2)

# 4. Streamlit UI
st.set_page_config(page_title="Smart Bill Splitter", layout="wide")
st.title("🧾 Smart Receipt & Bill Splitter")

uploaded_file = st.sidebar.file_uploader("Upload Receipt Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Receipt", use_container_width=True)
    
    if "bill_data" not in st.session_state or st.sidebar.button("Re-analyze"):
        with st.spinner("Extracting data via Gemini..."):
            st.session_state.bill_data = analyze_receipt(image)

    bill = st.session_state.bill_data

    st.subheader("1. Human Verification Screen")
    c1, c2 = st.columns(2)
    with c1:
        bill.subtotal = st.number_input("Subtotal", value=float(bill.subtotal))
        bill.tax = st.number_input("Tax / GST", value=float(bill.tax))
    with c2:
        bill.service_charge = st.number_input("Service Charge", value=float(bill.service_charge))
        bill.printed_total = st.number_input("Printed Total", value=float(bill.printed_total))

    st.subheader("2. Assign Items to People")
    people_input = st.text_input("Enter participant names (comma separated)", "Aarya, Priya, Rahul")
    people = [p.strip() for p in people_input.split(",") if p.strip()]

    assignments = {}
    for idx, item in enumerate(bill.items):
        selected = st.multiselect(
            f"Assign: '{item.item_name}' (₹{item.price})",
            options=people,
            default=people,
            key=f"item_assign_{idx}"
        )
        assignments[idx] = selected

    if st.button("Calculate Final Split"):
        results, calc_subtotal = calculate_splits(bill, assignments, people)
        st.subheader("3. Calculated Results")
        
        for person, vals in results.items():
            st.metric(
                label=f"👤 {person}'s Total Share", 
                value=f"₹{vals['final_total']}", 
                delta=f"Items: ₹{vals['subtotal']} | Fees: ₹{vals['extra_fees']}"
            )