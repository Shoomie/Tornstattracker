import requests
import sqlite3
import time
import os # <--- Make sure os is imported
from datetime import datetime, timezone
import platform # <--- Import platform module

# --- Configuration ---
DATABASE_FILE = "faction_data.db"  # Single DB for everything
API_BASE_URL = "https://api.torn.com/user/"
RATE_LIMIT_DELAY = 0.7
USER_AGENT = "PythonMenuCrimeTracker/1.1 (FactionOfficerTool)" # Version bump

# --- Clear Screen Function ---
def clear_screen():
    """Clears the terminal screen."""
    # Check the operating system
    system_name = platform.system()
    if system_name == "Windows":
        os.system('cls')
    else: # Assume Linux or macOS
        os.system('clear')

# --- Database Functions ---

def db_connect():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"\n!!! Database connection error: {e}")
        print("!!! Please ensure the script has permission to read/write in this directory.")
        exit(1)

def setup_database():
    """Creates the necessary table if it doesn't exist."""
    if not os.path.exists(DATABASE_FILE):
        print(f"Database file '{DATABASE_FILE}' not found, creating...")
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                api_key TEXT NOT NULL,
                name TEXT,
                last_crime_count INTEGER,
                last_update_timestamp TEXT,
                previous_crime_count INTEGER,
                previous_update_timestamp TEXT
            )
        """)
        conn.commit()
        print(f"Database '{DATABASE_FILE}' is ready.")
    except sqlite3.Error as e:
        print(f"\n!!! Database setup error: {e}")
    finally:
        if conn:
            conn.close()

def _add_or_update_member_db(user_id, api_key, name=None):
    """Internal function to add/update a member in the DB."""
    conn = db_connect()
    cursor = conn.cursor()
    success = False
    try:
        cursor.execute("SELECT user_id FROM members WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                UPDATE members
                SET api_key = ?, name = ?
                WHERE user_id = ?
            """, (api_key, name, user_id))
            print(f"\n--- Member {user_id} ('{name or 'N/A'}') updated successfully. ---")
        else:
            cursor.execute("""
                INSERT INTO members
                (user_id, api_key, name, last_crime_count, last_update_timestamp, previous_crime_count, previous_update_timestamp)
                VALUES (?, ?, ?, NULL, NULL, NULL, NULL)
            """, (user_id, api_key, name))
            print(f"\n--- Member {user_id} ('{name or 'N/A'}') added successfully. ---")
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
         print(f"\n!!! Error: Member with User ID {user_id} might already exist (unexpected issue).")
    except sqlite3.Error as e:
        print(f"\n!!! Database error adding/updating member {user_id}: {e}")
    finally:
        if conn:
            conn.close()
    return success # Indicate success/failure

