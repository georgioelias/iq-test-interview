import streamlit as st
import random
import os
import json
from PIL import Image
import base64

# Set page configuration
st.set_page_config(page_title="Quiz Application", layout="centered")

# Add custom CSS for fixed image sizes
st.markdown("""
<style>
.question-container {
    display: flex;
    justify-content: center;
    width: 100%;
    margin: 0 auto;
}

.question-img-container {
    width: 800px;
    height: 500px;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f8f9fa;
    margin: 0 auto;
}

.question-img-container img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.answer-img-container {
    width: 180px;
    height: 150px;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f8f9fa;
    margin-bottom: 10px;
    margin-right: 10px;
}

.answer-img-container img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}
</style>
""", unsafe_allow_html=True)

# Helper function to encode images for HTML display
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

# Function to load questions from folder structure
def load_questions():
    questions = {
        "easy": [],
        "medium": [],
        "hard": []
    }
    
    # Get questions from each difficulty folder
    for difficulty in questions.keys():
        difficulty_dir = os.path.join("questions", difficulty)
        if os.path.exists(difficulty_dir):
            question_dirs = [d for d in os.listdir(difficulty_dir) 
                            if os.path.isdir(os.path.join(difficulty_dir, d))]
            
            for q_dir in question_dirs:
                question_path = os.path.join(difficulty_dir, q_dir)
                config_file = os.path.join(question_path, "config.json")
                
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        question_data = json.load(f)
                        question_data["question_dir"] = question_path
                        question_data["difficulty"] = difficulty
                        questions[difficulty].append(question_data)
    
    return questions

# Function to generate quiz questions
def generate_quiz():
    questions_data = load_questions()
    
    # Select random questions from each difficulty level
    easy_questions = random.sample(questions_data["easy"], min(3, len(questions_data["easy"])))
    medium_questions = random.sample(questions_data["medium"], min(4, len(questions_data["medium"])))
    hard_questions = random.sample(questions_data["hard"], min(3, len(questions_data["hard"])))
    
    # Combine all questions
    st.session_state.questions = easy_questions + medium_questions + hard_questions
    # Shuffle the questions
    random.shuffle(st.session_state.questions)
    
    # Reset quiz state
    st.session_state.current_question = 0
    st.session_state.answers = [None] * len(st.session_state.questions)
    st.session_state.score = 0
    st.session_state.quiz_completed = False

# Function to handle login
def login(email, password):
    # In a real application, you would check credentials against a database
    # For this example, we'll use a simple hardcoded check
    valid_credentials = {
        "0": "0"
    }
    
    if email in valid_credentials and valid_credentials[email] == password:
        st.session_state.authenticated = True
        return True
    return False

# Function to handle answer submission
def submit_answer(question_idx, selected_option):
    st.session_state.answers[question_idx] = selected_option
    
    # Check if answer is correct
    correct_answer = st.session_state.questions[question_idx]["correct_answer"]
    if selected_option == correct_answer:
        st.session_state.score += 1
    
    # Move to next question
    st.session_state.current_question += 1

