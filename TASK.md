# Project Tasks

## User Stories
*   [ ] As a visitor, I want to authenticate through a specified password to ensure only authorized personnel can access this internal demo tool.
*   [ ] As an employee, I want to input my questions in an instant messaging-like interface and clearly see the bot's answers, so that the entire conversation feels natural.
*   [ ] As an HR administrator, I want to directly upload the latest company policy documents (e.g., PDF, DOCX) via the webpage, so that the intelligent assistant can learn and update its knowledge base.
*   [ ] As a user, when I send a question, I expect the system to quickly send it to the backend for processing and display the generated answer to me, so that I get a timely response.
*   [ ] As a user, if I accidentally refresh the browser page, I want my previous conversation records to be preserved, so I don't lose my context.

## Functional Requirements
*   [ ] **Feature 1: User Authentication**
    *   [ ] Implement a centered, minimalistic login page UI.
    *   [ ] Create a password input field (`<input type="password">`).
    *   [ ] Create an "Enter" or "Login" button.
    *   [ ] Implement client-side logic for hardcoded password validation.
    *   [ ] Redirect to the main chat interface upon successful authentication.
    *   [ ] Display a clear "Incorrect password, please try again" error message on authentication failure.
    *   [ ] Prevent navigation to main pages without successful authentication.
    *   [ ] Implement button disable/enable state based on password input presence.
*   [ ] **Feature 2: Core Chat Interface**
    *   [ ] Design and implement the main chat interface layout with distinct chat history and question input areas.
    *   [ ] Develop a message component for user questions (right-aligned, distinct color).
    *   [ ] Develop a message component for bot answers (left-aligned, distinct color).
    *   [ ] Implement functionality to send messages using the `Enter` key.
    *   [ ] Implement functionality to send messages by clicking a "Send" button.
    *   [ ] Clear the input box automatically after sending a message.
    *   [ ] Display a clear loading animation/indicator (e.g., "Thinking...") while waiting for the backend response.
    *   [ ] Implement automatic scrolling to the latest message in the chat history.
    *   [ ] Implement "typing effect" for bot's answers.
*   [ ] **Feature 3: File Upload Page**
    *   [ ] Create a clear navigation entry point (e.g., button, link) in the main application UI (header/sidebar) leading to the upload page.
    *   [ ] Implement the "Knowledge Base Document Upload" page with its title.
    *   [ ] Design and implement a file selection area with a clear text prompt ("Drag file here, or click to select file").
    *   [ ] Implement drag-and-drop functionality for file uploads.
    *   [ ] Implement file input handling for clicking to select files.
    *   [ ] Enforce client-side file type restrictions (e.g., `.pdf`, `.docx`).
    *   [ ] Disable the "Upload" button when no file is selected.
    *   [ ] Change the "Upload" button to a loading state upon click to prevent multiple submissions.
    *   [ ] Send files to the `POST /upload` endpoint using `multipart/form-data`.
    *   [ ] Display a global "File is being uploaded and processed, this may take some time, please wait..." message during upload and processing.
    *   [ ] Parse and display the backend's success message (e.g., `File 'example.pdf' uploaded and processed successfully.`).
    *   [ ] Provide a navigation link or button to return to the chat page after successful upload.
    *   [ ] Display a clear error message on the UI if file upload or processing fails.
*   [ ] **Feature 4: API Integration & Data Flow**
    *   [ ] Configure API client (e.g., Axios instance) for backend communication.
    *   [ ] Implement `POST /query` request with `{"query": "user_input"}` body.
    *   [ ] Implement parsing of `/query` successful response: `response.data.answer.raw`.
    *   [ ] Implement `POST /upload` request with `multipart/form-data`.
    *   [ ] Implement parsing of `/upload` successful response: `response.data.message`.
    *   [ ] Implement global error handling for all API requests, displaying user-friendly messages for failures.
    *   [ ] Implement specific error handling for different API error codes (e.g., 4xx, 5xx).
