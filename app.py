import streamlit as st
import pandas as pd
import io
import os

# Create a file to store feedback
if not os.path.exists("feedback.csv"):
    pd.DataFrame(columns=["Findings", "Action", "Root Cause Score", "Adjusted Root Cause Score", 
                          "Action Plan Score", "Adjusted Action Plan Score", 
                          "Root Cause Feedback", "Action Plan Feedback"]).to_csv("feedback.csv", index=False)

# Evaluation function
def evaluate_action_plan(reasons, measures, deadline, responsibility):
    root_cause_criteria = {"Systematic and Understandable": 0, "Linked to Findings": 0, "Depth of Analysis": 0}
    action_plan_criteria = {"Specificity and Clarity": 0, "Linked to Root Cause": 0, "Timeline and Responsibility": 0}
    comments = ""

    # Root Cause Evaluation
    if "why" in reasons.lower():
        root_cause_criteria["Systematic and Understandable"] = 2
    else:
        comments += "Root Cause: Missing systematic approach. "

    if "FIFO" in reasons.upper():
        root_cause_criteria["Linked to Findings"] = 2
    else:
        comments += "Root Cause: Not linked to findings. "

    if len(reasons.split()) > 10:
        root_cause_criteria["Depth of Analysis"] = 1
    else:
        comments += "Root Cause: Insufficient depth in analysis. "

    # Action Plan Evaluation
    if measures and len(measures) > 10:
        action_plan_criteria["Specificity and Clarity"] = 2
    else:
        comments += "Action Plan: Missing details or clarity. "

    if deadline:
        action_plan_criteria["Timeline and Responsibility"] += 1
    else:
        comments += "Action Plan: No timeline provided. "

    if responsibility:
        action_plan_criteria["Timeline and Responsibility"] += 1
    else:
        comments += "Action Plan: No responsibility assigned. "

    # Calculate Total Scores
    root_cause_score = sum(root_cause_criteria.values())
    action_plan_score = sum(action_plan_criteria.values())

    return {
        "Root Cause Score": min(root_cause_score, 5),
        "Root Cause Breakdown": root_cause_criteria,
        "Action Plan Score": min(action_plan_score, 5),
        "Action Plan Breakdown": action_plan_criteria,
        "Comments": comments,
    }

# Streamlit App
st.title("Action Plan Evaluator")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    full_data = pd.read_excel(uploaded_file, header=None)

    # Detect header row dynamically
    header_row = None
    for i, row in full_data.iterrows():
        if any("Reasons" in str(cell) for cell in row):
            header_row = i
            break

    if header_row is not None:
        df = pd.read_excel(uploaded_file, skiprows=header_row)

        # Ensure necessary columns are present
        if "Findings" in df.columns:
            df = df[df["Findings"].notna()]
            st.write("Uploaded Data", df)

            evaluation_results = []
            for index, row in df.iterrows():
                findings = row["Findings"]
                reasons = row["Reasons"]
                measures = row["Measures"]
                deadline = row["Deadline"]
                responsibility = row["Responsibility"]

                result = evaluate_action_plan(reasons, measures, deadline, responsibility)
                result["Row"] = index + 1
                result["Findings"] = findings
                result["Action"] = measures
                evaluation_results.append(result)

            st.subheader("Evaluation Results")
            for result in evaluation_results:
                st.write(f"**Row {result['Row']}**")
                st.write(f"Findings: {result['Findings']}")
                st.write(f"Action: {result['Action']}")
                st.write(f"Root Cause Score: {result['Root Cause Score']}/5")
                st.write(f"Action Plan Score: {result['Action Plan Score']}/5")
                st.write(f"Comments: {result['Comments']}")

                # Display criteria breakdown
                st.write("**Root Cause Evaluation Criteria (Met/Unmet):**")
                for criterion, score in result["Root Cause Breakdown"].items():
                    status = "Met" if score > 0 else "Unmet"
                    st.write(f"- {criterion}: {status}")

                st.write("**Action Plan Evaluation Criteria (Met/Unmet):**")
                for criterion, score in result["Action Plan Breakdown"].items():
                    status = "Met" if score > 0 else "Unmet"
                    st.write(f"- {criterion}: {status}")

                # Collect feedback for root cause
                root_cause_feedback = st.text_area(f"Root Cause Feedback for Row {result['Row']}", "")
                adjusted_root_cause_score = st.slider(f"Adjusted Root Cause Score for Row {result['Row']}", 0, 5, int(result["Root Cause Score"]))

                # Collect feedback for action plan
                action_plan_feedback = st.text_area(f"Action Plan Feedback for Row {result['Row']}", "")
                adjusted_action_plan_score = st.slider(f"Adjusted Action Plan Score for Row {result['Row']}", 0, 5, int(result["Action Plan Score"]))

                if st.button(f"Submit Feedback for Row {result['Row']}"):
                    feedback_data = {
                        "Findings": result["Findings"],
                        "Action": result["Action"],
                        "Root Cause Score": result["Root Cause Score"],
                        "Adjusted Root Cause Score": adjusted_root_cause_score,
                        "Action Plan Score": result["Action Plan Score"],
                        "Adjusted Action Plan Score": adjusted_action_plan_score,
                        "Root Cause Feedback": root_cause_feedback,
                        "Action Plan Feedback": action_plan_feedback,
                    }
                    feedback_df = pd.DataFrame([feedback_data])
                    feedback_df.to_csv("feedback.csv", mode="a", header=False, index=False)
                    st.success(f"Feedback for Row {result['Row']} saved!")

            # Export results
            export_df = pd.DataFrame(evaluation_results)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Evaluation Results")
            st.download_button(
                label="Download Results",
                data=output.getvalue(),
                file_name="evaluation_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
