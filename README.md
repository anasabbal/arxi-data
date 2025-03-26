# Sales Data API

This project implements a Flask-based API service designed to process and serve data related to sales, products, categories, and contacts. It includes efficient data loading strategies, caching, and custom error handling.

## Project Structure

### Core Files:
- **app.py**: Initializes the Flask application, sets up logging, registers API blueprints, and loads initial data.
- **config.py**: Stores application configuration (e.g., secret keys, debug mode, caching settings).
- **api/routes.py**: Contains the API endpoints for fetching sales data (e.g., most sold products by category, country, and top client).
- **services/data_loader.py**: Implements strategies for loading large datasets (categories, products, contacts, sales) and uses a factory pattern for flexibility.
- **services/exceptions.py**: Defines custom exceptions to handle errors during the data loading process.
- **utils/data_utils.py**: Contains utility functions for data processing:

## Features

- **Modular API**: Using Flask blueprints for clean and maintainable routing.
- **Data Loading**: Implements different strategies for loading large JSON datasets using the Strategy Design Pattern.
- **Caching**: Cached results for API responses to reduce redundant calculations and speed up frequent requests.
- **Error Handling**: Custom exceptions for controlled error responses, ensuring proper logging and reporting.
- **Performance**: The data loader processes sales data for a specific year (2024), optimizing for large datasets with efficient algorithms.

## Technologies Used

- **Flask**: Web framework for building the API.
- **Flask-Caching**: Caching mechanism to store frequently accessed data.
- **IJason**: Lightweight JSON parser to load large datasets incrementally.
- **Logging**: Configured for both development (console) and production (log file) environments.

## Design Patterns Used

### 1. **Strategy Pattern** (Data Loading)
   - Data loading logic is separated into different classes based on the data type (e.g., `CategoryLoadStrategy`, `ProductLoadStrategy`, etc.). This allows flexibility in adding new data sources or changing the loading process without modifying existing code.
   - **Why**: This promotes the Open/Closed principle, allowing the system to be extended without modifying existing code.

### 2. **Factory Pattern** (DataLoader)
   - A `DataLoadFactory` is used to instantiate different data loaders based on the type of data (categories, products, contacts, or sales).
   - **Why**: This reduces the dependency between different components and promotes loose coupling, making the code easier to maintain and scale.

### 3. **Facade Pattern** (DataLoader)
   - A simplified interface to load all data via the `DataLoader` class. The client doesn’t need to interact directly with each specific data loader, providing a more user-friendly interface.
   - **Why**: This reduces complexity and improves readability by abstracting the data loading logic into a single entry point.

### 4. **Singleton Pattern** (DataLoader Instance)
   - A single instance of `DataLoader` is used throughout the application to ensure that data is only loaded once.
   - **Why**: This ensures that data is shared across all parts of the application and prevents redundant data loading.

## Best Practices

### 1. **Error Handling**
   - Custom exceptions (`DataLoaderException`) are used to handle errors during data loading, ensuring that the application responds with meaningful error messages.
   - **Why**: This promotes clarity and debuggability, especially in large applications where identifying the source of an error can be challenging.

### 2. **Logging**
   - The app is configured with detailed logging that includes timestamps, log levels, and function names for easy tracking and debugging.
   - **Why**: Proper logging is crucial for monitoring, debugging, and auditing the application in both development and production environments.

### 3. **Caching**
   - Routes are decorated with `@cache.cached(timeout=300)` to cache the results for 5 minutes, improving performance for frequently requested data.
   - **Why**: Caching reduces redundant computations and speeds up response times for frequently accessed data.

### 4. **Modular Codebase**
   - The project uses Flask Blueprints to modularize the API, separating different concerns into distinct files and classes.
   - **Why**: This keeps the code organized, easy to scale, and maintainable, especially as the project grows.

### 5. **Data Loading Optimization**
   - The data loader processes each file incrementally using `ijson`, which helps in efficiently loading large JSON files without consuming excessive memory.
   - **Why**: This is especially important for large datasets, as it prevents memory overloads and keeps the application responsive.

### 6. **Performance**
- Stream processing with ijson
- defaultdict for efficient aggregations
- Query-aware caching (`@cache.cached(query_string=True)`)