*   [ ] **Feature 5: Conversation State Management**
    *   [ ] Implement storage and retrieval of conversation history using `sessionStorage`.
    *   [ ] Serialize chat message objects before storing them in `sessionStorage`.
    *   [ ] Deserialize chat message strings when retrieving from `sessionStorage`.
    *   [ ] Load and display conversation history from `sessionStorage` upon page load.
    *   [ ] Display a default welcome message if no conversation history is found in `sessionStorage`.

## Non-Functional Requirements (NFRs)
*   [ ] **UI/UX Design**
    *   [ ] Establish a dark theme as the primary visual style.
    *   [ ] Define and implement a bright accent color palette.
    *   [ ] Ensure all components adhere to a consistent, modern visual style using Tailwind CSS and/or shadcn/ui.
    *   [ ] Implement smooth page transitions (e.g., using React Router transition effects if desired).
    *   [ ] Add immediate visual feedback for interactive elements (e.g., button hover/active states, input focus states).
    *   [ ] Implement the "typing effect" for bot answers, displaying text character by character.
    *   [ ] Implement responsive design for desktop breakpoints.
    *   [ ] Implement responsive design for common mobile device breakpoints.
*   [ ] **Performance**
    *   [ ] Configure Vite for optimal fast cold start and hot module replacement.
    *   [ ] Implement code splitting and lazy loading for routes/components to optimize initial load time.
    *   [ ] Optimize rendering of long chat histories to ensure smooth scrolling (e.g., virtualized lists if history becomes extremely long, otherwise just efficient rendering).
    *   [ ] Minimize re-renders using `React.memo` or `useCallback`/`useMemo` where appropriate.
*   [ ] **Technical Stack Adherence**
    *   [ ] Ensure all new development strictly uses React as the core framework.
    *   [ ] Ensure project build and development leverages Vite.
    *   [ ] Use Tailwind CSS for all styling, including custom utilities.
    *   [ ] Integrate and utilize shadcn/ui components where applicable for UI consistency and speed.
    *   [ ] Manage component state primarily with React Hooks (`useState`, `useEffect`).
    *   [ ] Utilize `sessionStorage` API exclusively for conversation persistence.

## Technical Design & Architecture Tasks
*   [ ] Initialize a new React project using Vite.
*   [ ] Configure Tailwind CSS within the Vite/React project.
*   [ ] Integrate shadcn/ui components into the project.
*   [ ] Define the project's folder structure (e.g., `src/components`, `src/pages`, `src/services`, `src/hooks`, `src/utils`).
*   [ ] Set up React Router for navigation between login, chat, and upload pages.
*   [ ] Design the overall application state flow using React Context or custom hooks for global concerns like loading states, error messages.
*   [ ] Define global CSS variables or Tailwind theme extensions for colors (dark mode, accent colors).
*   [ ] Plan the component hierarchy for each main page (Login, Chat, Upload).
*   [ ] Design the API service layer (e.g., using Axios) with interceptors for common error handling.

## Backend Development Tasks
*   [ ] Review and confirm the exact `POST /query` endpoint details (URL, request body, successful response schema).
*   [ ] Review and confirm the exact `POST /upload` endpoint details (URL, expected `multipart/form-data` structure, successful response schema).
*   [ ] Understand and document backend error response formats for various failures (e.g., validation errors, internal server errors).

## Frontend Development Tasks
*   [ ] **Authentication Module**
    *   [ ] Create `LoginPage.jsx` component.
    *   [ ] Implement `useAuth.js` custom hook for login logic and state.
    *   [ ] Implement `AuthGuard.jsx` component for protected routes.
    *   [ ] Style login page using Tailwind CSS for centering and minimalist design.
*   [ ] **Chat Module**
    *   [ ] Create `ChatPage.jsx` component.
    *   [ ] Develop `MessageInput.jsx` component.
    *   [ ] Develop `ChatMessage.jsx` component (with props for `isUser`, `messageText`).
    *   [ ] Implement `useChat.js` custom hook to manage chat state, API calls, and history persistence.
    *   [ ] Implement a `ThinkingIndicator.jsx` component for loading states.
    *   [ ] Integrate a smooth scroll utility or hook.
    *   [ ] Implement the "typing effect" logic within `ChatMessage.jsx` or a dedicated hook.
