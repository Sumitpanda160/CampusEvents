
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

import mysql.connector

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set.")


@app.route("/")
def home():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            events.*,
            COUNT(registrations.id) AS registered_count,
            MAX(
                CASE
                    WHEN registrations.user_id = %s
                    THEN 1
                    ELSE 0
                END
            ) AS user_registered
        FROM events
        LEFT JOIN registrations
            ON events.id = registrations.event_id
            AND registrations.status = 'registered'
        GROUP BY events.id
        ORDER BY events.event_date ASC
    """, (session.get("user_id", 0),))

    events = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", events=events)


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )

            connection.commit()

            flash("Account created successfully! Please login.")
            return redirect(url_for("login"))

        except Exception as error:
            connection.rollback()
            print("Signup Error:", error)
            flash("Email already registered or invalid details.")

        finally:
            cursor.close()
            connection.close()

    return render_template("signup.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


# EVENT REGISTRATION AND RE-REGISTRATION
@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register_event(event_id):

    if "user_id" not in session:
        flash("Please login first to register for an event.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        cursor.execute(
            "SELECT * FROM events WHERE id = %s FOR UPDATE",
            (event_id,)
        )

        event = cursor.fetchone()

        if not event:
            connection.rollback()
            flash("Event not found.")
            return redirect(url_for("home"))

        cursor.execute(
            """
            SELECT id, status FROM registrations
            WHERE user_id = %s AND event_id = %s
            """,
            (session["user_id"], event_id)
        )

        existing_registration = cursor.fetchone()

        if existing_registration and existing_registration["status"] == "registered":

            connection.rollback()
            flash("You have already registered for this event.")
            return redirect(url_for("home"))

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM registrations
            WHERE event_id = %s AND status = 'registered'
            """,
            (event_id,)
        )

        registration_count = cursor.fetchone()["total"]

        if registration_count >= event["capacity"]:

            connection.rollback()
            flash("Sorry, this event is full.")
            return redirect(url_for("home"))

        if existing_registration and existing_registration["status"] == "cancelled":

            cursor.execute(
                """
                UPDATE registrations
                SET status = 'registered'
                WHERE id = %s
                """,
                (existing_registration["id"],)
            )

            flash("Successfully registered again for " + event["title"] + "!")

        else:

            cursor.execute(
                """
                INSERT INTO registrations (user_id, event_id)
                VALUES (%s, %s)
                """,
                (session["user_id"], event_id)
            )

            flash("Successfully registered for " + event["title"] + "!")

        connection.commit()

    except mysql.connector.Error as error:

        connection.rollback()
        print("Registration Error:", error)
        flash("Registration failed. Please try again.")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


# MY REGISTRATIONS PAGE
@app.route("/my-registrations")
def my_registrations():

    if "user_id" not in session:
        flash("Please login to view your registrations.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                registrations.id,
                registrations.registered_at,
                registrations.status,
                events.title,
                events.category,
                events.event_date,
                events.event_time,
                events.venue
            FROM registrations
            JOIN events
                ON registrations.event_id = events.id
            WHERE registrations.user_id = %s
            ORDER BY registrations.registered_at DESC
            """,
            (session["user_id"],)
        )

        registrations = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "my_registrations.html",
        registrations=registrations
    )


# CANCEL EVENT REGISTRATION
@app.route("/cancel-registration/<int:registration_id>", methods=["POST"])
def cancel_registration(registration_id):

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE registrations
            SET status = 'cancelled'
            WHERE id = %s
            AND user_id = %s
            AND status = 'registered'
            """,
            (registration_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount > 0:
            flash("Registration cancelled successfully!")
        else:
            flash("Registration not found or already cancelled.")

    except mysql.connector.Error as error:

        connection.rollback()
        print("Cancellation Error:", error)
        flash("Unable to cancel registration. Please try again.")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("my_registrations"))


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
