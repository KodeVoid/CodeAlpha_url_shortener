# Code Alpha URL Shortener

A comprehensive URL shortening service featuring custom codes, click analytics, and a full REST API.  
Built as part of the Code Alpha Internship Program.



## Features
- Shorten long URLs into compact links  
- Custom short codes support  
- Click analytics & tracking  
- REST API with Swagger documentation  
- Bulk operations support  
- Responsive frontend with TailwindCSS  



## API Documentation
Documentation is available at:  
[API Docs](https://codealpha-url-shortener.onrender.com/api-docs)

### Example Endpoints
- POST /short → Create a short URL  
- GET /urls → List all shortened URLs (paginated)  
- GET /urls/{id} → Retrieve details for a specific short URL  
- GET /{short_code} → Redirect to original long URL  


## Tech Stack
- Backend: Flask (Python)  
- Database: PostgreSQL (or SQLite for local dev)  
- Frontend: HTML + TailwindCSS + Vanilla JS  
- Deployment: Render + Vercel  



## Installation & Setup

### Clone the repository:
git clone https://github.com/KodeVoid/CodeAlpha_url_shortener.git
cd CodeAlpha_url_shortener


### Create & activate a virtual environment:


python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


### Install dependencies:


pip install -r requirements.txt


### Run the Flask App

#### Set up the required environment variables:

export DATABASE_URL=postgres://username:password@host:5432/dbname
export BASE_URL=http://localhost:5000
export FLASK_APP=app/app.py
You can also switch to SQLite or any other database of your choice by changing DATABASE_URL.
#### Initialize the database:

 python init_db.py


#### Start the server:


flask run


The app will be available at:
http://localhost:5000



## Deployment

The project is deployed here:
[Live Demo](https://void-iota-ashen.vercel.app/)



## Usage

### Shorten a URL (API)

bash
curl -X POST "https://codealpha-url-shortener.onrender.com/short" \
-H "Content-Type: application/json" \
-d '{"url": "https://example.com"}'


### Response

json
{
  "id": 1,
  "short_url": "https://codealpha-url-shortener.onrender.com/abc123",
  "long_url": "https://example.com",
  "clicks": 0
}




## Contributing

1. Fork the repo
2. Create a new branch: git checkout -b feature/my-feature
3. Commit changes: git commit -m "Add new feature"
4. Push to branch: git push origin feature/my-feature
5. Open a Pull Request



## Author

Developed with passion by [KodeVoid](https://www.linkedin.com/in/kodevoid)

 Portfolio: [void-iota-ashen.vercel.app](https://void-iota-ashen.vercel.app/)
 GitHub: [KodeVoid](https://github.com/KodeVoid)
 LinkedIn: [@kodevoid](https://www.linkedin.com/in/kodevoid)



## License

This project is licensed under the MIT License.
Feel free to use and modify for your own projects.


