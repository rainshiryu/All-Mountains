# Login.py
from flask import Flask, request, session, redirect, url_for, render_template_string
from Mountain_Information import mountain_search

app = Flask(__name__)
app.secret_key = "all-mountains-secret-key"

# Register the Mountain Information blueprint
app.register_blueprint(mountain_search)

# In-memory user database
user_database = {}

LOGIN_PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>All Mountains | Log In</title>
  <style>
    :root {
      --pine-dark: #163028;
      --pine-primary: #2c5e4f;
      --pine-light: #e7f0ed;
      --sunset-accent: #d97724;
      --sunset-hover: #b86119;
      --snow-bg: #f3f6f5;
      --card-bg: #ffffff;
      --text-main: #1d2b27;
      --text-muted: #5a6e67;
      --border-subtle: #d5e0dc;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #163028 0%, #2c5e4f 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      padding: 20px;
    }
    .auth-card {
      background: var(--card-bg);
      border-top: 6px solid var(--sunset-accent);
      border-radius: 14px;
      padding: 36px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 16px 32px rgba(10, 25, 20, 0.3);
    }
    .auth-card h2 {
      margin: 0 0 8px;
      color: var(--pine-dark);
      font-size: 1.6rem;
    }
    .auth-card p {
      margin: 0 0 24px;
      color: var(--text-muted);
      font-size: 0.95rem;
    }
    .form-group {
      margin-bottom: 18px;
    }
    .form-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    .form-group input {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      font-size: 1rem;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .form-group input:focus {
      border-color: var(--pine-primary);
    }
    .btn-submit {
      width: 100%;
      background: var(--sunset-accent);
      color: #ffffff;
      border: none;
      padding: 13px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s ease;
      margin-top: 8px;
    }
    .btn-submit:hover {
      background: var(--sunset-hover);
    }
    .error-msg {
      background: #fdecea;
      border-left: 4px solid #d93025;
      color: #9b1c1c;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.9rem;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="auth-card">
    <h2>🏔️ All Mountains</h2>
    <p>Sign in to access mountain directories and live conditions.</p>
    
    {% if error %}
      <div class="error-msg">{{ error }}</div>
    {% endif %}

    <form method="post">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" required autocomplete="username">
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required autocomplete="current-password">
      </div>
      <button type="submit" class="btn-submit">Log In</button>
    </form>
  </div>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username and password:
            if username not in user_database:
                user_database[username] = {"password": password, "profile": {}}
            
            if user_database[username]["password"] == password:
                session['user_id'] = username
                return redirect(url_for('mountain_search.search'))
            else:
                error = "Incorrect password. Please try again."
        else:
            error = "Please enter both a username and password."

    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)