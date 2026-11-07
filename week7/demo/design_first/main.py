import connexion

app = connexion.FlaskApp(__name__, specification_dir=".")
app.add_api("openapi.yaml", validate_responses=True)

if __name__ == "__main__":
    # Swagger UI: http://localhost:5001/api/v1/ui/
    app.run("main:app", host="127.0.0.1", port=5001)