def _remove_member_db(user_id):
    """Internal function to remove a member from the DB."""
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM members WHERE user_id = ?", (user_id,))
        changes = conn.total_changes # Use built-in counter
        conn.commit()
        return changes > 0 # Return True if a row was deleted
    except sqlite3.Error as e:
        print(f"\n!!! Database error removing member {user_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Torn API Function ---
# (get_crime_count remains the same as before)
def get_crime_count(user_id, api_key):
    """Fetches the total crime count for a user from the Torn API."""
    url = f"{API_BASE_URL}{user_id}?selections=crimes&key={api_key}"
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            error_info = data['error']
            return None, f"API Error Code {error_info.get('code', 'N/A')}: {error_info.get('error', 'Unknown API error')}"
        criminal_record = data.get('criminalrecord')
        if criminal_record and 'total' in criminal_record:
            return criminal_record['total'], None
        else:
            return None, "Could not find 'criminalrecord' or 'total' field in API response."
    except requests.exceptions.Timeout:
        return None, "Request timed out."
    except requests.exceptions.RequestException as e:
        return None, f"HTTP Request failed: {e}"
    except json.JSONDecodeError:
        return None, "Failed to parse JSON response from API."
    except Exception as e:
        return None, f"An unexpected error occurred during API call: {e}"


# --- Core Logic / Menu Actions ---

def add_member_interactive():
    """Handles the interactive process of adding/updating a member via main menu."""
    print("\n--- Add/Update Faction Member ---")
    while True:
        try:
            user_id_str = input("Enter Torn User ID (or press Enter to cancel): ").strip()
            if not user_id_str: return # Allow returning to menu
            user_id = int(user_id_str)
            break
        except ValueError:
            print("!!! Invalid input. User ID must be a number.")

    # Fetch current details if user exists, helps with placeholder text
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, name FROM members WHERE user_id = ?", (user_id,))
    current_member = cursor.fetchone()
    conn.close()

    current_api_key = current_member['api_key'] if current_member else ""
    current_name = current_member['name'] if current_member else ""
    action_verb = "Update" if current_member else "Add"

    print(f"\n--- {action_verb} details for User ID: {user_id} ---")
    if current_member:
        print(f"Current Name: {current_name or '(Not set)'}")
        print(f"Current API Key: {current_api_key}")
        print("(Press Enter to keep current values)")

    while True:
        api_key_prompt = f"Enter API Key [{current_api_key}]: " if current_member else "Enter API Key: "
        api_key = input(api_key_prompt).strip()
        if not api_key and current_member: # Keep current if updating and input is empty
            api_key = current_api_key
            break
        elif api_key: # Use new key if provided
            break
        elif not current_member: # Require key if adding new
             print("!!! API Key cannot be empty when adding a new member.")

    name_prompt = f"Enter Member's Name [{current_name or '(Not set)'}]: " if current_member else "Enter Member's Name (optional): "
    name = input(name_prompt).strip()
    if not name and current_member: # Keep current if updating and input is empty
        name = current_name
    name = name or None # Store None if empty/not set

    print("\n--- Review Details ---")
    print(f"  User ID: {user_id}")
    print(f"  API Key: {api_key}")
    print(f"  Name:    {name or '(Not set)'}")

    confirm = input(f"Confirm {action_verb.lower()}ing this member? (yes/no): ").strip().lower()
    if confirm == 'yes':
        _add_or_update_member_db(user_id, api_key, name)
    else:
        print("\n--- Operation cancelled. ---")

def edit_member_interactive(user_id):
    """Handles editing an existing member, called after listing."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, name FROM members WHERE user_id = ?", (user_id,))
    current_member = cursor.fetchone()
    conn.close()

    if not current_member:
        print(f"!!! Error: Member with ID {user_id} not found (should not happen here).")
        return

    current_api_key = current_member['api_key']
    current_name = current_member['name']

    print(f"\n--- Editing Member ID: {user_id} ---")
    print(f"Current Name: {current_name or '(Not set)'}")
    print(f"Current API Key: {current_api_key}")
    print("(Press Enter to keep current values)")

    while True:
        api_key = input(f"Enter NEW API Key [{current_api_key}]: ").strip()
        if not api_key: # Keep current if empty
            api_key = current_api_key
            break
        else: # Use new key if provided
            break

    name = input(f"Enter NEW Name [{current_name or '(Not set)'}]: ").strip()
    if not name: # Keep current if empty
        name = current_name
    name = name or None # Store None if empty/not set

    # Only proceed if something actually changed
    if api_key == current_api_key and name == current_name:
        print("\n--- No changes detected. Operation cancelled. ---")
        return

    print("\n--- Review Changes ---")
    print(f"  User ID: {user_id}")
    print(f"  API Key: {api_key}")
    print(f"  Name:    {name or '(Not set)'}")

    confirm = input("Confirm saving these changes? (yes/no): ").strip().lower()
    if confirm == 'yes':
        _add_or_update_member_db(user_id, api_key, name) # Use the same update function
    else:
        print("\n--- Operation cancelled. ---")


def _confirm_and_remove_member(user_id):
    """Handles confirmation and removal logic, usable from multiple places."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM members WHERE user_id = ?", (user_id,))
    member_row = cursor.fetchone()
    conn.close()

    if member_row:
        member_name = member_row['name'] or 'N/A'
        print(f"\nSelected member: {member_name} (ID: {user_id})")
        confirm = input("Are you sure you want to permanently remove this member and their stats? (yes/no): ").strip().lower()
        if confirm == 'yes':
            if _remove_member_db(user_id):
                print(f"\n--- Member {user_id} removed successfully. ---")
            else:
                # Error message handled in _remove_member_db
                 print(f"\n--- Failed to remove member {user_id}. ---")
        else:
            print("\n--- Removal cancelled. ---")
        return True # Indicated an action was attempted (or cancelled)
    else:
        print(f"\n--- Member with User ID {user_id} not found in the database. ---")
        return False # Indicate member not found


