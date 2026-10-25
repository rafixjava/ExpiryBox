# ExpiryBox

ExpiryBox is a small Django web application that helps you keep track of
things that expire (food, medicine, documents, warranties...). You can:

- register, log in, manage or delete your account
- add items with a category, **price**, dates, a reference number and a **photo**
- see which items are **expired**, **expiring soon** (within 7 days) or **OK**
- create reminders for your items and read the notifications they produce
- record whether each item was **saved** or **lost**, and how much it was worth
- see a yearly summary of the money you saved and lost

It uses only Django, HTML and plain CSS. No JavaScript is needed.

---

## 1. Requirements

| Software | Version |
|----------|---------|
| Python   | 3.10 – 3.14 (3.12 or 3.13 recommended) |
| Django   | 5.2 (installed from `requirements.txt`) |
| Pillow   | 11 or newer (needed for item photos) |
| PyCharm  | Community or Professional |

The database is **SQLite**, which comes with Python, so nothing extra has to be installed.

---

## 2. Open the project in PyCharm

1. Unzip the project (for example to `C:\Users\<you>\Downloads\ExpiryBox2`).
2. Start PyCharm and choose **File → Open...**.
3. Select the `ExpiryBox2` folder (the one that contains `manage.py`) and click **OK**.

## 3. Create a virtual environment

1. Go to **File → Settings → Project: ExpiryBox2 → Python Interpreter**.
2. Click **Add Interpreter → Add Local Interpreter...**.
3. Choose **Virtualenv Environment → New**, location `ExpiryBox2\.venv`, and pick your Python 3 installation.
4. Click **OK**. PyCharm's terminal now uses this environment automatically.

Alternatively, in a Windows terminal (Command Prompt or PowerShell) inside the project folder:

```bat
python -m venv .venv
.venv\Scripts\activate
```

## 4. Install the required packages

Open PyCharm's **Terminal** tab (bottom of the window) and run:

```bat
pip install -r requirements.txt
```

## 5. Set up the database

The database settings are already in `config/settings.py`: SQLite stores
everything in a file named `db.sqlite3` in the project folder. That file is
created automatically by the next command.

```bat
python manage.py makemigrations
python manage.py migrate
```

- `makemigrations` creates migration files when a model changes. The project already
  includes them, so it should print `No changes detected`.
- `migrate` creates the tables in `db.sqlite3`. It also adds 10 starting categories
  (Groceries, Medicine, Bakery...).

## 6. Create an admin user (optional)

```bat
python manage.py createsuperuser
```

Enter a username, email and password when asked.

## 7. Run the server

```bat
python manage.py runserver
```

Or, in PyCharm, choose the **runserver** run configuration (top-right) and press ▶.
It is in the `.run/` folder. If PyCharm asks for an interpreter, choose `.venv`.

## 8. Open the application

Go to **http://127.0.0.1:8000/** in your browser.

## 9. Try the features

1. Click **Register** and create a normal user account.
2. **Categories**: the 10 starting categories are *Predefined* and cannot be edited or
   deleted. Add your own category; you can edit or delete that one.
3. **Items → + Add item**: add a few items with a price and a photo. Give one an expiry date in
   the past, one within 7 days and one far in the future. The labels show
   *Expired*, *Expiring soon* and *OK*.
4. Open an item and click **+ Add reminder**. Choose today's date.
5. Open the **Dashboard** or **Notifications**. The due reminder has become a
   notification and the reminder now shows *Sent*. Mark it as read or delete it.
6. Open an item and click **Record outcome**. Choose *Saved* or *Lost*. The amount is
   taken from the item's price automatically.
7. **Impact → Yearly summary** shows the total saved and lost per year.
8. **Account → Delete my account** asks for your password, then deletes the account
   and all of its data.
9. Register a second user in a private/incognito window. That user cannot see the
   first user's items, and changing the ID in the URL (for example `/items/1/`)
   shows "Page not found".

