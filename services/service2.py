from flask import Flask
app = Flask(__name__)

@app.route("/test")
def test():
    return {"service": "service2", "status": "ok"}

if __name__ == "__main__":
    app.run(port=5002)
