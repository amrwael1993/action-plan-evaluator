import streamlit as st
import pandas as pd
import io

# Evaluation function
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
        "Timeline and Responsibility": 0
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
    if "implementation" in measures.lower():
        action_plan_criteria["Specificity and Clarity"] = 2
    else:
        comments += "Action Plan: Missing implementation details. "

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
        "Comments": comments
    }

# Streamlit App
st.title("Action Plan Evaluator")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the entire sheet without skipping rows
    full_data = pd.read_excel(uploaded_file, header=None)

    # Dynamically detect the header row based on column names
    header_row = None
    for i, row in full_data.iterrows():
        if any("Reasons" in str(cell) for cell in row):
            header_row = i
            break

    if header_row is not None:
        # Load the actual data starting from the detected header row
        df = pd.read_excel(uploaded_file, skiprows=header_row)

        # Display the uploaded data
        st.subheader("Uploaded Data")
        st.write(df)

        # Ensure the "Findings" column exists
        if "Findings" in df.columns:
            # Filter rows where "Findings" is not empty
            df = df[df["Findings"].notna()]
        else:
            st.error("The column 'Findings' is missing in the uploaded file. Please check the file format.")
            st.stop()

        if not df.empty:
            # Initialize results list
            evaluation_results = []

            # Loop through each row in the DataFrame
            for index, row in df.iterrows():
                # Extract data from each row
                findings = row["Findings"]
                reasons = row["Reasons"]
                measures = row["Measures"]
                deadline = row["Deadline"]
                responsibility = row["Responsibility"]

                # Evaluate the action plan for this row
                result = evaluate_action_plan(reasons, measures, deadline, responsibility)
                result["Row"] = index + 1  # Add row number for reference
                result["Findings"] = findings  # Include Findings in the result
                evaluation_results.append(result)

            # Display the evaluation results for each row
            st.subheader("Evaluation Results")
            for result in evaluation_results:
                st.write(f"**Row {result['Row']}**")
                st.write(f"**Findings:** {result['Findings']}")
                st.write(f"**Root Cause Score:** {result['Root Cause Score']}/5")
                st.write(f"**Action Plan Score:** {result['Action Plan Score']}/5")

                # Display criteria breakdown for Root Cause
                st.write("**Root Cause Evaluation Criteria**")
                for criterion, score in result["Root Cause Breakdown"].items():
                    st.write(f"{criterion}: {score}/2")

                # Display criteria breakdown for Action Plan
                st.write("**Action Plan Evaluation Criteria**")
                for criterion, score in result["Action Plan Breakdown"].items():
                    st.write(f"{criterion}: {score}/2")

                # Display comments
                st.write(f"**Comments:** {result['Comments']}")
                st.write("---")  # Separator for each row

            # Export evaluation results to Excel
            export_data = []
            for result in evaluation_results:
                export_data.append({
                    "Row": result["Row"],
                    "Findings": result["Findings"],  # Add Findings to export
                    "Root Cause Score": result["Root Cause Score"],
                    "Action Plan Score": result["Action Plan Score"],
                    "Comments": result["Comments"]
                })
            export_df = pd.DataFrame(export_data)

            # Save the DataFrame to an Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Evaluation Results")
            output.seek(0)

            # Add a download button
            st.download_button(
                label="Download Results as Excel",
                data=output,
                file_name="evaluation_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data found after filtering for non-empty 'Findings' rows.")
    else:
        st.error("Could not detect the header row. Please check your file format.")
        st.stop()

# Input fields for manual testing
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

    # Display Overall Scores
    st.write(f"**Root Cause Score:** {results['Root Cause Score']}/5")
    st.write(f"**Action Plan Score:** {results['Action Plan Score']}/5")

    # Display Detailed Criteria
    st.subheader("Root Cause Evaluation Criteria")
    for criterion, score in results["Root Cause Breakdown"].items():
        st.write(f"{criterion}: {score}/2")

    st.subheader("Action Plan Evaluation Criteria")
    for criterion, score in results["Action Plan Breakdown"].items():
        st.write(f"{criterion}: {score}/2")

    # Display Comments
    st.subheader("Comments")
    st.write(results["Comments"])