def remove_member_interactive():
    """Handles the interactive process of removing a member via main menu."""
    print("\n--- Remove Faction Member ---")
    while True:
        try:
            user_id_str = input("Enter Torn User ID of member to remove (or press Enter to cancel): ").strip()
            if not user_id_str: return # Allow returning to menu
            user_id = int(user_id_str)
            break
        except ValueError:
            print("!!! Invalid input. User ID must be a number.")
    # Call the shared confirmation and removal logic
    _confirm_and_remove_member(user_id)


def list_members():
    """Lists members and provides options to edit/delete."""
    print("\n--- Current Faction Members ---")
    conn = db_connect()
    cursor = conn.cursor()
    members_list = [] # Store fetched members for later lookup
    try:
        cursor.execute("SELECT user_id, name, last_update_timestamp FROM members ORDER BY name COLLATE NOCASE")
        members = cursor.fetchall()
        members_list = [dict(m) for m in members] # Convert to list of dicts

    except sqlite3.Error as e:
        print(f"\n!!! Database error listing members: {e}")
        if conn: conn.close()
        return # Can't proceed if fetch failed
    finally:
        if conn: conn.close()


    if not members_list:
        print("No members found in the database. Use 'Add Member' to add some.")
        return

    print(f"{'User ID':<10} {'Name':<25} {'Last Stat Update (UTC)'}")
    print("-" * 60)
    member_ids = set() # Keep track of listed IDs for validation
    for member in members_list:
        user_id = member['user_id']
        member_ids.add(user_id)
        name = member['name'] or '(No Name Set)'
        last_update = member['last_update_timestamp'] or 'Never'
        if last_update != 'Never':
            try:
                dt_obj = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                last_update = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError: pass # Keep original string if parsing fails
        print(f"{user_id:<10} {name:<25} {last_update}")
    print("-" * 60)

    # --- Post-Listing Actions ---
    while True:
        action = input("Enter User ID to Edit/Delete, or press Enter to return to menu: ").strip()
        if not action:
            break # Return to main menu

        try:
            target_user_id = int(action)
            if target_user_id not in member_ids:
                print(f"!!! Invalid User ID {target_user_id}. Please enter an ID from the list above.")
                continue

            # Valid ID entered, ask what to do
            sub_choice = input(f"Manage User {target_user_id}: (E)dit details, (D)elete member, or (C)ancel? ").strip().lower()

            if sub_choice == 'e':
                edit_member_interactive(target_user_id)
                break # Assume done after edit attempt, return to main menu
            elif sub_choice == 'd':
                _confirm_and_remove_member(target_user_id) # Use shared removal logic
                break # Assume done after delete attempt, return to main menu
            elif sub_choice == 'c':
                 print("--- Action cancelled. ---")
                 continue # Go back to asking for another ID or Enter
            else:
                print("!!! Invalid choice. Please enter E, D, or C.")

        except ValueError:
            print("!!! Invalid input. Please enter a numeric User ID or press Enter.")