# Function to display image or text question
def display_question(question_data):
    question_dir = question_data["question_dir"]
    
    # Check if this is a multi-part question
    is_multipart = "subquestions" in question_data and len(question_data.get("subquestions", [])) > 0
    
    if is_multipart:
        # For multi-part questions, we need to track the current subquestion
        if "current_subquestion" not in st.session_state:
            st.session_state.current_subquestion = 0
        
        subquestions = question_data["subquestions"]
        current_sub_idx = st.session_state.current_subquestion
        
        # Display the main question first
        if "question_text" in question_data and question_data["question_text"]:
            st.markdown(f"### Main Question: {question_data['question_text']}")
        
        # Display main question image if exists
        question_image_path_jpg = os.path.join(question_dir, "question.jpg")
        question_image_path_png = os.path.join(question_dir, "question.png")
        
        # Center the question image 
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        if os.path.exists(question_image_path_jpg):
            st.markdown(f'<div class="question-img-container"><img src="data:image/jpeg;base64,{encode_image(question_image_path_jpg)}" /></div>', unsafe_allow_html=True)
        elif os.path.exists(question_image_path_png):
            st.markdown(f'<div class="question-img-container"><img src="data:image/png;base64,{encode_image(question_image_path_png)}" /></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Now display the current subquestion
        st.markdown(f"#### Part {current_sub_idx + 1} of {len(subquestions)}")
        current_subq = subquestions[current_sub_idx]
        
        # Display subquestion text
        if "text" in current_subq:
            st.markdown(f"**{current_subq['text']}**")
        
        # Display subquestion image if exists
        subq_image_path_jpg = os.path.join(question_dir, f"subquestion_{current_sub_idx + 1}.jpg")
        subq_image_path_png = os.path.join(question_dir, f"subquestion_{current_sub_idx + 1}.png")
        
        # Center the subquestion image
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        if os.path.exists(subq_image_path_jpg):
            st.markdown(f'<div class="question-img-container"><img src="data:image/jpeg;base64,{encode_image(subq_image_path_jpg)}" /></div>', unsafe_allow_html=True)
        elif os.path.exists(subq_image_path_png):
            st.markdown(f'<div class="question-img-container"><img src="data:image/png;base64,{encode_image(subq_image_path_png)}" /></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display answer options for the subquestion
        option_labels = ["A", "B", "C", "D"]
        selected_option = None
        
        # Check if we have any image options for the subquestion
        has_image_options = False
        for option_label in option_labels:
            option_image_path_jpg = os.path.join(question_dir, f"subq{current_sub_idx + 1}_option_{option_label.lower()}.jpg")
            option_image_path_png = os.path.join(question_dir, f"subq{current_sub_idx + 1}_option_{option_label.lower()}.png")
            if os.path.exists(option_image_path_jpg) or os.path.exists(option_image_path_png):
                has_image_options = True
                break
        
        # Handle image-based options for subquestion
        if has_image_options:
            col1, col2, col3, col4 = st.columns(4)
            columns = [col1, col2, col3, col4]
            
            for i, option_label in enumerate(option_labels):
                option_image_path_jpg = os.path.join(question_dir, f"subq{current_sub_idx + 1}_option_{option_label.lower()}.jpg")
                option_image_path_png = os.path.join(question_dir, f"subq{current_sub_idx + 1}_option_{option_label.lower()}.png")
                
                with columns[i]:
                    st.write(f"**Option {option_label}**")
                    
                    if os.path.exists(option_image_path_jpg):
                        st.markdown(f'<div class="answer-img-container"><img src="data:image/jpeg;base64,{encode_image(option_image_path_jpg)}" /></div>', unsafe_allow_html=True)
                    elif os.path.exists(option_image_path_png):
                        st.markdown(f'<div class="answer-img-container"><img src="data:image/png;base64,{encode_image(option_image_path_png)}" /></div>', unsafe_allow_html=True)
                    elif "options" in current_subq and i < len(current_subq.get("options", [])):
                        st.write(current_subq["options"][i].get("text", ""))
                    
                    if st.button(f"Select {option_label}", key=f"subq_{current_sub_idx}_option_{i}"):
                        selected_option = option_label
        
        # Handle text-based options for subquestion
        else:
            for i, option_label in enumerate(option_labels):
                if "options" in current_subq and i < len(current_subq.get("options", [])):
                    col1, col2 = st.columns([1, 10])
                    
                    with col1:
                        if st.button(option_label, key=f"subq_{current_sub_idx}_option_{i}"):
                            selected_option = option_label
                    
                    with col2:
                        st.write(current_subq["options"][i].get("text", ""))
        
        # Handle subquestion navigation and submission
        if selected_option:
            # Store the answer to the current subquestion
            if "subquestion_answers" not in st.session_state:
                st.session_state.subquestion_answers = [None] * len(subquestions)
            
            st.session_state.subquestion_answers[current_sub_idx] = selected_option
            
            # Move to next subquestion or submit the whole question
            if current_sub_idx < len(subquestions) - 1:
                st.session_state.current_subquestion += 1
                st.rerun()
            else:
                # Check all subquestion answers against correct answers
                correct_count = 0
                for idx, (subq, ans) in enumerate(zip(subquestions, st.session_state.subquestion_answers)):
                    if ans == subq["correct_answer"]:
                        correct_count += 1
                
                # Count as correct if majority of subquestions are correct
                overall_correct = correct_count >= len(subquestions) / 2
                
                # Reset for next question
                st.session_state.current_subquestion = 0
                del st.session_state.subquestion_answers
                
                # Use the "correct_answer" from the main question data to indicate if question is correct
                if overall_correct:
                    selected_option = question_data["correct_answer"]  # This makes the main submit_answer() function count it as correct
                else:
                    # Use any wrong answer letter
                    wrong_option = "A"
                    if question_data["correct_answer"] == "A":
                        wrong_option = "B"
                    selected_option = wrong_option
        
    # Regular single question handling
    else:
        # Display question image if exists
        question_image_path_jpg = os.path.join(question_dir, "question.jpg")
        question_image_path_png = os.path.join(question_dir, "question.png")
        
        # Center the question image
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        if os.path.exists(question_image_path_jpg):
            st.markdown(f'<div class="question-img-container"><img src="data:image/jpeg;base64,{encode_image(question_image_path_jpg)}" /></div>', unsafe_allow_html=True)
        elif os.path.exists(question_image_path_png):
            st.markdown(f'<div class="question-img-container"><img src="data:image/png;base64,{encode_image(question_image_path_png)}" /></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display question text if exists
        if "question_text" in question_data and question_data["question_text"]:
            st.markdown(f"### {question_data['question_text']}")
        
        # Display answer options
        option_labels = ["A", "B", "C", "D"]
        selected_option = None
        
        # Check if we have any image options
        has_image_options = False
        for option_label in option_labels:
            option_image_path_jpg = os.path.join(question_dir, f"option_{option_label.lower()}.jpg")
            option_image_path_png = os.path.join(question_dir, f"option_{option_label.lower()}.png")
            if os.path.exists(option_image_path_jpg) or os.path.exists(option_image_path_png):
                has_image_options = True
                break
        
        # Handle image-based options
        if has_image_options:
            col1, col2, col3, col4 = st.columns(4)
            columns = [col1, col2, col3, col4]
            
            for i, option_label in enumerate(option_labels):
                option_image_path_jpg = os.path.join(question_dir, f"option_{option_label.lower()}.jpg")
                option_image_path_png = os.path.join(question_dir, f"option_{option_label.lower()}.png")
                
                with columns[i]:
                    st.write(f"**Option {option_label}**")
                    
                    if os.path.exists(option_image_path_jpg):
                        st.markdown(f'<div class="answer-img-container"><img src="data:image/jpeg;base64,{encode_image(option_image_path_jpg)}" /></div>', unsafe_allow_html=True)
                    elif os.path.exists(option_image_path_png):
                        st.markdown(f'<div class="answer-img-container"><img src="data:image/png;base64,{encode_image(option_image_path_png)}" /></div>', unsafe_allow_html=True)
                    elif "options" in question_data and i < len(question_data.get("options", [])):
                        st.write(question_data["options"][i].get("text", ""))
                    
                    if st.button(f"Select {option_label}", key=f"option_{i}"):
                        selected_option = option_label
        
        # Handle text-based options
        else:
            for i, option_label in enumerate(option_labels):
                if "options" in question_data and i < len(question_data.get("options", [])):
                    col1, col2 = st.columns([1, 10])
                    
                    with col1:
                        if st.button(option_label, key=f"option_{i}"):
                            selected_option = option_label
                    
                    with col2:
                        st.write(question_data["options"][i].get("text", ""))
    
    return selected_option

# Main application
def main():
    # Title and description
    st.title("Maids.cc IQ Test")
    
    # Login section
    if not st.session_state.authenticated:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if login(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
    
    # Quiz section - visible only after authentication
    else:
        # If no quiz has been generated yet
        if not st.session_state.questions:
            st.subheader("Generate Test")
            if st.button("Generate New Test"):
                generate_quiz()
                st.rerun()
        
        # If quiz is in progress (not completed or not submitted)
        elif not st.session_state.quiz_completed:
            question_idx = st.session_state.current_question
            
            # Check if we've reached the end of questions
            if question_idx >= len(st.session_state.questions):
                st.subheader("Test Complete!")
                st.write("All the questions have been answered. Click 'Submit Test' to see the results.")
                
                if st.button("Submit Test"):
                    st.session_state.quiz_completed = True
                    st.rerun()
            else:
                current_question = st.session_state.questions[question_idx]
                
                # Progress indicator
                st.progress((question_idx) / len(st.session_state.questions))
                st.write(f"Question {question_idx + 1} of {len(st.session_state.questions)}")
                #st.write(f"Difficulty: {current_question.get('difficulty', 'Unknown')}")
                
                # Display the question and get selected option
                selected_option = display_question(current_question)
                
                # If an option was selected
                if selected_option:
                    submit_answer(question_idx, selected_option)
                    st.rerun()
        
        # Display results after completion and submission
        else:
            st.subheader("Test Results")
            st.write(f"Your score: {st.session_state.score} out of {len(st.session_state.questions)}")
            st.write(f"Percentage: {(st.session_state.score / len(st.session_state.questions)) * 100:.2f}%")
            
            # Show detailed results
            st.subheader("Results Breakdown")
            for i, (question, answer) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                is_correct = answer == question["correct_answer"]
                
                # Get question text or a default if it's an image-only question
                question_text = question.get('question_text', f'Question {i+1}')
                if not question_text:
                    question_text = f'Question {i+1} (Image)'
                
                st.markdown(
                    f"**Question {i+1}**: {question_text} - "
                    f"{'✓ Correct' if is_correct else '✗ Incorrect'}"
                )
                if not is_correct:
                    st.markdown(f"Your answer: {answer}, Correct answer: {question['correct_answer']}")
            
            # Restart button
            if st.button("Take Another Quiz"):
                st.session_state.questions = []
                st.rerun()

if __name__ == "__main__":
    main()