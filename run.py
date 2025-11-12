from app.main import app

if __name__ == '__main__':
    # This file is used to run the Flask app with gunicorn
    # It's also used as the entry point for the Docker container
    import os
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
