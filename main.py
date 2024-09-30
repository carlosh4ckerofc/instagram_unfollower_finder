import instaloader
import os

# Load credentials from acc.txt
def load_credentials():
    try:
        with open("acc.txt", "r") as f:
            username = f.readline().strip()
            password = f.readline().strip()
            return username, password
    except FileNotFoundError:
        print("Error: acc.txt file not found.")
        return None, None

# Function to login with session or create new session
def login_instaloader(loader, username, password):
    session_file = f"{username}.session"
    
    # Check if session file exists
    if os.path.exists(session_file):
        print(f"Loading session for {username}...")
        loader.load_session_from_file(username, session_file)
    else:
        print(f"Logging in as {username}...")
        try:
            loader.login(username, password)
            # Save the session to file
            loader.save_session_to_file(session_file)
            print(f"Session saved to {session_file}")
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("Two-factor authentication required.")
            two_factor_code = input("Enter the 2FA code: ")
            loader.two_factor_login(two_factor_code)
            loader.save_session_to_file(session_file)
        except instaloader.exceptions.ConnectionException as e:
            print(f"Connection error: {e}")
        except instaloader.exceptions.BadCredentialsException:
            print("Error: Bad credentials provided.")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True

# Function to find unfollowers and save their usernames and IDs
def find_unfollowers(loader, username):
    try:
        profile = instaloader.Profile.from_username(loader.context, username)

        # Fetch followers and followees
        print("Fetching followers...")
        followers = {follower.username: follower.userid for follower in profile.get_followers()}
        
        print("Fetching followees...")
        followees = {followee.username: followee.userid for followee in profile.get_followees()}

        # Find unfollowers
        unfollowers = {user: followees[user] for user in followees if user not in followers}

        # Save unfollowers (usernames and IDs) to find.txt
        with open("find.txt", "w") as f:
            for unfollower, user_id in unfollowers.items():
                f.write(f"Username: {unfollower}, User ID: {user_id}\n")

        print(f"Unfollowers saved to find.txt: {len(unfollowers)} users")
    
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: The profile {username} does not exist.")
    except instaloader.exceptions.ConnectionException as e:
        print(f"Connection error while fetching profile: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Load credentials
    username, password = load_credentials()
    
    if username and password:
        # Create an Instaloader instance
        loader = instaloader.Instaloader()

        # Log in
        if login_instaloader(loader, username, password):
            # Find unfollowers
            find_unfollowers(loader, username)
        else:
            print("Failed to log in.")
    else:
        print("Could not load Instagram credentials.")