*   [ ] **File Upload Module**
    *   [ ] Create `UploadPage.jsx` component.
    *   [ ] Develop `FileUploadArea.jsx` component with drag-and-drop handlers.
    *   [ ] Implement `useFileUpload.js` custom hook for upload logic, state, and API calls.
    *   [ ] Develop a `GlobalNotification.jsx` component to display processing messages.
    *   [ ] Style file upload page elements consistent with theme.
*   [ ] **Common UI Components**
    *   [ ] Develop a `Button.jsx` component based on shadcn/ui for consistent styling and states.
    *   [ ] Develop an `Input.jsx` component based on shadcn/ui for consistent styling.
    *   [ ] Create a `Header.jsx` component for navigation (including "Upload Document" link).
    *   [ ] Implement a `LoadingSpinner.jsx` component for general loading feedback.
*   [ ] **Responsiveness**
    *   [ ] Apply Tailwind CSS responsive utility classes (`sm:`, `md:`, `lg:`) to all main layouts and components.
    *   [ ] Test and refine UI elements on various screen sizes using browser developer tools.

## Data & Database Tasks
*   [ ] Define the JavaScript object schema for a single chat message (e.g., `{ id: string, sender: 'user' | 'bot', text: string, timestamp: number }`).
*   [ ] Implement `JSON.stringify` for storing chat history array in `sessionStorage`.
*   [ ] Implement `JSON.parse` for retrieving and parsing chat history from `sessionStorage`.

## DevOps & Infrastructure Tasks
*   [ ] Configure Vite build command for production-ready static assets.
*   [ ] Set up environment variables (e.g., `VITE_API_BASE_URL`, `VITE_HARDCODED_PASSWORD`) for development and production.
*   [ ] Create a basic `Dockerfile` for containerizing the frontend application (if deploying via containers).
*   [ ] Draft a simple deployment script or CI/CD pipeline step to build and deploy static assets to a web server/CDN.
*   [ ] Define hosting strategy for the online demo (e.g., Vercel, Netlify, S3 + CloudFront).

## Testing & Quality Assurance Tasks
*   [ ] **Unit Tests**
    *   [ ] Write unit tests for the login authentication logic.
    *   [ ] Write unit tests for chat message parsing and formatting.
    *   [ ] Write unit tests for `sessionStorage` persistence logic.
    *   [ ] Write unit tests for file type validation logic.
    *   [ ] Write unit tests for custom hooks (`useChat`, `useFileUpload`, `useAuth`).
*   [ ] **Integration Tests**
    *   [ ] Write integration tests for login flow (simulating API call, even if hardcoded).
    *   [ ] Write integration tests for sending chat messages and displaying responses.
    *   [ ] Write integration tests for file upload process (simulating API call).
*   [ ] **End-to-End Tests (E2E)**
    *   [ ] Set up an E2E testing framework (e.g., Cypress or Playwright).
    *   [ ] Create E2E test case: Successful login and navigation to chat.
    *   [ ] Create E2E test case: Sending a message and receiving a response.
    *   [ ] Create E2E test case: Navigating to upload, performing a successful upload, and returning to chat.
    *   [ ] Create E2E test case: Verifying chat history persistence after page refresh.
*   [ ] **Manual Testing**
    *   [ ] Conduct comprehensive UI/UX review on desktop browsers (Chrome, Firefox, Safari).
    *   [ ] Conduct comprehensive UI/UX review on various mobile devices/emulators.
    *   [ ] Perform accessibility checks (keyboard navigation, basic ARIA roles).
    *   [ ] Perform performance checks (loading speed, interaction smoothness, especially with long chat history).
    *   [ ] Test all error scenarios (incorrect password, API failures, invalid file types).

## Documentation Tasks
*   [ ] Create/Update `README.md` with project setup instructions, development commands, and deployment notes.
*   [ ] Document API client configuration and common error handling strategies.
*   [ ] Document the hardcoded password location (e.g., `.env` file or direct JS variable).
*   [ ] Document the chosen state management approach for chat history.
*   [ ] Create a `CONTRIBUTING.md` guide for future developers (if applicable).