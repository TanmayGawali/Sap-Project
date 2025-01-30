import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class StudyScheduleOptimizer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, marks, attendance, importance):
        data = np.column_stack((marks, attendance, importance))
        return self.scaler.fit_transform(data)
    
    def generate_schedule(self, total_hours, marks, attendance, importance):
        # Normalize input values
        marks = np.array(marks) / 100  # Scale marks between 0 and 1
        attendance = np.array(attendance) / 100  # Scale attendance between 0 and 1
        importance = np.array(importance) / 10  # Scale importance between 0 and 1
        
        # Compute weight contributions
        marks_weight = 1 - marks  # Lower marks should get higher priority
        attendance_weight = 1 - attendance  # Lower attendance should get higher priority
        importance_weight = importance  # Higher importance should get higher priority
        
        # Total weight calculation
        total_weights = marks_weight + attendance_weight + importance_weight
        normalized_weights = total_weights / np.sum(total_weights)
        
        # Distribute study hours based on computed weights
        allocated_hours = normalized_weights * total_hours
        
        return np.round(allocated_hours, 1)

def main():
    st.set_page_config(page_title="Study Schedule Generator", page_icon="📚", layout="wide")
    
    # Initialize the optimizer
    optimizer = StudyScheduleOptimizer()
    
    # App title and description
    st.title("📚 Study Schedule Generator")
    st.markdown("Generate your personalized study schedule based on your performance and preferences.")
    
    # Create form
    with st.form("schedule_form"):
        # Basic Information
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Student Name")
            total_hours = st.number_input("Total Available Study Hours", 
                                        min_value=1.0, 
                                        max_value=24.0, 
                                        value=8.0)
        
        with col2:
            num_subjects = st.number_input("Number of Subjects", 
                                         min_value=1, 
                                         max_value=10, 
                                         value=3)
        
        # Subject Details
        st.subheader("Subject Details")
        
        subjects = []
        marks = []
        attendance = []
        importance = []
        
        for i in range(int(num_subjects)):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                subject = st.text_input(f"Subject {i+1}", key=f"subject_{i}")
                subjects.append(subject)
            
            with col2:
                mark = st.number_input(f"Current Marks ({subject if subject else f'Subject {i+1}'})", 
                                     min_value=0.0,
                                     max_value=100.0,
                                     key=f"marks_{i}")
                marks.append(mark)
            
            with col3:
                attend = st.number_input(f"Attendance % ({subject if subject else f'Subject {i+1}'})", 
                                       min_value=0.0,
                                       max_value=100.0,
                                       key=f"attendance_{i}")
                attendance.append(attend)
            
            with col4:
                imp = st.number_input(f"Importance (1-10) ({subject if subject else f'Subject {i+1}'})", 
                                    min_value=1,
                                    max_value=10,
                                    key=f"importance_{i}")
                importance.append(imp)
        
        submitted = st.form_submit_button("Generate Schedule")
    
    if submitted:
        try:
            # Validate inputs
            if not all(subjects):
                st.error("Please enter names for all subjects.")
                return
                
            # Generate schedule
            hours = optimizer.generate_schedule(
                total_hours,
                marks,
                attendance,
                importance
            )
            
            # Create results DataFrame
            results_df = pd.DataFrame({
                'Subject': subjects,
                'Current Marks': marks,
                'Attendance (%)': attendance,
                'Importance': importance,
                'Recommended Hours': hours
            })
            
            # Display results
            st.success("Schedule generated successfully!")
            
            # Display student info
            st.subheader("📋 Schedule Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"Student: {name}\nTotal Study Hours: {total_hours} hours")
                st.dataframe(results_df, use_container_width=True)
            
            with col2:
                st.subheader("📊 Time Distribution")
                st.bar_chart(results_df.set_index('Subject')['Recommended Hours'])
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please ensure all fields are filled correctly.")

if __name__ == "__main__":
    main()
