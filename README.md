# task-manager-api
Full-stack task management with Django REST + React
# ✅ Task Management REST API — Django + React

A full-stack Jira-style task management app with project boards, task assignment, JWT auth, and Kanban UI.

## ✨ Features
- RESTful CRUD for Users, Projects, Tasks, Comments
- JWT-based Authentication
- Role-based access control (Admin / Member)
- React Kanban board with drag-and-drop
- 85% unit test coverage
- GitHub Actions CI/CD pipeline
- Postman API documentation

## 🛠️ Tech Stack
**Backend:** `Python` `Django REST Framework` `MySQL` `JWT`  
**Frontend:** `React` `CSS Modules`  
**DevOps:** `GitHub Actions` `Postman`

## 📁 Project Structure
```
task-manager/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── api/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── tests.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── KanbanBoard.jsx
│   │   │   └── TaskCard.jsx
│   │   ├── App.jsx
│   │   └── api.js
│   └── package.json
├── .github/
│   └── workflows/ci.yml
└── README.md
```

## ⚙️ Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure MySQL in settings.py, then:
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## ⚙️ Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔑 API Endpoints
| Method | Endpoint              | Description         | Auth     |
|--------|-----------------------|---------------------|----------|
| POST   | /api/auth/login/      | Get JWT token       | Public   |
| GET    | /api/projects/        | List projects       | Required |
| POST   | /api/projects/        | Create project      | Admin    |
| GET    | /api/tasks/           | List tasks          | Required |
| POST   | /api/tasks/           | Create task         | Admin    |
| PATCH  | /api/tasks/{id}/      | Update task status  | Member   |
| DELETE | /api/tasks/{id}/      | Delete task         | Admin    |

## 🧪 Run Tests
```bash
cd backend
python manage.py test api --verbosity=2
```

## 👤 Author
**Narayana Vasan S S**
