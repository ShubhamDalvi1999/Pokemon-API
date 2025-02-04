# Pokemon API

A Flask-based REST API that serves as a wrapper for the PokéAPI, providing both REST and GraphQL endpoints for accessing Pokemon data.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/pokemon-api.git
cd pokemon-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Then edit `.env` with your actual configuration values.

## Credentials Setup

### Google Cloud (BigQuery)
1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the BigQuery API
4. Create a service account and download the JSON key file
5. Save the JSON key file in a secure location (NOT in the repository)
6. Update your `.env` file with the path to the credentials file:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

### Database Setup
1. Set up your PostgreSQL database
2. Set up your MongoDB instance
3. Update the connection strings in your `.env` file

## Running the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

## API Documentation

### REST Endpoints

1. Get Pokemon Details
```
GET /pokemon/<name>
Example: /pokemon/pikachu
```

2. List All Pokemon
```
GET /pokemon/list
```

3. Get Pokemon by Type
```
GET /pokemon/type/<type_name>
Example: /pokemon/type/fire
```

4. Get Pokemon Abilities
```
GET /pokemon/<name>/abilities
Example: /pokemon/charizard/abilities
```

5. Get Evolution Chain
```
GET /pokemon/species/<name>/evolution
Example: /pokemon/species/bulbasaur/evolution
```

6. Get Pokemon Moves
```
GET /pokemon/<name>/moves
Example: /pokemon/squirtle/moves
```

7. Get Pokemon Habitat
```
GET /pokemon/species/<name>/habitat
Example: /pokemon/species/psyduck/habitat
```

8. Get Pokemon Encounters
```
GET /pokemon/<name>/encounters
Example: /pokemon/jigglypuff/encounters
```

### GraphQL Endpoints

1. Get First 10 Pokemon
```
GET /graphql/pokemon/first10
```

2. Get First 5 Pokemon with Types
```
GET /graphql/pokemon/first5types
```

## Security Notes

- Never commit sensitive credentials to the repository
- Keep your `.env` file and credential files secure
- Use environment variables for all sensitive configuration
- Regularly rotate your credentials

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Ensure no sensitive data is included in your commits
4. Submit a pull request

## Error Handling

All endpoints include proper error handling and will return appropriate HTTP status codes and error messages when:
- The requested Pokemon/resource doesn't exist
- The PokeAPI is unavailable
- Invalid parameters are provided
- Database connections fail

## Rate Limiting

Please note that this API wrapper is subject to the same rate limiting as the original PokeAPI. Be mindful of your request frequency to avoid being rate-limited. 