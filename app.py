import streamlit as st
import pandas as pd
import io

# Evaluation function with improved logic
def evaluate_action_plan(reasons, measures, deadline, responsibility):
    # Initialize scores and comments
    root_cause_criteria = {
        "Systematic and Understandable": 0,
        "Linked to Findings": 0,
        "Depth of Analysis": 0
    }
    action_plan_criteria = {
        "Specificity and Clarity": 0,
        "Linked to Root Cause": 0,
        "Timeline and Responsibility": 0,
        "Criticality Match": 0
    }
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
    if len(measures.split()) > 5:
        action_plan_criteria["Specificity and Clarity"] = 2
    else:
        comments += "Action Plan: Actions lack sufficient detail. "

    if "prevent" in measures.lower() or "address" in measures.lower() or "eliminate" in measures.lower():
        action_plan_criteria["Linked to Root Cause"] = 2
    elif len(reasons) > 0 and len(measures) > 0:
        action_plan_criteria["Linked to Root Cause"] = 1
        comments += "Action Plan: Actions partially address the root cause. "
    else:
        comments += "Action Plan: Actions do not address the root cause. "

    if deadline and responsibility:
        action_plan_criteria["Timeline and Responsibility"] = 2
    elif deadline or responsibility:
        action_plan_criteria["Timeline and Responsibility"] = 1
        comments += "Action Plan: Timeline or responsibility is missing. "
    else:
        comments += "Action Plan: Neither timeline nor responsibility is defined. "

    if "critical" in measures.lower() or "priority" in measures.lower():
        action_plan_criteria["Criticality Match"] = 1
    else:
        comments += "Action Plan: Actions may not match the criticality of the finding. "

    # Calculate Total Scores
    root_cause_score = sum(root_cause_criteria.values())
    action_plan_score = sum(action_plan_criteria.values())

    return {
        "Root Cause Score": min(root_cause_score, 5),
        "Root Cause Breakdown": root_cause_criteria,
        "Action Plan Score": min(action_plan_score, 5),
        "Action Plan Breakdown": action_plan_criteria,
        "Comments": comments
    }

# Streamlit App
st.title("Action Plan Evaluator")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Optimize memory usage for large files
    df = pd.read_excel(uploaded_file, skip_blank_lines=True)

    # Display uploaded data
    st.subheader("Uploaded Data")
    st.write(df)

    # Ensure the "Findings" column exists
    if "Findings" in df.columns:
        df = df[df["Findings"].notna()]  # Filter rows with non-empty Findings
        if not df.empty:
            evaluation_results = []

            # Process each row
            for index, row in df.iterrows():
                findings = row["Findings"]
                reasons = row["Reasons"]
                measures = row["Measures"]
                deadline = row["Deadline"]
                responsibility = row["Responsibility"]

                # Evaluate each row
                result = evaluate_action_plan(reasons, measures, deadline, responsibility)
                result["Row"] = index + 1
                result["Findings"] = findings
                result["Action"] = measures
                evaluation_results.append(result)

            # Display results
            st.subheader("Evaluation Results")
            for result in evaluation_results:
                st.write(f"**Row {result['Row']}**")
                st.write(f"**Findings:** {result['Findings']}")
                st.write(f"**Action:** {result['Action']}")
                st.write(f"**Root Cause Score:** {result['Root Cause Score']}/5")
                st.write(f"**Action Plan Score:** {result['Action Plan Score']}/5")
                st.write("**Comments:**", result["Comments"])
                st.write("---")

            # Export results to Excel
            output = io.BytesIO()
            export_df = pd.DataFrame(evaluation_results)
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Evaluation Results")
            output.seek(0)

            st.download_button(
                label="Download Results as Excel",
                data=output,
                file_name="evaluation_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No valid rows found after filtering.")
    else:
        st.error("The column 'Findings' is missing in the uploaded file. Please check the file format.")
