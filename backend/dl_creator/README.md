# DL Creator - Driving License Management System

A Spring Boot application for managing driving license applications and user authentication.

## 🚀 Features

- **User Authentication & Authorization**: JWT-based authentication system
- **Driving License Management**: Create, update, and manage driving license applications
- **User Management**: User registration and profile management
- **RESTful API**: Complete REST API with proper error handling
- **Database Integration**: MySQL database with JPA/Hibernate
- **Security**: Spring Security with JWT tokens

## 🛠️ Tech Stack

- **Backend**: Spring Boot 3.5.4
- **Database**: H2 (In-Memory)
- **Security**: Spring Security + JWT
- **ORM**: Spring Data JPA + Hibernate
- **Build Tool**: Maven
- **Java Version**: 17

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Java 17** or higher
- **Maven 3.6** or higher
- **Docker** (optional, for containerized deployment)

**Note**: This application uses H2 in-memory database, so no external database setup is required!

### 🎯 Benefits of H2 Database

- **Zero Configuration**: No external database setup required
- **In-Memory**: Fast performance with data stored in memory
- **Embedded**: Database is part of the application
- **Web Console**: Built-in H2 console for database management
- **Development Friendly**: Perfect for development and testing
- **Auto-Create Tables**: Tables are automatically created on startup

## 🚀 Quick Start

### Option 1: Local Development

#### 1. Build and Run (No Database Setup Required!)

The application uses H2 in-memory database, so no external database setup is needed.

```bash
cd dl_creator

# Build the project
mvn clean install

# Run the application
mvn spring-boot:run
```

The application will start on `http://localhost:7500`

**Access Points:**
- **Application API**: http://localhost:7500
- **H2 Database Console**: http://localhost:7500/h2-console
  - JDBC URL: `jdbc:h2:mem:dl_creator_db`
  - Username: `sa`
  - Password: (leave empty)

**Quick Test:**
```bash
# Test the application is running
curl http://localhost:7500/user/createUser \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"fullName": "Test User", "email": "test@example.com", "password": "123456"}'
```

### Option 2: Docker Deployment

#### Using Docker Compose (Recommended)

1. **Build and run with Docker Compose:**
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

2. **Stop the services:**
```bash
docker-compose down
```

#### Manual Docker Build

1. **Build the Docker image:**
```bash
docker build -t dl-creator .
```

2. **Run the container:**
```bash
docker run -p 7500:7500 --name dl-creator-app dl-creator
```

## 📚 API Documentation

### User Management Endpoints

#### Create User
```http
POST /user/createUser
Content-Type: application/json

{
  "fullName": "John",
  "email": "john@example.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "email": "john@example.com",
    "fullName": "John"
  }
}
```

#### Get Current User
```http
GET /user/currentUser
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Current user retrieved successfully",
  "data": {
    "email": "john@example.com",
    "fullName": "John"
  }
}
```

### Authentication Endpoints

#### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "token": "<jwt-token>",
  "expiresIn": 3600000
}
```

### Driving License Endpoints

#### Create Driving License
```http
POST /drivingLicense/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "firstName": "Alex",
  "lastName": "Rogers",
  "vehicleType": "Car",
  "vehicleMake": "Toyota",
  "address": "123 Main St, Springfield, IL"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Driving license created successfully",
  "data": {
    "id": 152,
    "userId": 102,
    "licenseNumber": "DL-102-175578760328916906",
    "issueDate": "2025-08-21T14:46:43.290+00:00",
    "expirationDate": "2025-08-21T14:46:43.290+00:00",
    "firstName": "Alex",
    "lastName": "Rogers",
    "vehicleType": "Car",
    "vehicleMake": "Toyota",
    "address": "123 Main St, Springfield, IL"
  }
}
```

#### Get License Details
```http
GET /drivingLicense/getLicenseDetails
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Driving license retrieved successfully",
  "data": {
    "id": 152,
    "userId": 102,
    "licenseNumber": "DL-102-175578760328916906",
    "issueDate": "2025-08-21T14:46:43.290+00:00",
    "expirationDate": "2025-08-21T14:46:43.290+00:00",
    "firstName": "Alex",
    "lastName": "Rogers",
    "vehicleType": "Car",
    "vehicleMake": "Toyota",
    "address": "123 Main St, Springfield, IL"
  }
}
```

#### Update License Status
```http
POST /drivingLicense/updateStatus?status=PENDING
Authorization: Bearer <token>
```

**Available Status Values:**
- `PENDING`
- `CANCELLED`
- `SUBMITTED`
- `PRINTED`
- `DISPATCHED`
- `DELIVERED`

#### Update License Information
```http
POST /drivingLicense/updateLicenseInfo
Authorization: Bearer <token>
Content-Type: application/json

