# LITRevu_app

This is a Django application that allows users to create tickets and reviews.

## Setup

1. Create a project folder named "project_9_django":
    ```bash
    mkdir project_9_django
    ```

2. Navigate into the folder:
    ```bash
    cd project_9_django
    ```

3. Clone the project from GitHub into this folder:
    ```bash
    git clone https://github.com/Abdelhz/da_python_p9_v2.git
    ```

4. Navigate into the cloned project's directory (replace `project_directory` with the actual directory name):
    ```bash
    cd project_directory
    ```

5. Create a virtual environment:
    ```bash
    python3 -m venv env
    ```

6. Activate the virtual environment:
    - On Windows:
        ```bash
        cd env/Scripts/
        ```
        ```bash
        source activate
        ```
        ```bash
        cd ../../
        ```
    - On Unix or MacOS:
        ```bash
        source env/bin/activate
        ```

7. Install the dependencies from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

8. Navigate to the directory where `manage.py` is located:
    ```bash
    cd da_python_p9_v2/LITRevu_app
    ```

9. Start the Django project:
    ```bash
    python manage.py runserver
    ```

## Application Structure

The application consists of a main Django project (`LITRevu_app`) and an app within that project (`my_LITRevu_app`). The `my_LITRevu_app` directory contains models, views, and forms, as well as other standard Django files like `admin.py` and `apps.py`. The `templates` directory contains HTML templates, organized by functionality. The `static` directory contains static files, such as CSS and JavaScript files.

## Models

The application includes the following models:

- `Ticket`: Represents a ticket. Each ticket has a unique title, a description, an associated user, an optional image, and a timestamp indicating when it was created.
- `Review`: Represents a review. Each review is associated with a ticket and a user, has a rating between 0 and 5, a headline, an optional body, and a timestamp indicating when it was created.
- `UserFollows`: Represents the relationship between users in terms of following. Each instance of `UserFollows` indicates that a user is following another user.
- `UserBlock`: Represents the relationship between users in terms of blocking. Each instance of `UserBlock` indicates that a user has blocked another user.

## Views

The application includes the following views:

- `view_review`: A view to display a specific review. It requires the user to be logged in.
- `add_review_to_ticket`: A view to add a review to a specific ticket. It requires the user to be logged in.
- `delete_review`: A view to delete a specific review. It requires the user to be logged in and to be the author of the review.
- `EditTicketView`: A class-based view to edit a specific ticket. It requires the user to be logged in.
- `EditReviewView`: A class-based view to edit a specific review. It requires the user to be logged in.
- `subscriptions`: A view to display the users that the current user is following and the users that the current user has blocked. It requires the user to be logged in.
- `search_user`: A view to search for users by username. It requires the user to be logged in.
- `follow_user`: A view to follow a specific user. It requires the user to be logged in.
- `unfollow_user`: A view to unfollow a specific user. It requires the user to be logged in.
- `block_user`: A view to block a specific user. It requires the user to be logged in.
- `unblock_user`: A view to unblock a specific user. It requires the user to be logged in.

Each view is associated with a URL, defined in the `urls.py` file, and a template, located in the `templates` directory.

## Forms

The application includes the following forms:

- `TicketForm`: A form for creating and editing tickets.
- `ReviewForm`: A form for creating and editing reviews.
- `LoginForm`: A form for user login.

## URLs

The application includes URLs for user registration, login, logout, and profile viewing, user actions such as following and unfollowing other users, and blocking and unblocking other users, ticket actions such as adding a ticket, viewing a ticket, editing a ticket, and deleting a ticket, review actions such as adding a review, adding a review to a ticket, viewing a review, editing a review, and deleting a review, and displaying posts, feed, subscriptions, and searching for users.

## Settings

The application's settings are defined in the `settings.py` file. The settings include configuration for the database, installed apps, middleware, templates, static files, and more.