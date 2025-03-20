# BTC Demo Trading

BTC Demo Trading is a web application that lets you paper trade Bitcoin (BTC) in a risk-free environment. The app starts with an account pre-loaded with $10,000 and 0.5 BTC, allowing you to simulate market orders, track your positions, and review your order history.

## Features

- **Live Bitcoin Price Updates:**  
  The app fetches the latest BTC price every 5 seconds for real-time market tracking.
  
- **Paper Trading:**  
  Simulate buy and sell market orders with the click of a button.
  
- **Account Management:**  
  Start with an initial balance of $10,000 and 0.5 BTC, and watch your account update as you trade.
  
- **Positions & Order History:**  
  View your current open positions, close positions when desired, and review your complete trading history.

## Technology Stack

- **Backend:**
  - Python with FastAPI
  - PostgreSQL for storing account and order data
  - Redis for caching order history
  - Poetry for dependency management
  - Fully tested using pytest
- **Frontend:**
  - A lightweight web interface (React and/or Django for the frontend)
- **Containerization & Orchestration:**
  - Docker Compose to run and orchestrate all services

## Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/slickroot/btc-demo-trading.git
   cd btc-demo-trading
   ```
2. **Start the Application:**
   Use Docker Compose to build and run the services:
   ```bash
   docker compose up
   ```
   Once the containers are up and running, open your browser and navigate to [http://localhost:3000](http://localhost:3000) to view the app.

3. **Screenshot:**
  ![screenshot](https://github.com/user-attachments/assets/836b2ab3-ce78-488f-a6e4-4a630ebf189b)

## Running Tests
The backend is fully tested using pytest. To run the tests, use the following command:

  ```bash
  docker compose -f docker-compose.yml -f docker-compose.test.yml run tests
  ```
This command will start the necessary services for testing and execute the entire test suite.

## Project Structure
```bash
.
├── backend          # FastAPI backend service
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── ...          # Source code and tests for backend
├── web              # Frontend application
│   └── ...          # Source code for the web client
├── docker-compose.yml
└── docker-compose.test.yml   # Additional Compose file for tests
```
## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request with your improvements.

## License
This project is licensed under the MIT License.
