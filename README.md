# CS2 Skin Market

A web-based marketplace for Counter-Strike 2 (CS2) skins trading. This platform allows users to buy, sell, and manage their CS2 skin inventory.

## Features

- **User Authentication**
  - User registration and login
  - Secure password management
  - Profile management

- **Market Features**
  - Browse available CS2 skins
  - Buy skins with virtual currency
  - View detailed skin information
  - Real-time inventory management

- **Account Management**
  - Virtual currency balance
  - Transaction history
  - Personal inventory management
  - Account recharge functionality

- **Admin Panel**
  - User management
  - Transaction monitoring
  - Skin inventory control
  - Activity logging

## Technology Stack

- **Backend**
  - Python 3.9
  - Django 4.2.20
  - SQLite3 Database

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 4

- **Additional Packages**
  - django-crispy-forms
  - Pillow (Python Imaging Library)
  - whitenoise
  - gunicorn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JiangY03/ITGroup96-web_app_code.git
cd ITGroup96-web_app_code
```

2. Create and activate virtual environment:
```bash
python3.9 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

```
ITGroup96-web_app_code/
├── accounts/          # User authentication and profile management
├── market/           # Core marketplace functionality
├── payment/          # Payment and transaction handling
├── cs2_skin_market/  # Project settings and configuration
├── templates/        # HTML templates
├── static/          # Static files (CSS, JS, images)
└── media/           # User-uploaded files
```

## Deployment

The project is deployed on PythonAnywhere and can be accessed at:
[ITGroup96.pythonanywhere.com](https://ITGroup96.pythonanywhere.com)

## Security Features

- CSRF protection
- Secure password hashing
- User session management
- Protected admin interface
- Secure file upload handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Link: [https://github.com/JiangY03/ITGroup96-web_app_code](https://github.com/JiangY03/ITGroup96-web_app_code)
