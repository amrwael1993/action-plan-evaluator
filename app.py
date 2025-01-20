import streamlit as st

# Evaluation function
def evaluate_action_plan(reasons, measures, deadline, responsibility):
    root_cause_score = 0
    action_plan_score = 0
    comments = ""

    # Evaluate Reasons (Root Cause Analysis)
    if "why" in reasons.lower():
        root_cause_score += 2
    else:
        comments += "Root Cause: Missing systematic approach. "
    if "FIFO" in reasons.upper():
        root_cause_score += 2
    else:
        comments += "Root Cause: Not linked to findings. "
    if len(reasons.split()) > 10:
        root_cause_score += 1
    else:
        comments += "Root Cause: Insufficient depth in analysis. "

    # Evaluate Measures (Action Plan)
    if "implementation" in measures.lower():
        action_plan_score += 2
    else:
        comments += "Action Plan: Missing implementation details. "
    if deadline:
        action_plan_score += 1
    else:
        comments += "Action Plan: No timeline provided. "
    if responsibility:
        action_plan_score += 1
    else:
        comments += "Action Plan: No responsibility assigned. "

    return {
        "Root Cause Score": min(root_cause_score, 5),
        "Action Plan Score": min(action_plan_score, 5),
        "Comments": comments
    }

# Streamlit App
st.title("Action Plan Evaluator")
st.write("Enter the details of the action plan below for evaluation.")

# Input fields
reasons = st.text_area("Reasons (Root Cause Analysis)", height=100)
measures = st.text_area("Measures (Action Plan)", height=100)
deadline = st.text_input("Deadline")
responsibility = st.text_input("Responsibility")

if st.button("Evaluate"):
    # Evaluate and display results
    results = evaluate_action_plan(reasons, measures, deadline, responsibility)
    st.subheader("Evaluation Results")
    st.write(f"**Root Cause Score:** {results['Root Cause Score']}/5")
    st.write(f"**Action Plan Score:** {results['Action Plan Score']}/5")
    st.write(f"**Comments:** {results['Comments']}")
