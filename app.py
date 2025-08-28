from flask import Flask, request, render_template
from flask import jsonify
import smtplib, json, os
from email.mime.text import MIMEText

app = Flask(__name__)

try:
    SMTP_SERVER = os.environ["SMTP_SERVER"]
    PORT = int(os.environ["PORT"])
    RECEIVER_EMAIL = os.environ["RECEIVER_EMAIL"]
    PASSWORD = os.environ["SMTP_PASSWORD"]
except KeyError:
    with open("config.json") as f:
        config = json.load(f)
    SMTP_SERVER = os.environ.get("SMTP_SERVER", config.get("SMTP_SERVER"))
    PORT = int(os.environ.get("PORT", config.get("PORT", 465)))
    RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", config.get("RECEIVER_EMAIL"))
    PASSWORD = os.environ.get("SMTP_PASSWORD")


if not PASSWORD:
    raise Exception("SMTP_PASSWORD must be set as an environment variable!")

@app.route("/")
def Home():
    return render_template("form.html")


@app.route("/send", methods=["POST"])
def Send_Emails():
    try:
        form_data = request.get_json()
        if not form_data:
            return "Invalid JSON", 400
    except Exception:
        return "Failed to parse JSON", 400

    if form_data.get("Terms") != "yes":
        return jsonify({"success": False, "message": "❌ You must accept the Terms & Conditions"}), 400

    form_data.pop("Terms", None)
    form_data.pop("Remember", None)

    body = json.dumps(form_data, indent=4)
     
    msg = MIMEText(body)
    msg["Subject"] = "New Contact Form Submission"
    msg["From"] = RECEIVER_EMAIL
    msg["TO"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, PORT) as server:
            server.login(RECEIVER_EMAIL, PASSWORD)
            server.sendmail(RECEIVER_EMAIL, RECEIVER_EMAIL, msg.as_string())

            return jsonify({"success": True, "message": "✅ Form submitted successfully! Email sent."})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Failed to send email: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)










