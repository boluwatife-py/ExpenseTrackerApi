# Expense Tracker Backend API

A Flask-based RESTful API for managing personal expenses, with user authentication, expense tracking, and category management.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd expense_tracker
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   Create a `.env` file in the root directory:
   ```bash
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Authentication
- **POST /api/auth/register**: Register a new user
  - Body: `{ "username": "string", "email": "string", "password": "string" }`
- **POST /api/auth/login**: Login and receive JWT token
  - Body: `{ "username": "string", "password": "string" }`

### Expenses
- **POST /api/expenses/**: Create a new expense (JWT required)
  - Body: `{ "amount": float, "description": "string", "category_id": int, "date": "YYYY-MM-DD" (optional) }`
- **GET /api/expenses/**: Get all expenses for the user (JWT required)
- **GET /api/expenses/<id>**: Get a specific expense (JWT required)
- **PUT /api/expenses/<id>**: Update an expense (JWT required)
  - Body: `{ "amount": float, "description": "string", "category_id": int, "date": "YYYY-MM-DD" }` (all optional)
- **DELETE /api/expenses/<id>**: Delete an expense (JWT required)

### Categories
- **POST /api/categories/**: Create a new category (JWT required)
  - Body: `{ "name": "string" }`
- **GET /api/categories/**: Get all categories for the user (JWT required)
- **PUT /api/categories/<id>**: Update a category (JWT required)
  - Body: `{ "name": "string" }`
- **DELETE /api/categories/<id>**: Delete a category (JWT required, only if no expenses are associated)

## Database
- Uses SQLite (`expense_tracker.db`) for simplicity.
- Tables: `user`, `expense`, `category`.

## Security
- JWT-based authentication for protected routes.
- Passwords are hashed using bcrypt.
- Input validation to prevent common errors.

## Notes
- Ensure you include the `Authorization: Bearer <token>` header for protected routes.
- The API uses CORS to allow cross-origin requests.
- Dates should be in `YYYY-MM-DD` format.