# (update_all_stats remains the same as before)
def update_all_stats():
    """Fetches current crime stats for all members and updates the database."""
    print("\n--- Update Crime Stats for All Members ---")
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, api_key, name, last_crime_count, last_update_timestamp FROM members")
        members_to_update = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"\n!!! Error fetching members from database: {e}")
        if conn: conn.close()
        return
    if not members_to_update:
        print("No members found in the database to update.")
        if conn: conn.close()
        return

    total_members = len(members_to_update)
    print(f"Starting update for {total_members} members...")
    success_count = 0
    fail_count = 0
    updates_to_commit = []
    conn.close() # Close connection before long loop

    for i, member_data in enumerate(members_to_update):
        member = dict(member_data) # Work with dict copy
        user_id = member['user_id']
        api_key = member['api_key']
        member_name = member['name'] or f"User {user_id}"
        current_last_count = member['last_crime_count']
        current_last_timestamp = member['last_update_timestamp']

        print(f"({i+1}/{total_members}) Fetching for {member_name} (ID: {user_id})... ", end="")
        new_crime_count, error = get_crime_count(user_id, api_key)

        if error:
            print(f"Failed! Error: {error}")
            fail_count += 1
        elif new_crime_count is not None:
            print(f"Success! Crimes: {new_crime_count}")
            success_count += 1
            now_timestamp_iso = datetime.now(timezone.utc).isoformat()
            updates_to_commit.append({
                'user_id': user_id,
                'last_crime_count': new_crime_count,
                'last_update_timestamp': now_timestamp_iso,
                'previous_crime_count': current_last_count,
                'previous_update_timestamp': current_last_timestamp
            })
        else:
             print(f"Failed! Unknown error fetching crimes.")
             fail_count += 1
        if i < total_members - 1:
            time.sleep(RATE_LIMIT_DELAY)

    # --- Commit all successful updates ---
    if updates_to_commit:
        print("\nCommitting updates to database...")
        conn_commit = db_connect()
        cursor_commit = conn_commit.cursor()
        try:
            for update_data in updates_to_commit:
                cursor_commit.execute("""
                    UPDATE members SET last_crime_count = ?, last_update_timestamp = ?,
                                        previous_crime_count = ?, previous_update_timestamp = ?
                    WHERE user_id = ? """, (
                    update_data['last_crime_count'], update_data['last_update_timestamp'],
                    update_data['previous_crime_count'], update_data['previous_update_timestamp'],
                    update_data['user_id']
                ))
            conn_commit.commit()
            print("Updates committed successfully.")
        except sqlite3.Error as e:
            print(f"\n!!! Database error during commit: {e}")
            conn_commit.rollback()
        finally:
            if conn_commit: conn_commit.close()
    else:
        print("\nNo successful API updates to commit.")

    print(f"\n--- Update finished. Success: {success_count}, Failed: {fail_count} ---")