## 10. Django admin site

Go to **http://127.0.0.1:8000/admin/** and log in with the superuser from step 6.
You can view and edit every table there.

## 11. Run the automatic tests

```bat
python manage.py check
python manage.py test
```

---

## Project structure

```
ExpiryBox2/
├── manage.py
├── requirements.txt
├── README.md
├── config/                 Django project settings
│   ├── settings.py
│   ├── urls.py             main URL list (includes each app's urls.py)
│   ├── asgi.py
│   └── wsgi.py
├── accounts/               App 1: register, login, logout, account page
├── items/                  App 2: items, categories and the dashboard
├── notifications/          App 3: reminders and notifications
├── impact/                 App 4: impact records and yearly summary
├── templates/
│   ├── base.html           shared layout (navigation bar and messages)
│   ├── accounts/  items/  notifications/  impact/
├── static/css/style.css    the only stylesheet (brand colours from the logo)
├── static/img/logo.svg     the ExpiryBox logo
└── media/                  uploaded item photos (created automatically)
```

Each app has the usual Django files: `models.py` (database tables), `forms.py`
(ModelForms), `views.py` (function-based views), `urls.py`, `admin.py` and `tests.py`.

## How the class diagram maps to the code

| Diagram | Django model | Notes |
|---------|--------------|-------|
| USER (name, email, password, createdAt) | Django's built-in `User` | name → `first_name`, createdAt → `date_joined`. Passwords are hashed by Django. |
| ITEM | `items.Item` | All diagram fields, plus `price` and an optional `photo`. |
| CATEGORY | `items.Category` | Shared by all users (the diagram gives it no `user`). Extra field `is_predefined`: the 10 starting categories cannot be edited or deleted. |
| REMINDER | `notifications.Reminder` | |
| NOTIFICATION | `notifications.Notification` | `item` is optional. |
| OUTCOMESTATUS (SAVED, LOST) | `impact.OutcomeStatus` | Django `TextChoices`, used by `ImpactRecord.outcome`. |
| IMPACTRECORD | `impact.ImpactRecord` | `amount_value` is copied from the item's price. `notes` is a **text** field (the diagram shows bool). |
| IMPACTSUMMARY (user, year) | `impact.ImpactSummary` | Totals are calculated from the records, not stored. |

Relationships (all `ForeignKey`):

- A **user** owns many **items**. Deleting a user deletes their items.
- A **category** has many **items**. A category that is still in use cannot be deleted.
- An **item** has many **reminders**, **notifications** and **impact records**.
  Deleting an item deletes them too.
- A **notification** and an **impact summary** belong to a **user**.

## How reminders and notifications work

- A **reminder** is a saved date for an item. Its `is_sent` value starts as `False`.
- There is **no background job**. When you open the **Dashboard** or **Notifications**
  page, the function `create_due_notifications()` in `notifications/views.py` looks
  for your reminders whose date is today or earlier and whose `is_sent` is still `False`.
- For each one it creates a **notification** and sets `is_sent = True`. So every
  reminder produces exactly one notification, no matter how often you reload the page.
- Editing a reminder sets `is_sent` back to `False`, so it can fire again on its new date.
- Notifications are shown inside the app only. No emails or SMS are sent.

## Expiry status rule

`Item.expiry_status()` in `items/models.py`:

- **Expired**: the expiry date is before today.
- **Expiring soon**: it expires today or within the next 7 days (`EXPIRING_SOON_DAYS = 7`).
- **OK**: it expires later than that.

## Security

- Every private page uses `@login_required`.
- Every query filters by the logged-in user, for example
  `get_object_or_404(Item, pk=pk, user=request.user)`, so another user's records
  give a 404 page.
- The item drop-downs in the reminder and impact forms only list your own items.
- All POST forms include `{% csrf_token %}`.
- The `SECRET_KEY` and `DEBUG = True` in `settings.py` are for local development only.
