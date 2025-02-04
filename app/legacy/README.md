# Legacy Pokemon API Code

This directory contains the original version of the Pokemon API application before it was restructured following best practices. The code is kept for reference and historical purposes.

## File Structure

```
legacy/
├── app.py                    # Original monolithic Flask application
├── db_repositories.py        # Original database repository implementations
├── models.py                # Original database models
├── graphql_routes.py        # Original GraphQL route handlers
├── templates/              
│   └── index.html          # Original frontend template
└── sql/
    └── create_azure_table.sql  # Original Azure SQL table creation script
```

## Key Differences from New Version

1. **Monolithic Structure**: All routes and logic were in a single file
2. **Limited Error Handling**: Basic error handling without proper custom exceptions
3. **No Service Layer**: Direct API calls without a service abstraction
4. **Basic Configuration**: Simple environment variable loading without proper config classes
5. **Limited Type Hints**: Minimal use of Python type hints
6. **No Test Structure**: Lack of organized test infrastructure

## Migration Notes

The code has been restructured into the new version with:
- Proper separation of concerns
- Service layer pattern
- Repository pattern
- Better error handling
- Type hints
- Proper configuration management
- Test infrastructure

Please refer to the main project README for the new structure and best practices. 