{
  "firstName": "Alex",
  "lastName": "Rogers",
  "vehicleType": "Car",
  "vehicleMake": "Toyota",
  "address": "456 New St, Springfield, IL",
  "licenseStatus": "SUBMITTED"
}
```

#### Change Address
```http
POST /drivingLicense/changeAddress?address=789 Oak St, Springfield, IL
Authorization: Bearer <token>
```

#### Renew License
```http
POST /drivingLicense/renewLicense
Authorization: Bearer <token>
```

## 🔄 API Workflow

### Typical Usage Flow:

1. **Create User Account**
   ```bash
   POST /user/createUser
   ```

2. **Login to Get JWT Token**
   ```bash
   POST /auth/login
   ```

3. **Create Driving License**
   ```bash
   POST /drivingLicense/create
   Authorization: Bearer <token>
   ```

4. **View License Details**
   ```bash
   GET /drivingLicense/getLicenseDetails
   Authorization: Bearer <token>
   ```

5. **Update License Status** (Admin/System)
   ```bash
   POST /drivingLicense/updateStatus?status=SUBMITTED
   Authorization: Bearer <token>
   ```

### Example cURL Commands:

```bash
# 1. Create a user
curl -X POST http://localhost:7500/user/createUser \
  -H "Content-Type: application/json" \
  -d '{"fullName": "John Doe", "email": "john@example.com", "password": "123456"}'

# 2. Login to get token
curl -X POST http://localhost:7500/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "123456"}'

# 3. Create driving license (use token from step 2)
curl -X POST http://localhost:7500/drivingLicense/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"firstName": "John", "lastName": "Doe", "vehicleType": "Car", "vehicleMake": "Toyota", "address": "123 Main St, City, State"}'

# 4. Get license details
curl -X GET http://localhost:7500/drivingLicense/getLicenseDetails \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Configuration

### Environment Variables

You can override the default configuration using environment variables:

- `SPRING_DATASOURCE_URL`: H2 database URL (default: jdbc:h2:mem:dl_creator_db)
- `SPRING_DATASOURCE_USERNAME`: H2 username (default: sa)
- `SPRING_DATASOURCE_PASSWORD`: H2 password (default: empty)
- `SPRING_H2_CONSOLE_ENABLED`: Enable H2 console (default: true)
- `SPRING_H2_CONSOLE_PATH`: H2 console path (default: /h2-console)
- `JWT_SECRET`: JWT secret key
- `JWT_EXPIRATION`: JWT expiration time in milliseconds (default: 3600000)
- `SERVER_PORT`: Application port (default: 7500)

### Application Properties

Key configuration in `application.properties`:

```properties
# Server Configuration
server.port=7500

# H2 Database Configuration
spring.datasource.url=jdbc:h2:mem:dl_creator_db
spring.datasource.username=sa
spring.datasource.password=

# H2 Console Configuration
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# JPA Configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# JWT Configuration
security.jwt.secret-key=your_jwt_secret_key
security.jwt.expiration-time=3600000
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
mvn test

# Run tests with coverage
mvn test jacoco:report
```

## 📦 Project Structure

```
src/
├── main/
│   ├── java/com/dlyog/dl_creator/
│   │   ├── Auth/                 # Authentication related classes
│   │   ├── config/               # Configuration classes
│   │   ├── controller/           # REST controllers
│   │   ├── dto/                  # Data Transfer Objects
│   │   ├── Enum/                 # Enums
│   │   ├── Exception/            # Exception handling
│   │   ├── model/                # Entity models
│   │   ├── record/               # Record classes
│   │   ├── repository/           # Data access layer
│   │   └── service/              # Business logic layer
│   └── resources/
│       └── application.properties
└── test/                         # Test classes
```

## 🐳 Docker Configuration

The application includes Docker support with:

- **Dockerfile**: Multi-stage build for optimized image size
- **docker-compose.yml**: Complete stack with MySQL database
- **.dockerignore**: Excludes unnecessary files from build context

### Docker Compose Services

- **dl-creator-app**: Spring Boot application with embedded H2 database

## 🔒 Security

- JWT-based authentication
- Password encryption using BCrypt
- Role-based access control
- CORS configuration
- Input validation and sanitization

