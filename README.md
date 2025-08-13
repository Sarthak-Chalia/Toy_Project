# Toy_Project

## Features

- 🔇 Offline wake word detection using Porcupine
- 🎙️ Voice-based authentication system
- 📝 Context-aware conversations (maintains last 10 messages)
- 💾 Local storage for user credentials and chat history
- 🔊 Text-to-speech and speech-to-text capabilities
- 🤖 Powered by Meta-Llama-3.1-8B-Instruct-Turbo LLM

## Technologies and Libraries Used

### Core Libraries
1. **Speech Recognition**:
   - `speech_recognition` - For converting speech to text using Google's speech recognition API
   - `pvporcupine` - For offline wake word detection ("porcupine")

2. **Text-to-Speech**:
   - `pyttsx3` - Offline text-to-speech conversion

3. **AI and Language Processing**:
   - `langchain_together` - Interface for the Together AI API
   - `langchain` - For conversation memory and message schemas

4. **Audio Processing**:
   - `sounddevice` - For audio input stream handling
   - `numpy` - For audio data processing

5. **Data Storage**:
   - `json` - For storing user credentials and chat history locally

## System Architecture and Methodology

### 1. Offline Wake Word Detection
- **Algorithm**: Uses Porcupine's lightweight wake word detection engine
- **Process**:
  1. Continuously listens to microphone input in sleep mode
  2. Processes audio frames in real-time
  3. Detects the wake word "porcupine" without internet connection
  4. Activates the main system upon detection

### 2. Voice Authentication System
- **User Database**:
  - Stores usernames and passwords in `users.json`
  - Case-insensitive matching for usernames
  - Exact matching for passwords

- **Authentication Flow**:
  1. Prompts user for username via voice
  2. Checks if username exists (case-insensitive)
  3. For existing users:
     - 3 attempts for password verification
  4. For new users:
     - Creates new account after password confirmation

### 3. Conversation Management
- **Chat History**:
  - Maintains last 10 messages per user in `chat_history.json`
  - Includes timestamps for each message
  - Structured with roles ("user" or "assistant")

- **Context Handling**:
  1. Prepares conversation context from history
  2. Maintains system message for new conversations
  3. Limits context to most recent messages for efficiency

### 4. AI Response Generation
- **Model**: Meta-Llama-3.1-8B-Instruct-Turbo via Together AI
- **Temperature**: 0.7 (balanced creativity/focus)
- **Message Preparation**:
  1. Combines system message, chat history, and new input
  2. Formats messages according to LangChain schema
  3. Sends to LLM for response generation

## Installation and Setup

### Prerequisites
- Python 3.8+
- Microphone
- Speaker/audio output

##Usage Instructions

Activation:
Run the program in terminal:
python assistant.py
System starts in sleep mode listening for wake word "porcupine"

Authentication:
When activated, system will prompt for:
Username (voice input)
Password (voice input)
New users will go through account creation

Interaction:
After authentication, speak your query
System responds via voice and maintains context
Previous 10 messages are used for context

Deactivation:
Say "exit" or "quit" to end session
System returns to sleep mode after each interaction