# (show_results remains the same as before)
def show_results():
    """Calculates and displays the crime difference between the last two updates."""
    print("\n--- Crime Stats Results (Since Last Update) ---")
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id, name, last_crime_count, previous_crime_count,
                   last_update_timestamp, previous_update_timestamp
            FROM members
            WHERE last_crime_count IS NOT NULL AND previous_crime_count IS NOT NULL """)
        results_data = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"\n!!! Error fetching results from database: {e}")
        if conn: conn.close()
        return
    finally:
        if conn: conn.close()

    if not results_data:
        print("\nNo members found with two consecutive valid crime counts.")
        print("Please run 'Update All Stats' at least twice to see results.")
        return

    calculated_diffs = []
    skipped_members = []
    for row_data in results_data:
        row = dict(row_data)
        if row['last_crime_count'] >= row['previous_crime_count']:
            diff = row['last_crime_count'] - row['previous_crime_count']
            calculated_diffs.append({
                'user_id': row['user_id'], 'name': row['name'] or f"User {row['user_id']}",
                'crimes_done': diff, 'start_time': row['previous_update_timestamp'],
                'end_time': row['last_update_timestamp']
            })
        else:
            skipped_members.append({
                'user_id': row['user_id'], 'name': row['name'] or f"User {row['user_id']}",
                'reason': f"End count ({row['last_crime_count']}) < Start count ({row['previous_crime_count']})"
            })
    if not calculated_diffs:
        print("\nNo valid differences could be calculated.")
        return

    calculated_diffs.sort(key=lambda x: x['crimes_done'], reverse=True)
    try:
        overall_start = min(datetime.fromisoformat(r['start_time'].replace('Z', '+00:00')) for r in calculated_diffs if r['start_time']) if calculated_diffs else None
        overall_end = max(datetime.fromisoformat(r['end_time'].replace('Z', '+00:00')) for r in calculated_diffs if r['end_time']) if calculated_diffs else None
        period_str = f"Period approx: {overall_start.strftime('%Y-%m-%d %H:%M') if overall_start else '?'} to {overall_end.strftime('%Y-%m-%d %H:%M') if overall_end else '?'} UTC"
    except Exception: period_str = "Period times unavailable."

    print(f"\n{period_str}")
    print("-" * 65)
    print(f"{'Rank':<5} {'User ID':<10} {'Name':<25} {'Crimes Done':<12} {'Period'}")
    print("-" * 65)
    for i, result in enumerate(calculated_diffs):
        start_short = datetime.fromisoformat(result['start_time'].replace('Z', '+00:00')).strftime('%m/%d %H:%M') if result['start_time'] else '?'
        end_short = datetime.fromisoformat(result['end_time'].replace('Z', '+00:00')).strftime('%m/%d %H:%M') if result['end_time'] else '?'
        period_user = f"{start_short}-{end_short}"
        print(f"{i+1:<5} {result['user_id']:<10} {result['name']:<25} {result['crimes_done']:<12} {period_user}")
    print("-" * 65)
    if skipped_members:
        print("\nNote: Some members were skipped in results calculation:")
        for skipped in skipped_members: print(f"- {skipped['name']} (ID: {skipped['user_id']}): {skipped['reason']}")


# --- Menu System ---

def display_main_menu():
    """Prints the main menu options."""
    # Displaying the menu remains the same
    print("\n===== Torn Faction Crime Tracker Menu =====")
    print(" 1. Add / Update Member")
    print(" 2. Remove Member")
    print(" 3. List All Members (and Edit/Delete)")
    print(" 4. Update All Member Stats (Fetch from API)")
    print(" 5. Show Crime Results (Since Last Update)")
    print(" 0. Exit")
    print("==========================================")

def main_loop():
    """Runs the main interactive menu loop."""
    while True:
        clear_screen() # <--- ADD THIS LINE to clear before showing menu
        display_main_menu()
        choice = input("Enter your choice (0-5): ").strip()

        # --- Execute chosen action ---
        if choice == '1':
            add_member_interactive()
        elif choice == '2':
            remove_member_interactive()
        elif choice == '3':
            list_members()
        elif choice == '4':
            update_all_stats()
        elif choice == '5':
            show_results()
        elif choice == '0':
            print("\nExiting program. Goodbye!")
            break
        else:
            # No action taken, just show error message
            print("\n!!! Invalid choice. Please enter a number between 0 and 5. !!!")
            # Optional short pause after invalid choice before clearing again
            # time.sleep(1.5)
            # Continue directly to clear screen and show menu again
            continue # Go directly to the next loop iteration

        # --- Pause after a valid action (except exit) ---
        if choice != '0':
             # This input will happen *after* the action function prints its output
             input("\nPress Enter to return to the menu...")
             # The loop will then restart, clear the screen, and show the menu


# --- Main Execution ---

if __name__ == "__main__":
    print("Starting Faction Crime Tracker...")
    setup_database()
    main_loop()