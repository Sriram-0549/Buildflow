from flask import Flask

app = Flask(__name__)

@app.route("/")

def home():
	return "Buildflow API is running"
	
@app.route("/health")
def health():
	return "healthy"

@app.route("/version")
def version():
	return "version 3.0"
